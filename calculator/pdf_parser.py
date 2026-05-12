"""PDF datasheet parameter extraction for the Slewing Drive Calculator."""

import re

NOT_FOUND = "not in the datasheet"

# (display label, list of lowercase regex patterns)
SPEC_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "Motor Frame Material",
        [
            r"cast\s*iron", r"grey\s*cast", r"gjl[-\s]?\d*", r"gg-?\s*\d+",
            r"frame\s+material", r"housing\s+material", r"carcas[s]?",
        ],
    ),
    (
        "Output Flange",
        [
            r"ø\s*165", r"165\s*mm", r"output\s+flange",
            r"flange.*165", r"165.*flange",
        ],
    ),
    (
        "Shaft",
        [
            r"32k6", r"ø\s*32(?!\d)", r"shaft.*32",
            r"32.*x.*50", r"output\s+shaft",
        ],
    ),
    (
        "Cooling Method",
        [
            r"ic\s*410", r"ic410", r"\btenv\b", r"totally\s+enclosed",
            r"cooling\s+method", r"ic\s*4\s*1\s*0",
        ],
    ),
    (
        "Ambient Temperatures",
        [
            r"-\s*20\s*[°]?\s*c", r"ambient\s+temp",
            r"temp(?:erature)?\s+range", r"ambient.*-20",
        ],
    ),
    (
        "Voltages / Frequencies",
        [
            r"400\s*v", r"480\s*v", r"690\s*v",
            r"50\s*hz", r"60\s*hz", r"voltage[s]?.*freq", r"supply\s+voltage",
        ],
    ),
    (
        "Duty Cycle",
        [
            r"\bs3\s*[-–]?\s*25", r"\bs2\s*[-–]?\s*15",
            r"duty\s+cycle", r"\bs3\b", r"\bs2\b", r"intermittent",
        ],
    ),
    (
        "Standstill Heater",
        [
            r"stand.?still\s+heat", r"anti.?conden",
            r"24\s*vdc", r"24\s*v\s*dc", r"space\s+heat", r"heater.*24",
        ],
    ),
    (
        "Coating",
        [
            r"c5[-\s]*h\b", r"en\s*12944", r"coating\s+class",
            r"paint\s+system", r"corrosion\s+cat", r"surface\s+treat",
        ],
    ),
    (
        "Top Color",
        [
            r"ral\s*7035", r"ral7035", r"light\s+grey",
            r"top\s+colou?r", r"finish\s+colou?r", r"paint.*ral\s*7",
        ],
    ),
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
