"""PDF datasheet parameter extraction for the Slewing Drive Calculator."""

import re

NOT_FOUND = "not in the datasheet"

SPEC_PATTERNS: list[tuple[str, list[str]]] = [
    ("Motor Frame Material", [
        r"cast\s*iron", r"grey\s*cast", r"gjl[-\s]?\d*", r"gg-?\s*\d+",
        r"frame\s+material", r"housing\s+material", r"carcas[s]?",
    ]),
    ("Output Flange", [
        r"ø\s*165", r"165\s*mm", r"output\s+flange",
        r"flange.*165", r"165.*flange",
    ]),
    ("Shaft", [
        r"32k6", r"ø\s*32(?!\d)", r"shaft.*32",
        r"32.*x.*50", r"output\s+shaft",
    ]),
    ("Cooling Method", [
        r"ic\s*410", r"ic410", r"\btenv\b", r"totally\s+enclosed",
        r"cooling\s+method", r"ic\s*4\s*1\s*0",
    ]),
    ("IP Rating", [
        r"\bip\s*66\b", r"ip66", r"ingress\s+prot.*66",
        r"protection\s+class.*66", r"ip\s*6[56]",
    ]),
    ("Ambient Temperatures", [
        r"-\s*20\s*[°]?\s*c", r"ambient\s+temp",
        r"temp(?:erature)?\s+range", r"ambient.*-20",
    ]),
    ("Voltages / Frequencies", [
        r"400\s*v", r"480\s*v", r"690\s*v",
        r"50\s*hz", r"60\s*hz", r"voltage[s]?.*freq", r"supply\s+voltage",
    ]),
    ("Insulation Class", [
        r"insul(?:ation)?\s+class\s*[fh]\b", r"\bclass\s*[fh]\b",
        r"thermal\s+class\s*[fh]", r"insulation\s+class",
        r"\bclass\s+f\b", r"\bclass\s+h\b", r"insul\.\s*class",
    ]),
    ("Duty Cycle", [
        r"\bs3\s*[-–]?\s*25", r"\bs2\s*[-–]?\s*15",
        r"duty\s+cycle", r"\bs3\b", r"\bs2\b", r"intermittent",
    ]),
    ("Standstill Heater", [
        r"stand.?still\s+heat", r"anti.?conden",
        r"24\s*vdc", r"24\s*v\s*dc", r"space\s+heat", r"heater.*24",
    ]),
    ("Coating", [
        r"c5[-\s]*h\b", r"en\s*12944", r"coating\s+class",
        r"paint\s+system", r"corrosion\s+cat", r"surface\s+treat",
    ]),
    ("Top Color", [
        r"ral\s*7035", r"ral7035", r"light\s+grey",
        r"top\s+colou?r", r"finish\s+colou?r", r"paint.*ral\s*7",
    ]),
    ("Motor Certificate", [
        r"\bdnv\b", r"\babs\b", r"\blloyd", r"\batex\b",
        r"type\s+approv", r"certificat", r"class\s+soc",
    ]),
    ("Weight", [
        r"weight\s*[:\-]?\s*\d+[\.,]?\d*\s*kg",
        r"mass\s*[:\-]?\s*\d+[\.,]?\d*\s*kg",
        r"\d+[\.,]\d*\s*kg\b",
        r"approx[\.,]?\s*\d+\s*kg",
    ]),
]

# Compliance rules: (form_field_name, display_label, required_display, regex_patterns)
_COMPLIANCE_RULES = [
    ('spec_frame_material', 'Motor Frame Material', 'Cast Iron',
     [r"cast\s*iron", r"gjl", r"gg[-\s]?\d+"]),
    ('spec_output_flange', 'Output Flange', 'Ø165 mm',
     [r"165"]),
    ('spec_shaft', 'Shaft', 'Ø32k6',
     [r"32k6"]),
    ('spec_cooling_method', 'Cooling Method', 'IC410 TENV',
     [r"ic\s*410", r"ic410", r"\btenv\b"]),
    ('spec_ip_rating', 'IP Rating', 'IP66',
     [r"\bip\s*66\b", r"ip66"]),
    ('spec_ambient_temp', 'Ambient Temperature', '−20°C to +45°C min.',
     [r"-\s*20"]),
    ('spec_coating', 'Coating', 'C5H / EN 12944-5',
     [r"c5[-\s]*h", r"en\s*12944"]),
    ('spec_top_color', 'Top Color', 'RAL7035',
     [r"ral\s*7035", r"ral7035"]),
    ('spec_heater', 'Standstill Heater', '24VDC',
     [r"24\s*v\s*dc", r"24\s*vdc"]),
]


def _find_field(text_lower: str, text_orig: str, patterns: list[str]) -> str:
    for pat in patterns:
        m = re.search(pat, text_lower)
        if m:
            start = max(0, m.start() - 30)
            end = min(len(text_orig), m.end() + 100)
            snippet = text_orig[start:end].strip()
            return re.sub(r"\s+", " ", snippet)
    return NOT_FOUND


def parse_datasheet(pdf_path: str) -> dict[str, str]:
    """Extract motor spec fields from a PDF. Returns {label: extracted_text}."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is required for PDF parsing.\n"
            "Install it with: pip install pdfplumber"
        )

    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)

    text_orig = "\n".join(pages)
    text_lower = text_orig.lower()

    return {
        label: _find_field(text_lower, text_orig, patterns)
        for label, patterns in SPEC_PATTERNS
    }


def specs_to_form_initial(specs: dict) -> dict:
    """Map PDF spec dict → MotorSpecsForm initial data (empty string for NOT_FOUND)."""
    mapping = {
        'Motor Frame Material': 'spec_frame_material',
        'Output Flange':        'spec_output_flange',
        'Shaft':                'spec_shaft',
        'Cooling Method':       'spec_cooling_method',
        'IP Rating':            'spec_ip_rating',
        'Ambient Temperatures': 'spec_ambient_temp',
        'Coating':              'spec_coating',
        'Top Color':            'spec_top_color',
        'Standstill Heater':    'spec_heater',
        'Insulation Class':     'spec_insulation_class',
        'Duty Cycle':           'spec_duty_cycle',
        'Motor Certificate':    'spec_motor_certificate',
    }
    initial = {}
    for pdf_label, form_field in mapping.items():
        val = specs.get(pdf_label, NOT_FOUND)
        initial[form_field] = '' if val == NOT_FOUND else val
    # Painting mirrors the coating text from PDF
    coating_val = specs.get('Coating', NOT_FOUND)
    initial['spec_painting'] = '' if coating_val == NOT_FOUND else coating_val
    return initial


def check_compliance(form_data: dict) -> list[dict]:
    """
    Check form field values against required PF crane motor specs.

    form_data: dict with keys spec_frame_material, spec_shaft, etc.
    Returns list of {label, required, found, status} where status ∈ PASS/FAIL/UNKNOWN.
    """
    results = []
    for field_key, label, required_display, patterns in _COMPLIANCE_RULES:
        value = (form_data.get(field_key) or '').strip()
        if not value:
            status = 'UNKNOWN'
        else:
            value_lower = value.lower()
            passed = any(re.search(p, value_lower) for p in patterns)
            status = 'PASS' if passed else 'FAIL'
        results.append({
            'label': label,
            'required': required_display,
            'found': value or '—',
            'status': status,
        })
    return results
