from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

import os

# --- CONFIGURATION ---
OUTPUT_FILE = "RWA_Tokenization_Manual.pdf"
CODE_FILES = [
    "app/main.py",
    "app/agents/nlp_agent.py",
    "app/agents/verification_agent.py",
    "app/agents/tokenization_agent.py",
    "app/models/database.py",
    "static/js/app.js",
    "templates/index.html",
]
SCREENSHOT = "e73a0852-5dc4-478f-919d-5ed4409f0845.png"  # Your screenshot filename

# --- SETUP ---
styles = getSampleStyleSheet()

styleTitle = ParagraphStyle(
    name='TitleStyle',
    fontSize=28,
    leading=34,
    alignment=TA_CENTER,
    spaceAfter=20
)

styleHeading = ParagraphStyle(
    name='HeadingStyle',
    fontSize=20,
    leading=26,
    textColor=colors.HexColor("#003366"),
    spaceAfter=12
)

styleSubHeading = ParagraphStyle(
    name='SubHeadingStyle',
    fontSize=16,
    leading=22,
    textColor=colors.HexColor("#003366"),
    spaceAfter=10
)

styleNormal = styles['Normal']

styleCode = ParagraphStyle(
    name='CodeStyle',
    fontName='Courier',
    fontSize=9,
    leading=11,
    leftIndent=10,
    rightIndent=10,
    borderPadding=5,
    backColor=colors.whitesmoke,
    borderWidth=0.5,
    borderColor=colors.lightgrey
)

# --- CONTENT BUILDING ---
content = []

# Title Page
content.append(Spacer(1, 100))
content.append(Paragraph("RWA Tokenization App", styleTitle))
content.append(Paragraph("Developer & User Manual", styleTitle))
content.append(Spacer(1, 50))
content.append(Paragraph("Version 1.0", styleNormal))
content.append(Spacer(1, 500))
content.append(PageBreak())

# Screenshot Page
content.append(Paragraph("📸 Screenshot of Application", styleHeading))
if os.path.exists(SCREENSHOT):
    img = Image(SCREENSHOT)
    img._restrictSize(500, 350)
    content.append(img)
else:
    content.append(Paragraph(f"⚠️ Screenshot not found: {SCREENSHOT}", styleNormal))
content.append(PageBreak())

# Add each code file
for filepath in CODE_FILES:
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        content.append(Paragraph(f"📄 File: {filepath}", styleHeading))
        content.append(Spacer(1, 6))

        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        content.append(Preformatted(code, styleCode))
        content.append(PageBreak())
    else:
        content.append(Paragraph(f"⚠️ Missing file: {filepath}", styleNormal))
        content.append(PageBreak())

# --- GENERATE PDF ---
doc = SimpleDocTemplate(OUTPUT_FILE, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
doc.build(content)

print(f"✅ PDF generated: {OUTPUT_FILE}")
