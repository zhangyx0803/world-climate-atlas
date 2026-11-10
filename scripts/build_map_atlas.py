from pathlib import Path
# -*- coding: utf-8 -*-
"""Build (a) a contact sheet of all 13 maps, (b) a Word atlas with one map per page."""
import os, glob
from PIL import Image
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_ORIENT

WD = str(Path(__file__).resolve().parent.parent)
MAPS = sorted(glob.glob(os.path.join(WD, "maps", "*.png")))
assert len(MAPS) == 13, len(MAPS)

# ---------------- (a) contact sheet ----------------
COLS, ROWS = 3, 5
TW, TH = 1180, 515          # thumbnail size (matches 3652x1592 aspect)
GAP, PAD = 26, 40
HEAD = 110
SW = PAD * 2 + COLS * TW + (COLS - 1) * GAP
SH = HEAD + PAD + ROWS * (TH + 46) + (ROWS - 1) * GAP

sheet = Image.new("RGB", (SW, SH), (255, 255, 255))
FZ = r"C:\Windows\Fonts"
def f(p, s):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(p, s)
    except Exception:
        return ImageFont.load_default()

from PIL import ImageDraw
sd = ImageDraw.Draw(sheet)
f_title = f(os.path.join(FZ, "msyhbd.ttc"), 46)
f_name = f(os.path.join(FZ, "simsun.ttc"), 26)
f_sub = f(os.path.join(FZ, "simsun.ttc"), 20)

sd.text((PAD, 26), "世界气候类型分布图集 · 13 张", font=f_title, fill=(28, 42, 66))
sd.text((PAD, 78), "底图：Natural Earth 真实国界数据　|　每张图标出该气候类型所在的国家与地区", font=f_sub, fill=(96, 104, 118))

for i, mp in enumerate(MAPS):
    r, c = divmod(i, COLS)
    x = PAD + c * (TW + GAP)
    y = HEAD + PAD + r * (TH + 46 + GAP)
    im = Image.open(mp).convert("RGB")
    im.thumbnail((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, y))
    sd.rectangle([x, y, x + im.width, y + im.height], outline=(178, 184, 194), width=2)
    name = os.path.splitext(os.path.basename(mp))[0]
    sd.text((x, y + TH + 8), name, font=f_name, fill=(40, 50, 66))

sheet_path = os.path.join(WD, "世界气候类型分布图集_总览.png")
sheet.save(sheet_path)
print("contact sheet:", sheet_path, sheet.size)

# ---------------- (b) Word atlas ----------------
doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
sec.left_margin = sec.right_margin = Cm(1.2)
sec.top_margin = sec.bottom_margin = Cm(1.0)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

def head(text, size, bold=True, color=(0x1F, 0x3B, 0x63), after=6, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = RGBColor(*color)
    return p

head("世界气候类型分布图集", 22, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
head("——按气候类型分幅，每型一幅世界图（底图：Natural Earth 真实国界）", 11,
     bold=False, color=(0x55, 0x66, 0x77), align=WD_ALIGN_PARAGRAPH.CENTER, after=10)

for i, mp in enumerate(MAPS, 1):
    if i > 1:
        doc.add_page_break()
    name = os.path.splitext(os.path.basename(mp))[0]
    head(f"{name}", 15, after=4)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(mp, width=Cm(27.0))

out = os.path.join(WD, "世界气候类型分布图集.docx")
doc.save(out)
print("atlas:", out)
