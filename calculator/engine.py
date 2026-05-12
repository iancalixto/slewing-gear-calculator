"""Core drivetrain sizing calculations (motor → bevel gearbox → worm gear → slewing ring)."""


SAFETY_FACTOR = 1.34  # Z-Systems sizing sheet constant


def _check(value, required, label):
    """Return a dict describing a single supplier vs. required comparison."""
    if value is None:
        return None
    margin = value / required
    if margin >= 1.10:
        status = 'OK'
    elif margin >= 1.00:
        status = 'Marginal'
    else:
        status = 'Too small'
    return {
        'label': label,
        'supplied': round(value, 3),
        'required': round(required, 3),
        'margin': round(margin, 3),
        'status': status,
    }


def _ratio_check(value, calculated, label):
    """Return a dict for ratio comparison (exact match within ±2%)."""
    if value is None:
        return None
    deviation = abs(value - calculated) / calculated
    status = 'OK' if deviation <= 0.02 else 'Mismatch'
    return {
        'label': label,
        'supplied': round(value, 3),
        'calculated': round(calculated, 3),
        'deviation_pct': round(deviation * 100, 2),
        'status': status,
    }


def drivetrain_sizing(
    crane_torque_max,
    worm_ratio,
    worm_efficiency,
    motor_speed,
    gearbox_output_speed,
    motor_rated_torque,
    starting_factor,
    crane_torque_nom=None,        # optional — only needed for Steps 2 & 3
    supplier_motor_power_kw=None,
    supplier_motor_rated_torque=None,
    supplier_motor_starting_torque=None,
    supplier_gearbox_rated_torque=None,
    supplier_bevel_ratio=None,
    supplier_worm_ratio=None,
):
    r = {}

    # Step 1 — Worm shaft torque (maximum)
    # M2_Max = M_Max / (i_worm × η)
    r['worm_input_torque_max'] = crane_torque_max / (worm_ratio * worm_efficiency)

    # Step 2 — Worm shaft torque (nominal)  [skipped when M_Nenn not provided]
    if crane_torque_nom is not None:
        r['worm_input_torque_nom'] = crane_torque_nom / (worm_ratio * worm_efficiency)
    else:
        r['worm_input_torque_nom'] = None

    # Step 3 — Required gearbox output torque  [skipped when M_Nenn not provided]
    if r['worm_input_torque_nom'] is not None:
        r['gearbox_required_torque'] = r['worm_input_torque_nom'] * SAFETY_FACTOR
    else:
        r['gearbox_required_torque'] = None

    # Step 4 — Bevel gearbox ratio
    # i_bevel = n_motor / n_gear_out
    r['bevel_ratio'] = motor_speed / gearbox_output_speed

    # Step 5 — Slewing speed
    # n_slew = n_gear_out / i_worm
    r['slewing_speed_rpm'] = gearbox_output_speed / worm_ratio

    # Step 6 — Motor torque required
    # M_motor_req = M2_Max / i_bevel
    r['motor_torque_required'] = r['worm_input_torque_max'] / r['bevel_ratio']

    # Step 7 — Motor starting torque available
    # M_start = M_n × (Ma/Mn)
    r['motor_start_torque'] = motor_rated_torque * starting_factor

    # Step 8 — Torque feasibility check
    # S15 = M_start (available), S21 = M_motor_req (required)
    # OK         : S15 > S21
    # On the limit: S21 <= S15 + 2  (required is within 2 Nm of available)
    # Too small  : S21 > S15 + 2
    S15 = r['motor_start_torque']
    S21 = r['motor_torque_required']
    r['torque_margin'] = S15 / S21  # ratio kept for display
    if S15 > S21:
        r['torque_check'] = 'OK'
    elif S21 <= S15 + 2:
        r['torque_check'] = 'On the limit'
    else:
        r['torque_check'] = 'Too small'

    # Step 9 — Motor rated power (nameplate)
    # P = (M_n × n_motor) / 9550
    # M_n is the rated torque from the motor nameplate, not the back-calculated
    # required torque. This gives the standard IEC power class of the motor.
    r['motor_power_kw'] = (motor_rated_torque * motor_speed) / 9550

    # ── Optional gearbox sizing (load spectrum method) ───────────────────────
    # Requires crane_torque_nom (M_Nenn). Uses M2_Nenn and M2_Max already
    # computed in Steps 1 and 2.
    if crane_torque_nom is not None:
        M2n = r['worm_input_torque_nom']   # M2_Nenn
        M2a = r['worm_input_torque_max']   # M2_Max
        # Step GB-3: load spectrum ratio  λ = M2_Nenn / M2_Max
        lam = M2n / M2a
        # Step GB-4: required gearbox nominal torque
        M_soll = M2n + (M2a - M2n) * lam
        r['gb_load_spectrum_ratio'] = round(lam, 4)
        r['gb_sizing_torque'] = round(M_soll, 3)
    else:
        r['gb_load_spectrum_ratio'] = None
        r['gb_sizing_torque'] = None

    # ── Supplier data checks ─────────────────────────────────────────────────
    supplier_checks = []
    checks_passed = None

    sc = _check(supplier_motor_starting_torque, r['motor_torque_required'],
                'Motor starting torque Ma vs required')
    if sc:
        supplier_checks.append(sc)

    sc = _check(supplier_motor_rated_torque, motor_rated_torque,
                'Motor rated torque M_n vs input')
    if sc:
        supplier_checks.append(sc)

    sc = _check(supplier_motor_power_kw, r['motor_power_kw'],
                'Motor power vs required')
    if sc:
        supplier_checks.append(sc)

    if r['gearbox_required_torque'] is not None:
        sc = _check(supplier_gearbox_rated_torque, r['gearbox_required_torque'],
                    'Gearbox rated torque vs required')
        if sc:
            supplier_checks.append(sc)

    sc = _ratio_check(supplier_bevel_ratio, r['bevel_ratio'],
                      'Bevel ratio vs calculated')
    if sc:
        supplier_checks.append(sc)

    sc = _ratio_check(supplier_worm_ratio, worm_ratio,
                      'Worm ratio vs input')
    if sc:
        supplier_checks.append(sc)

    r['supplier_checks'] = supplier_checks
    if supplier_checks:
        all_statuses = [c['status'] for c in supplier_checks]
        if all(s == 'OK' for s in all_statuses):
            checks_passed = 'ALL OK'
        elif any(s == 'Too small' or s == 'Mismatch' for s in all_statuses):
            checks_passed = 'FAIL'
        else:
            checks_passed = 'MARGINAL'
    r['supplier_overall'] = checks_passed

    # Round all numeric results for display (guard None for optional steps 2 & 3)
    for key in ('worm_input_torque_max', 'worm_input_torque_nom',
                'gearbox_required_torque', 'bevel_ratio',
                'slewing_speed_rpm', 'motor_torque_required',
                'motor_start_torque', 'torque_margin', 'motor_power_kw'):
        if r[key] is not None:
            r[key] = round(r[key], 3)

    return r
