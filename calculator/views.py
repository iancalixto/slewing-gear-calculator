import json
import os
import tempfile
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from .forms import DrivetrainForm, SaveCalculationForm, DatasheetUploadForm, MotorSpecsForm
from .engine import drivetrain_sizing
from .models import MotorCalculation
from .pdf_parser import parse_datasheet, check_compliance, specs_to_form_initial

# Raw strings so backslashes reach KaTeX unchanged.
FORMULAS = {
    'f1':  r'M_{2,\max} = \dfrac{M_{\max}}{i_{\text{worm}} \cdot \eta}',
    'f2':  r'M_{2,\text{nom}} = \dfrac{M_{\text{nom}}}{i_{\text{worm}} \cdot \eta}',
    'f3':  r'M_{\text{gear,req}} = M_{2,\text{nom}} \times S_f \qquad S_f = 1.34',
    'f4':  r'i_{\text{bevel}} = \dfrac{n_{\text{motor}}}{n_{\text{gear,out}}}',
    'f5':  r'n_{\text{slew}} = \dfrac{n_{\text{gear,out}}}{i_{\text{worm}}}',
    'f6':  r'M_{\text{motor,req}} = \dfrac{M_{2,\max}}{i_{\text{bevel}}}',
    'f7':  r'M_{\text{start}} = M_n \cdot k_{\text{start}}, \qquad k_{\text{start}} = \dfrac{M_a}{M_n}',
    'f8':  r'\text{margin} = \dfrac{M_{\text{start}}}{M_{\text{motor,req}}}',
    'f8c': (
        r'\begin{cases}'
        r'M_{\text{start}} > M_{\text{motor,req}} & \Rightarrow \textbf{OK} \\'
        r'M_{\text{motor,req}} \leq M_{\text{start}} + 2\,\text{Nm} & \Rightarrow \textbf{On\;the\;limit} \\'
        r'M_{\text{motor,req}} > M_{\text{start}} + 2\,\text{Nm} & \Rightarrow \textbf{Too\;small}'
        r'\end{cases}'
    ),
    'f9':     r'P_{\text{rated}}\,[\text{kW}] = \dfrac{M_n\,[\text{Nm}] \cdot n_{\text{motor}}\,[\text{rpm}]}{9550}',
    'f9_inv': r'M_n\,[\text{Nm}] = \dfrac{9550 \times P_{\text{rated}}\,[\text{kW}]}{n_{\text{motor}}\,[\text{rpm}]}',
    'f9b':    r'9550 = \dfrac{60 \times 10^3}{2\pi} \approx 9549.3',
    'fg1': r'M_{2,\text{nom}} = \dfrac{M_{\text{nom}}}{i_{\text{worm}} \cdot \eta}',
    'fg2': r'M_{2,\max} = \dfrac{M_{\max}}{i_{\text{worm}} \cdot \eta}',
    'fg3': r'\lambda = \dfrac{M_{2,\text{nom}}}{M_{2,\max}}',
    'fg4': r'M_{\text{gear,soll}} = M_{2,\text{nom}} + \left(M_{2,\max} - M_{2,\text{nom}}\right) \cdot \lambda',
    'fg4_exp': (
        r'M_{\text{gear,soll}} = M_{2,\text{nom}} + '
        r'\left(M_{2,\max} - M_{2,\text{nom}}\right) \cdot '
        r'\dfrac{M_{2,\text{nom}}}{M_{2,\max}}'
    ),
    'fs_margin': r'\text{margin} = \dfrac{\text{value}_{\text{supplier}}}{\text{value}_{\text{required}}} \geq 1.10',
    'fs_ratio':  r'\text{deviation} = \dfrac{|\,r_{\text{supplier}} - r_{\text{calc}}\,|}{r_{\text{calc}}} \leq 2\%',
}


def _load_datasheet(post_data) -> tuple:
    """Parse optional datasheet_data JSON from POST. Returns (dict|None, str)."""
    raw = post_data.get('datasheet_data', '').strip()
    if raw:
        try:
            return json.loads(raw), raw
        except (json.JSONDecodeError, ValueError):
            pass
    return None, ''


def _spec_fields_from_form(sd: dict) -> dict:
    """Extract all spec_ fields from cleaned form data, returning safe defaults."""
    return {
        'spec_frame_material':    sd.get('spec_frame_material', '') or '',
        'spec_output_flange':     sd.get('spec_output_flange', '') or '',
        'spec_shaft':             sd.get('spec_shaft', '') or '',
        'spec_cooling_method':    sd.get('spec_cooling_method', '') or '',
        'spec_ip_rating':         sd.get('spec_ip_rating', '') or '',
        'spec_ambient_temp':      sd.get('spec_ambient_temp', '') or '',
        'spec_coating':           sd.get('spec_coating', '') or '',
        'spec_top_color':         sd.get('spec_top_color', '') or '',
        'spec_heater':            sd.get('spec_heater', '') or '',
        'spec_insulation_class':  sd.get('spec_insulation_class', '') or '',
        'spec_duty_cycle':        sd.get('spec_duty_cycle', '') or '',
        'spec_painting':          sd.get('spec_painting', '') or '',
        'spec_motor_certificate': sd.get('spec_motor_certificate', '') or '',
        'spec_weight_kg':         sd.get('spec_weight_kg'),
    }


