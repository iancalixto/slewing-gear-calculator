from django import forms
from .models import MotorCalculation


FLOAT_WIDGET     = {'class': 'form-control form-control-sm', 'step': 'any'}
FLOAT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'step': 'any', 'placeholder': 'optional'}
TEXT_WIDGET      = {'class': 'form-control form-control-sm'}
TEXT_WIDGET_OPT  = {'class': 'form-control form-control-sm', 'placeholder': 'optional'}


class DrivetrainForm(forms.Form):
    # ── Crane load ──────────────────────────────────────────────────────────
    crane_torque_max = forms.FloatField(
        label='Max torque M_Max (Nm)',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 62000'}),
    )
    crane_torque_nom = forms.FloatField(
        label='Nominal torque M_Nenn (Nm) — optional',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 23120 (for gearbox sizing)'}),
    )

    # ── Worm gear ────────────────────────────────────────────────────────────
    worm_ratio = forms.FloatField(
        label='Worm ratio i_worm',
        min_value=1,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 150'}),
    )
    worm_efficiency = forms.FloatField(
        label='Worm efficiency η (0–1)',
        min_value=0.01, max_value=1.0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 0.40'}),
    )

    # ── Motor ────────────────────────────────────────────────────────────────
    motor_speed = forms.FloatField(
        label='Motor speed n_motor (rpm)',
        min_value=1,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 1454'}),
    )
    motor_rated_torque = forms.FloatField(
        label='Motor rated torque M_n (Nm)',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 12'}),
    )
    starting_factor = forms.FloatField(
        label='Starting factor Ma/Mn',
        min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 3.40'}),
    )

    # ── Gearbox ──────────────────────────────────────────────────────────────
    gearbox_output_speed = forms.FloatField(
        label='Gearbox output speed n_gear_out (rpm)',
        min_value=0.001,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET, 'placeholder': 'e.g. 43.5'}),
    )

    # ── Supplier data (optional comparison) ─────────────────────────────────
    supplier_motor_power_kw = forms.FloatField(
        label='Supplier motor power (kW)',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_motor_rated_torque = forms.FloatField(
        label='Supplier motor rated torque M_n (Nm)',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_motor_starting_torque = forms.FloatField(
        label='Supplier motor starting torque Ma (Nm)',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_gearbox_rated_torque = forms.FloatField(
        label='Supplier gearbox rated torque (Nm)',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_bevel_ratio = forms.FloatField(
        label='Supplier bevel gearbox ratio',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )
    supplier_worm_ratio = forms.FloatField(
        label='Supplier worm ratio',
        required=False, min_value=0,
        widget=forms.NumberInput(attrs=FLOAT_WIDGET_OPT),
    )


class MotorSpecsForm(forms.Form):
    """Motor physical specification fields for compliance checking and storage."""

    spec_frame_material = forms.CharField(
        label='Frame Material', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Cast Iron / GJL-250'}),
    )
    spec_output_flange = forms.CharField(
        label='Output Flange', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Ø165 mm'}),
    )
    spec_shaft = forms.CharField(
        label='Shaft', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Ø32k6 × 50'}),
    )
    spec_cooling_method = forms.CharField(
        label='Cooling Method', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IC410 TENV'}),
    )
    spec_ip_rating = forms.CharField(
        label='IP Rating', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. IP66'}),
    )
    spec_ambient_temp = forms.CharField(
        label='Ambient Temperature', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. -20°C to +45°C'}),
    )
    spec_coating = forms.CharField(
        label='Coating Class', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. C5H / EN 12944-5'}),
    )
    spec_top_color = forms.CharField(
        label='Top Color', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. RAL7035'}),
    )
    spec_heater = forms.CharField(
        label='Standstill Heater', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. 24VDC'}),
    )
    spec_insulation_class = forms.CharField(
        label='Insulation Class', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. F or H'}),
    )
    spec_duty_cycle = forms.CharField(
        label='Duty Cycle', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. S3-25%'}),
    )
    spec_painting = forms.CharField(
        label='Painting Description', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. Marine C5H system, epoxy primer'}),
    )
    spec_motor_certificate = forms.CharField(
        label='Motor Certificate', required=False,
        widget=forms.TextInput(attrs={**TEXT_WIDGET_OPT, 'placeholder': 'e.g. DNV, GL, ABS'}),
    )
    spec_weight_kg = forms.FloatField(
        label='Weight (kg)', required=False, min_value=0,
        widget=forms.NumberInput(attrs={**FLOAT_WIDGET_OPT, 'placeholder': 'e.g. 45'}),
    )


class SaveCalculationForm(forms.Form):
    supplier_name = forms.CharField(
        max_length=200,
        label='Supplier / Motor name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'e.g. Siemens 1LA7 0.75 kW',
        }),
    )
    crane_type = forms.ChoiceField(
        choices=MotorCalculation.CRANE_CHOICES,
        label='Crane type',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )


class DatasheetUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label='PDF Datasheet',
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-sm',
            'accept': '.pdf',
        }),
    )
    supplier_name = forms.CharField(
        max_length=200,
        label='Supplier Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'e.g. Bonfiglioli, ABB, Siemens',
        }),
    )
    crane_type = forms.ChoiceField(
        choices=MotorCalculation.CRANE_CHOICES,
        label='Crane Type',
        initial=MotorCalculation.STANDARD_PF,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    price_prototype = forms.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        label='Prototype Price (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01',
            'placeholder': 'e.g. 1250.00',
        }),
    )
    price_series = forms.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        label='Series Price — 100 units (€)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.01',
            'placeholder': 'e.g. 980.00',
        }),
    )
