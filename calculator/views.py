from django.shortcuts import render
from .forms import DrivetrainForm
from .engine import drivetrain_sizing

EXAMPLE_DATA = {
    'crane_torque_max': 62000,
    'crane_torque_nom': 23120,
    'worm_ratio': 150,
    'worm_efficiency': 0.40,
    'motor_speed': 1454,
    'gearbox_output_speed': 43.5,
    'motor_rated_torque': 12,
    'starting_factor': 3.40,
}

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
    'f8c': r'\begin{cases} \text{margin} \geq 1.3 & \Rightarrow \textbf{OK} \\ '
           r'1.1 \leq \text{margin} < 1.3 & \Rightarrow \textbf{Marginal} \\ '
           r'\text{margin} < 1.1 & \Rightarrow \textbf{Too small} \end{cases}',
    # Step 9 — both rearrangements of the same identity
    'f9':     r'P\,[\text{kW}] = \dfrac{M\,[\text{Nm}] \cdot n\,[\text{rpm}]}{9550}',
    'f9_inv': r'M\,[\text{Nm}] = \dfrac{9550 \times P\,[\text{kW}]}{n\,[\text{rpm}]}',
    'f9b':    r'9550 = \dfrac{60 \times 10^3}{2\pi} \approx 9549.3',
    'fs_margin': r'\text{margin} = \dfrac{\text{value}_{\text{supplier}}}{\text{value}_{\text{required}}} \geq 1.10',
    'fs_ratio':  r'\text{deviation} = \dfrac{|\,r_{\text{supplier}} - r_{\text{calc}}\,|}{r_{\text{calc}}} \leq 2\%',
}


def index(request):
    results = None
    form = DrivetrainForm(initial=EXAMPLE_DATA)

    if request.method == 'POST':
        form = DrivetrainForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            results = drivetrain_sizing(
                crane_torque_max=d['crane_torque_max'],
                crane_torque_nom=d['crane_torque_nom'],
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
        'results': results,
        **FORMULAS,
    })
