# Slewing Gear Calculator — Project Context

## What this is
Django 6.x web app for sizing slewing gear drivetrain motors on offshore cranes.
Local dev server: `py manage.py runserver` → http://127.0.0.1:8000/
Repo: https://github.com/iancalixto/slewing-gear-calculator
Local clone: `C:\Users\CALIXTOI\slewing-gear-calculator`
Network mirror (read-only reference): `\\satsbgc13fil21\ba\Marine\BU_Marine_Wind\02_Design_Wind\02_PROJECTS\PF_range\PF Redesign\10_Steuerung\Slewing Gear Motor\django_updates\`

## Stack
- Python 3.13, Django 6.x, SQLite3 (`db.sqlite3`)
- Bootstrap 5.3.3, Bootstrap Icons, KaTeX 0.16.11 (all via CDN)
- pdfplumber 0.11.9 for PDF extraction (`py -m pip install pdfplumber`)
- Use `py` (Python Launcher) — NOT `python` or `pip` directly (Windows alias issue)

## Key files
| File | Purpose |
|---|---|
| `calculator/models.py` | `MotorCalculation` model — add new spec fields here |
| `calculator/forms.py` | `DrivetrainForm`, `SaveCalculationForm`, `DatasheetUploadForm` |
| `calculator/views.py` | All views; `_load_datasheet()` reads JSON hidden field |
| `calculator/engine.py` | `drivetrain_sizing()` pure calculation function |
| `calculator/pdf_parser.py` | `parse_datasheet(pdf_path)` → `dict[str, str]` via pdfplumber + regex |
| `calculator/urls.py` | URL routing |
| `calculator/templates/calculator/` | All HTML templates |
| `calculator/static/calculator/` | Static files (CSS, images) |

## No Django sessions
`settings.py` has no sessions middleware configured. Datasheet data is passed between pages via a hidden form field `datasheet_data` containing JSON. Helper: `_load_datasheet(request.POST)` in `views.py`.

## Crane types (model constants)
- `MotorCalculation.STANDARD_PF = 'standard_pf'`
- `MotorCalculation.PF_XXL = 'pf_xxl'`

## Background image
Source: `\\Satsbgc13fil21\ba\Marine\BU_Marine_Wind\02_Design_Wind\02_PROJECTS\PF_range\PF Redesign\10_Steuerung\Slewing Gear Motor\20230602101923554.jpg`
Target: `calculator/static/calculator/bg.jpg`
Copy command: `Copy-Item "\\Satsbgc13fil21\ba\...\20230602101923554.jpg" "C:\Users\CALIXTOI\slewing-gear-calculator\calculator\static\calculator\bg.jpg"`

---

## PENDING ROUND 2 TASKS (not yet implemented)

### 1. Background image
- Copy `bg.jpg` to static folder (see above)
- In `base.html`: set `bg.jpg` as CSS `background-image` on `.page-content` with a dark overlay
- Remove existing PF crane banner image from `index.html` top-right card

### 2. Motor compliance check (9 required specs)
Required values that must be checked PASS/FAIL against datasheet or manual input:

| Parameter | Required value |
|---|---|
| Motor Frame Material | Cast Iron |
| Output Flange | Ø165 mm |
| Shaft | Ø32k6 |
| Cooling Method | IC410 TENV |
| IP Rating | IP66 |
| Ambient Temperature | -20°C to +45°C (or higher) |
| Coating | C5H / EN 12944-5 |
| Top Color | RAL7035 |
| Standstill Heater | 24VDC |

### 3. New motor spec fields (add to model + form)
- Insulation Class (e.g. F, H)
- Duty Cycle (e.g. S3-25%, S2-15%)
- Painting / Coating description
- Motor Certificate (e.g. DNV, GL, ATEX)
- Weight (kg)

### 4. PDF extraction enhancements
- Add IP Rating pattern to `pdf_parser.py` (r"ip\s*66", r"\bip66\b")
- Add extraction patterns for: Insulation Class, Motor Certificate, Weight
- Add `check_compliance(specs_dict) -> list[dict]` returning `[{label, required, found, status}]`
- On `datasheet_result.html`: show compliance table (PASS/FAIL per spec); pre-fill spec fields from PDF; show "not found — enter manually" for missing

### 5. DatasheetUploadForm — add crane type selector
Add `crane_type = forms.ChoiceField(choices=MotorCalculation.CRANE_CHOICES)` to `DatasheetUploadForm`
Show as radio buttons (PF Standard / PF-XXL) in `datasheet_upload.html`

### 6. New `/comparison/` page
- URL: `path('comparison/', views.comparison, name='comparison')`
- View: `comparison(request)` — queries all `MotorCalculation`, groups by crane type
- Template `comparison.html`: table with all saved motors as columns, spec parameters as rows
- Filter tabs: All / Standard PF / PF-XXL
- Add "Comparison" link to sidebar in `base.html`

### 7. Model migration
After adding spec fields to `models.py`:
```
py manage.py makemigrations
py manage.py migrate
```

### 8. Updated `save_calculation` view
Must also save all 15 spec fields from the form POST to `MotorCalculation`.

---

## models.py — fields to add (Round 2)
```python
# Motor compliance specs (stored from datasheet or manual input)
spec_frame_material = models.CharField(max_length=100, blank=True, default='')
spec_output_flange_mm = models.CharField(max_length=50, blank=True, default='')
spec_shaft = models.CharField(max_length=50, blank=True, default='')
spec_cooling_method = models.CharField(max_length=50, blank=True, default='')
spec_ip_rating = models.CharField(max_length=20, blank=True, default='')
spec_ambient_temp = models.CharField(max_length=50, blank=True, default='')
spec_coating = models.CharField(max_length=100, blank=True, default='')
spec_top_color = models.CharField(max_length=50, blank=True, default='')
spec_heater = models.CharField(max_length=50, blank=True, default='')
spec_insulation_class = models.CharField(max_length=10, blank=True, default='')
spec_duty_cycle = models.CharField(max_length=20, blank=True, default='')
spec_painting = models.CharField(max_length=200, blank=True, default='')
spec_motor_certificate = models.CharField(max_length=100, blank=True, default='')
spec_weight_kg = models.FloatField(null=True, blank=True)
```

## pdf_parser.py — patterns to add/update
```python
("IP Rating",       [r"\bip\s*66\b", r"ip66", r"ingress\s+prot"]),
("Insulation Class",[r"insul.*class\s*[fh]\b", r"\bclass\s+[fh]\b", r"thermal\s+class"]),
("Motor Certificate",[r"\bdnv\b", r"\bgl\b", r"\batex\b", r"type\s+approval", r"certificate"]),
("Weight",          [r"weight.*\d+\s*kg", r"\d+[\.,]\d+\s*kg", r"mass.*\d+\s*kg"]),
```
