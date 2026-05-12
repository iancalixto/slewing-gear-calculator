from django.db import models


class MotorCalculation(models.Model):
    STANDARD_PF = 'standard_pf'
    PF_XXL = 'pf_xxl'
    CRANE_CHOICES = [
        (STANDARD_PF, 'Standard PF Crane'),
        (PF_XXL, 'PF-XXL'),
    ]

    # ── Metadata ─────────────────────────────────────────────────────────────
    supplier_name = models.CharField(max_length=200)
    crane_type = models.CharField(max_length=20, choices=CRANE_CHOICES)
    saved_at = models.DateTimeField(auto_now_add=True)
    price_prototype = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_series = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ── Calculation inputs ────────────────────────────────────────────────────
    crane_torque_max = models.FloatField()
    crane_torque_nom = models.FloatField(null=True, blank=True)
    worm_ratio = models.FloatField()
    worm_efficiency = models.FloatField()
    motor_speed = models.FloatField()
    motor_rated_torque = models.FloatField()
    starting_factor = models.FloatField()
    gearbox_output_speed = models.FloatField()

    # ── Optional supplier comparison inputs ───────────────────────────────────
    supplier_motor_power_kw = models.FloatField(null=True, blank=True)
    supplier_motor_rated_torque = models.FloatField(null=True, blank=True)
    supplier_motor_starting_torque = models.FloatField(null=True, blank=True)
    supplier_gearbox_rated_torque = models.FloatField(null=True, blank=True)
    supplier_bevel_ratio = models.FloatField(null=True, blank=True)
    supplier_worm_ratio = models.FloatField(null=True, blank=True)

    # ── Key results (stored for list display; detail re-runs engine) ──────────
    torque_check = models.CharField(max_length=20)
    torque_margin = models.FloatField()
    motor_power_kw = models.FloatField()

    class Meta:
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.supplier_name} ({self.get_crane_type_display()})"

    def recalculate(self):
        from .engine import drivetrain_sizing
        return drivetrain_sizing(
            crane_torque_max=self.crane_torque_max,
            crane_torque_nom=self.crane_torque_nom,
            worm_ratio=self.worm_ratio,
            worm_efficiency=self.worm_efficiency,
            motor_speed=self.motor_speed,
            gearbox_output_speed=self.gearbox_output_speed,
            motor_rated_torque=self.motor_rated_torque,
            starting_factor=self.starting_factor,
            supplier_motor_power_kw=self.supplier_motor_power_kw,
            supplier_motor_rated_torque=self.supplier_motor_rated_torque,
            supplier_motor_starting_torque=self.supplier_motor_starting_torque,
            supplier_gearbox_rated_torque=self.supplier_gearbox_rated_torque,
            supplier_bevel_ratio=self.supplier_bevel_ratio,
            supplier_worm_ratio=self.supplier_worm_ratio,
        )
