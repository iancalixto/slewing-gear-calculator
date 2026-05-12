from django.shortcuts import render, redirect, get_object_or_404
from .forms import DrivetrainForm, SaveCalculationForm
from .engine import drivetrain_sizing
from .models import MotorCalculation

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
    # Gearbox sizing (load spectrum method) — optional, requires M_Nenn
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


def index(request):
    results = None
    save_form = SaveCalculationForm()
    form = DrivetrainForm()  # always starts empty

    if request.method == 'POST':
        form = DrivetrainForm(request.POST)
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

    return render(request, 'calculator/index.html', {
        'form': form,
        'save_form': save_form,
        'results': results,
        'active_page': 'calculator',
        **FORMULAS,
    })


def save_calculation(request):
    if request.method != 'POST':
        return redirect('index')

    calc_form = DrivetrainForm(request.POST)
    save_form = SaveCalculationForm(request.POST)

    if calc_form.is_valid() and save_form.is_valid():
        d = calc_form.cleaned_data
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
            torque_check=results['torque_check'],
            torque_margin=results['torque_margin'],
            motor_power_kw=results['motor_power_kw'],
        )
        return redirect('suppliers')

    # Validation failed — re-render calculator with errors
    results = None
    if calc_form.is_valid():
        d = calc_form.cleaned_data
        results = drivetrain_sizing(**{k: d[k] for k in (
            'crane_torque_max', 'crane_torque_nom', 'worm_ratio', 'worm_efficiency',
            'motor_speed', 'gearbox_output_speed', 'motor_rated_torque', 'starting_factor',
        )})
    return render(request, 'calculator/index.html', {
        'form': calc_form,
        'save_form': save_form,
        'results': results,
        'active_page': 'calculator',
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
