from .models import MotorCalculation


def sidebar_data(request):
    qs = MotorCalculation.objects.values('pk', 'supplier_name', 'crane_type', 'torque_check').order_by('-saved_at')
    return {
        'sidebar_calculations': qs[:30],
        'sidebar_standard_count': MotorCalculation.objects.filter(crane_type=MotorCalculation.STANDARD_PF).count(),
        'sidebar_xxl_count': MotorCalculation.objects.filter(crane_type=MotorCalculation.PF_XXL).count(),
    }
