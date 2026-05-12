from .models import MotorCalculation


def sidebar_data(request):
    return {
        'sidebar_calculations': MotorCalculation.objects.values(
            'pk', 'supplier_name', 'crane_type', 'torque_check'
        ).order_by('-saved_at')[:30],
    }
