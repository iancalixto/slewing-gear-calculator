from django import forms
from .models import MotorCalculation


FLOAT_WIDGET = {'class': 'form-control form-control-sm', 'step': 'any'}
FLOAT_WIDGET_OPT = {'class': 'form-control form-control-sm', 'step': 'any', 'placeholder': 'optional'}


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
