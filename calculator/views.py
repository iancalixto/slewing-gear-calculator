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

    return render(request, 'calculator/index.html', {'form': form, 'results': results})