def index(request):
    results = None
    save_form = SaveCalculationForm()
    form = DrivetrainForm()
    specs_form = MotorSpecsForm()
    datasheet = None
    datasheet_json = ''
    compliance = None

    if request.method == 'POST':
        form = DrivetrainForm(request.POST)
        specs_form = MotorSpecsForm(request.POST)
        datasheet, datasheet_json = _load_datasheet(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            results = drivetrain_sizing(
                crane_torque_max=d['crane_torque_max'],
                crane_torque_nom=d.get('crane_torque_nom'),
                worm_ratio=d['worm_ratio'],
                worm_efficiency=d['worm_efficiency'],
                motor_speed=d['motor_speed'],
                gearbox_output_speed=d['gearbox_output_speed'],
                motor_rated_torque=d['motor_rated_torque'],
                starting_factor=d['starting_factor'],
                supplier_motor_power_kw=d.get('supplier_motor_power_kw'),
                supplier_motor_rated_torque=d.get('supplier_motor_rated_torque'),
                supplier_motor_starting_torque=d.get('supplier_motor_starting_torque'),
                supplier_gearbox_rated_torque=d.get('supplier_gearbox_rated_torque'),
                supplier_bevel_ratio=d.get('supplier_bevel_ratio'),
                supplier_worm_ratio=d.get('supplier_worm_ratio'),
            )

        if specs_form.is_valid():
            compliance = check_compliance(specs_form.cleaned_data)

    return render(request, 'calculator/index.html', {
        'form': form,
        'specs_form': specs_form,
        'save_form': save_form,
        'results': results,
        'datasheet': datasheet,
        'datasheet_json': datasheet_json,
        'compliance': compliance,
        'active_page': 'calculator',
        **FORMULAS,
    })


def upload_datasheet(request):
    if request.method == 'GET':
        return render(request, 'calculator/datasheet_upload.html', {
            'form': DatasheetUploadForm(),
            'active_page': 'calculator',
        })

    form = DatasheetUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'calculator/datasheet_upload.html', {
            'form': form,
            'active_page': 'calculator',
        })

    pdf_file = request.FILES['pdf_file']
    supplier = form.cleaned_data['supplier_name']
    crane_type = form.cleaned_data['crane_type']
    raw_proto  = form.cleaned_data.get('price_prototype')
    raw_series = form.cleaned_data.get('price_series')
    price_proto  = float(raw_proto)  if raw_proto  else None
    price_series = float(raw_series) if raw_series else None

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
            for chunk in pdf_file.chunks():
                tmp.write(chunk)
        specs = parse_datasheet(tmp_path)
    except Exception as exc:
        form.add_error('pdf_file', f'Could not read PDF: {exc}')
        return render(request, 'calculator/datasheet_upload.html', {
            'form': form,
            'active_page': 'calculator',
        })
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    form_initial = specs_to_form_initial(specs)
    compliance = check_compliance(form_initial)

    datasheet = {
        'supplier':        supplier,
        'crane_type':      crane_type,
        'price_prototype': price_proto,
        'price_series':    price_series,
        'specs':           specs,
    }
    datasheet_json = json.dumps(datasheet)

    return render(request, 'calculator/datasheet_result.html', {
        'datasheet':      datasheet,
        'datasheet_json': datasheet_json,
        'compliance':     compliance,
        'form':           DrivetrainForm(),
        'specs_form':     MotorSpecsForm(initial=form_initial),
        'save_form':      SaveCalculationForm(initial={'crane_type': crane_type}),
        'active_page':    'calculator',
        **FORMULAS,
    })


def save_calculation(request):
    if request.method != 'POST':
        return redirect('index')

    calc_form  = DrivetrainForm(request.POST)
    save_form  = SaveCalculationForm(request.POST)
    specs_form = MotorSpecsForm(request.POST)

    if calc_form.is_valid() and save_form.is_valid():
        d  = calc_form.cleaned_data
        sd = specs_form.cleaned_data if specs_form.is_valid() else {}
        results = drivetrain_sizing(
            crane_torque_max=d['crane_torque_max'],
            crane_torque_nom=d.get('crane_torque_nom'),
            worm_ratio=d['worm_ratio'],
            worm_efficiency=d['worm_efficiency'],
            motor_speed=d['motor_speed'],
            gearbox_output_speed=d['gearbox_output_speed'],
            motor_rated_torque=d['motor_rated_torque'],
            starting_factor=d['starting_factor'],
            supplier_motor_power_kw=d.get('supplier_motor_power_kw'),
            supplier_motor_rated_torque=d.get('supplier_motor_rated_torque'),
            supplier_motor_starting_torque=d.get('supplier_motor_starting_torque'),
            supplier_gearbox_rated_torque=d.get('supplier_gearbox_rated_torque'),
            supplier_bevel_ratio=d.get('supplier_bevel_ratio'),
            supplier_worm_ratio=d.get('supplier_worm_ratio'),
        )
        ds, _ = _load_datasheet(request.POST)
        price_proto  = Decimal(str(ds['price_prototype']))  if ds and ds.get('price_prototype')  else None
        price_series = Decimal(str(ds['price_series']))     if ds and ds.get('price_series')     else None

        spec_data = _spec_fields_from_form(sd)

        MotorCalculation.objects.create(
            supplier_name=save_form.cleaned_data['supplier_name'],
            crane_type=save_form.cleaned_data['crane_type'],
            crane_torque_max=d['crane_torque_max'],
            crane_torque_nom=d.get('crane_torque_nom'),
            worm_ratio=d['worm_ratio'],
            worm_efficiency=d['worm_efficiency'],
            motor_speed=d['motor_speed'],
            motor_rated_torque=d['motor_rated_torque'],
            starting_factor=d['starting_factor'],
            gearbox_output_speed=d['gearbox_output_speed'],
            supplier_motor_power_kw=d.get('supplier_motor_power_kw'),
            supplier_motor_rated_torque=d.get('supplier_motor_rated_torque'),
            supplier_motor_starting_torque=d.get('supplier_motor_starting_torque'),
            supplier_gearbox_rated_torque=d.get('supplier_gearbox_rated_torque'),
            supplier_bevel_ratio=d.get('supplier_bevel_ratio'),
            supplier_worm_ratio=d.get('supplier_worm_ratio'),
            price_prototype=price_proto,
            price_series=price_series,
            torque_check=results['torque_check'],
            torque_margin=results['torque_margin'],
            motor_power_kw=results['motor_power_kw'],
            **spec_data,
        )
        return redirect('suppliers')

    results = None
    if calc_form.is_valid():
        d = calc_form.cleaned_data
        results = drivetrain_sizing(**{k: d[k] for k in (
            'crane_torque_max', 'crane_torque_nom', 'worm_ratio', 'worm_efficiency',
            'motor_speed', 'gearbox_output_speed', 'motor_rated_torque', 'starting_factor',
        )})

    compliance = None
    if specs_form.is_valid():
        compliance = check_compliance(specs_form.cleaned_data)

    datasheet, datasheet_json = _load_datasheet(request.POST)
    return render(request, 'calculator/index.html', {
        'form':           calc_form,
        'specs_form':     specs_form,
        'save_form':      save_form,
        'results':        results,
        'datasheet':      datasheet,
        'datasheet_json': datasheet_json,
        'compliance':     compliance,
        'active_page':    'calculator',
        **FORMULAS,
    })


def suppliers(request, crane_filter=None):
    qs = MotorCalculation.objects.all()
    if crane_filter == 'standard_pf':
        qs = qs.filter(crane_type=MotorCalculation.STANDARD_PF)
    elif crane_filter == 'pf_xxl':
        qs = qs.filter(crane_type=MotorCalculation.PF_XXL)
    return render(request, 'calculator/suppliers.html', {
        'calculations': qs,
        'active_page': 'suppliers',
        'crane_filter': crane_filter,
    })


def supplier_detail(request, pk):
    calc = get_object_or_404(MotorCalculation, pk=pk)
    results = calc.recalculate()
    return render(request, 'calculator/supplier_detail.html', {
        'calc': calc,
        'results': results,
        'active_page': 'suppliers',
        **FORMULAS,
    })


def delete_calculation(request, pk):
    calc = get_object_or_404(MotorCalculation, pk=pk)
    if request.method == 'POST':
        calc.delete()
    return redirect('suppliers')


def formulas(request):
    return render(request, 'calculator/formulas.html', {
        'active_page': 'formulas',
        **FORMULAS,
    })


def comparison(request):
    crane_filter = request.GET.get('crane', None)
    qs = MotorCalculation.objects.all()
    if crane_filter == 'standard_pf':
        qs = qs.filter(crane_type=MotorCalculation.STANDARD_PF)
    elif crane_filter == 'pf_xxl':
        qs = qs.filter(crane_type=MotorCalculation.PF_XXL)
    return render(request, 'calculator/comparison.html', {
        'calculations': qs,
        'crane_filter': crane_filter,
        'active_page': 'comparison',
    })
