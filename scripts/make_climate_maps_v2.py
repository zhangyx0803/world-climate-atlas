# -*- coding: utf-8 -*-
"""
One world map per climate type (13 maps) -- v2.

v2 change: countries are NO LONGER filled as a whole. Each map draws the actual
climate REGION as a filled polygon (clipped to land), so the highlighted shape is
the climate zone itself, with country borders showing through as context.
Place names (撒哈拉沙漠, 中南半岛, 亚马孙平原 ...) are labelled on each map.

Base map : Natural Earth 110m country boundaries (real geometry).
Renderer : Pillow only.
NOTE     : region outlines are hand-drawn schematic extents based on the source
           courseware's descriptions, not a surveyed climate-boundary dataset.
"""
import json, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = str(Path(__file__).resolve().parent.parent)
GEO = os.path.join(WD, "data", "countries_110m.geojson")
OUT = os.path.join(WD, "maps")
os.makedirs(OUT, exist_ok=True)

FZ = r"C:\Windows\Fonts"
def font(p, s):
    try:
        return ImageFont.truetype(p, s)
    except Exception:
        return ImageFont.load_default()

# ---------------- view window ----------------
LON0, LON1, LAT0, LAT1 = -180.0, 180.0, -58.0, 84.0
SCALE = 10.0
W = int(round((LON1 - LON0) * SCALE))
H = int(round((LAT1 - LAT0) * SCALE))
PAD_L, PAD_R, PAD_T, PAD_B = 26, 26, 96, 108
IW, IH = W + PAD_L + PAD_R, H + PAD_T + PAD_B

def px(lon, lat):
    return (PAD_L + (lon - LON0) * SCALE, PAD_T + (LAT1 - lat) * SCALE)

# ---------------- load geometry ----------------
gj = json.load(open(GEO, encoding="utf-8"))

def polys_of(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c]
    if t == "MultiPolygon":
        return c
    return []

CO = []
for f in gj["features"]:
    p = f["properties"]
    rings = []
    for poly in polys_of(f["geometry"]):
        outer = poly[0]
        if len(outer) < 4:
            continue
        lons = [q[0] for q in outer]
        if max(lons) - min(lons) > 350:
            continue
        rings.append(outer)
    if not rings:
        continue
    CO.append({"name": p.get("ADMIN") or p.get("NAME"),
               "px": [[px(x, y) for x, y in r] for r in rings]})

# ---------------- palette ----------------
C_TITLE = (28, 42, 66)
C_OCEAN = (222, 235, 245)
C_LAND  = (232, 231, 223)
C_LINE  = (172, 175, 171)
C_GRID  = (198, 215, 230)
C_EQ    = (146, 178, 205)

TYPE_COLOR = {
    "热带雨林":     (24, 132, 70),
    "热带稀树草原": (150, 188, 58),
    "热带沙漠":     (226, 170, 46),
    "热带季风":     (16, 156, 138),
    "地中海":       (228, 118, 38),
    "亚热带季风":   (62, 104, 188),
    "亚热带湿润":   (116, 158, 214),
    "温带海洋性":   (40, 100, 162),
    "温带大陆性":   (166, 130, 80),
    "温带季风":     (110, 74, 160),
    "亚寒带针叶林": (36, 92, 124),
    "极地":         (124, 170, 200),
    "高原山地":     (148, 110, 176),
}
TYPE_EN = {
    "热带雨林": "Tropical rainforest", "热带稀树草原": "Tropical savanna",
    "热带沙漠": "Hot desert", "热带季风": "Tropical monsoon",
    "地中海": "Mediterranean", "亚热带季风": "Humid subtropical (monsoon)",
    "亚热带湿润": "Humid subtropical", "温带海洋性": "Temperate oceanic",
    "温带大陆性": "Temperate continental", "温带季风": "Temperate monsoon",
    "亚寒带针叶林": "Subarctic (taiga)", "极地": "Polar",
    "高原山地": "Highland / Alpine",
}

# =====================================================================
# Climate regions.  regs = [(name, [(lon,lat), ...]), ...]
# =====================================================================
FS = [
 dict(key="热带雨林气候", color="热带雨林",
   sub="热带 · 全年高温多雨（全年受赤道低气压带控制）", fname="01_热带雨林气候.png",
   regs=[
     ("亚马孙平原",        [(-74,-9),(-66,-6),(-58,-4),(-50,0),(-46,-2),(-47,-8),(-52,-14),(-62,-14),(-72,-12)]),
     ("刚果盆地",          [(9,4),(15,5),(24,6),(31,5),(31,-5),(24,-9),(15,-8),(9,-3)]),
     ("几内亚湾沿岸",      [(-15,11),(-9,9),(-3,7),(3,8),(9,6),(10,4),(4,4),(-2,3),(-9,3),(-15,5)]),
     ("马达加斯加岛东部",  [(47.5,-24),(51,-21),(50,-14),(47,-13),(46,-17),(46,-22)]),
     ("马来群岛",          [(95,5),(108,7),(120,8),(135,5),(142,-2),(150,-8),(141,-10),(130,-7),(120,-8),(110,-7),(100,-2)]),
     ("新几内亚",          [(130,-1),(140,-2),(151,-6),(151,-11),(141,-10),(130,-9)]),
     ("澳大利亚东北部",    [(144,-26),(152,-24),(153,-15),(146,-11),(143,-14),(142,-19)]),
   ],
   labels=[("亚马孙平原",(-62,-4),None), ("刚果盆地",(19,1),None),
           ("几内亚湾沿岸",(-4,7),(-34,-6)), ("马达加斯加岛东部",(48.5,-19),(30,-42)),
           ("马来群岛",(114,0.5),(112,-26)), ("新几内亚",(142,-6),None),
           ("澳大利亚东北部",(145,-18),(158,-40))]),

 dict(key="热带稀树草原气候", color="热带稀树草原",
   sub="热带 · 全年高温，明显干湿季（赤道低压与信风交替控制）", fname="02_热带稀树草原气候.png",
   regs=[
     ("非洲大草原（北带）", [(15,17),(30,16),(38,12),(41,6),(36,3),(26,2),(16,6),(8,10),(3,14)]),
     ("非洲大草原（南带）", [(11,-6),(19,-8),(27,-11),(35,-15),(40,-20),(36,-26),(31,-25),(24,-20),(15,-16),(11,-11)]),
     ("东非高原",          [(31,3),(39,3),(40,-6),(35,-11),(31,-8)]),
     ("巴西高原",          [(-60,-6),(-52,-4),(-42,-6),(-38,-12),(-40,-20),(-48,-23),(-58,-18),(-62,-12)]),
     ("澳大利亚北部",      [(121,-15),(127,-11),(136,-11),(143,-13),(146,-20),(140,-23),(130,-24),(121,-23)]),
   ],
   labels=[("非洲大草原",(22,10),(-40,4)), ("东非高原",(35.5,-2),(46,-26)),
           ("巴西高原",(-47,-13),(-66,-26)), ("澳大利亚北部",(133,-17),(132,-46))]),

 dict(key="热带沙漠气候", color="热带沙漠",
   sub="热带 · 全年炎热干燥（副热带高气压带与内陆信风控制）", fname="03_热带沙漠气候.png",
   regs=[
     ("撒哈拉沙漠",        [(-16,19),(-16,26),(-10,30),(0,31),(11,33),(25,31),(34,29),(35,22),(31,16),(16,15),(0,15),(-12,16)]),
     ("阿拉伯半岛",        [(35,29),(48,29),(56,24),(59,21),(52,16),(44,13),(38,17),(34,25)]),
     ("纳米布沙漠",        [(11.5,-17),(17,-19),(17,-28),(15,-28),(13,-22)]),
     ("阿塔卡马沙漠",      [(-71,-18),(-69,-20),(-69,-27),(-70,-30),(-72,-29),(-71,-24)]),
     ("南美西海岸 30°S—20°S",[(-81,-2),(-79,-5),(-77,-10),(-76,-16),(-73,-18),(-71,-14),(-76,-8),(-79,-4)]),
     ("加利福尼亚寒流沿岸",[(-117,33),(-114,31),(-110,27),(-109,23),(-112,23),(-115,28),(-119,31)]),
     ("澳大利亚西部沙漠",  [(114,-20),(126,-19),(134,-22),(139,-27),(134,-31),(124,-33),(115,-31)]),
   ],
   labels=[("撒哈拉沙漠",(13,24),(30,-4)), ("阿拉伯半岛",(46,22),None),
           ("纳米布沙漠",(14.5,-23),(20,-46)), ("阿塔卡马沙漠",(-69.5,-24),(-92,-34)),
           ("南美西海岸 30°S—20°S",(-78,-6),(-108,-10)),
           ("加利福尼亚寒流沿岸",(-114,29),(-136,20)),
           ("澳大利亚西部沙漠",(128,-26),(128,-46))]),

 dict(key="热带季风气候", color="热带季风",
   sub="热带 · 全年高温，明显旱雨季（海陆热力差异＋气压带风带季节移动）", fname="04_热带季风气候.png",
   regs=[
     ("南亚印度半岛",      [(70,23),(78,28),(86,26),(92,24),(95,20),(93,15),(85,11),(79,8),(76,12),(72,18)]),
     ("斯里兰卡",          [(80,7),(82,9),(82,6),(80,5)]),
     ("东南亚中南半岛",    [(94,23),(100,23),(108,23),(108,11),(106,8),(100,6),(98,11),(94,17)]),
     ("海南岛",            [(108.6,20),(111,20),(111,18),(108.6,18.2)]),
   ],
   labels=[("南亚印度半岛",(80,19),(56,6)), ("东南亚中南半岛",(102,15),(112,-8))]),

 dict(key="地中海气候", color="地中海",
   sub="亚热带 · 夏季高温少雨，冬季温和多雨（副高与西风交替控制）", fname="05_地中海气候.png",
   regs=[
     ("地中海沿岸",        [(-9,38),(-9,43),(0,44),(8,44),(16,42),(24,41),(32,37),(36,36),(35,32),(24,31),(10,32),(0,34),(-6,35)]),
     ("美国西海岸（加州）", [(-124,40),(-121,37),(-117,32),(-116,30),(-119,32),(-123,36)]),
     ("南美西海岸 30°S—40°S",[(-72,-30),(-70,-33),(-71,-38),(-73,-39),(-73,-34),(-73,-31)]),
     ("南非西南部（好望角）",[(17,-31),(20,-32),(24,-34),(20,-36),(18,-34)]),
     ("澳大利亚西南部",    [(114,-29),(118,-29),(120,-33),(116,-35),(114,-33)]),
   ],
   labels=[("地中海沿岸",(2,42),(-22,52)), ("美国西海岸",(-121,36),(-146,44)),
           ("南美西海岸 30°S—40°S",(-72,-35),(-98,-44)),
           ("南非西南部（好望角）",(20,-33.5),(24,-52)),
           ("澳大利亚西南部",(117,-32),(120,-50))]),

 dict(key="亚热带季风气候", color="亚热带季风",
   sub="亚热带 · 夏季高温多雨，冬季温和少雨（海陆热力差异）", fname="06_亚热带季风气候.png",
   regs=[
     ("东亚秦岭—淮河以南地区",[(103,32),(110,32),(118,33),(122,31),(122,22),(112,22),(104,24)]),
     ("日本群岛南部",      [(129,32),(136,34),(141,36),(141,33),(135,31),(130,30)]),
     ("台湾岛",            [(120,25),(122,25),(122,22),(120,22)]),
   ],
   labels=[("东亚秦岭—淮河以南地区",(112,27),(118,4)),
           ("日本群岛南部",(135,35),(150,18)),
           ("台湾岛",(121,23),(124,10))]),

 dict(key="亚热带湿润气候", color="亚热带湿润",
   sub="亚热带 · 夏季高温多雨，冬季温和少雨（海陆热力差异较弱，年较差小）", fname="07_亚热带湿润气候.png",
   regs=[
     ("美国东南部",        [(-95,33),(-86,34),(-77,35),(-75,31),(-80,25),(-88,26),(-94,29)]),
     ("南美拉普拉塔平原",  [(-64,-27),(-56,-25),(-53,-30),(-55,-36),(-62,-37),(-66,-33)]),
     ("澳大利亚东南部",    [(140,-28),(152,-26),(153,-33),(149,-38),(142,-37),(139,-33)]),
   ],
   labels=[("美国东南部",(-85,31),(-108,14)),
           ("南美拉普拉塔平原",(-59,-31),(-84,-48)),
           ("澳大利亚东南部",(147,-33),(150,-52))]),

 dict(key="温带海洋性气候", color="温带海洋性",
   sub="温带 · 全年温和湿润（全年受来自海洋的西风控制）", fname="08_温带海洋性气候.png",
   regs=[
     ("西欧",              [(-10,43),(-10,49),(0,51),(7,54),(10,58),(16,66),(26,69),(28,63),(22,58),(13,55),(8,50),(-2,45)]),
     ("美国西北沿海",      [(-129,51),(-123,50),(-122,44),(-124,39),(-128,44)]),
     ("南美西海岸 40°S—60°S",[(-75,-40),(-71,-42),(-70,-49),(-72,-54),(-75,-50),(-75,-44)]),
     ("新西兰",            [(166,-45),(172,-41),(175,-37),(178,-38),(174,-41),(170,-46),(167,-46)]),
     ("塔斯马尼亚岛",      [(144,-41),(148,-41),(148,-44),(144,-43)]),
   ],
   labels=[("西欧",(5,47),(-30,62)), ("美国西北沿海",(-124,44.5),(-152,36)),
           ("南美西海岸 40°S—60°S",(-73,-46),(-102,-54)),
           ("新西兰",(173,-42),(180,-54)), ("塔斯马尼亚岛",(146,-42),(152,-52))]),

 dict(key="温带大陆性气候", color="温带大陆性",
   sub="温带 · 夏热冬冷，降水稀少且集中于夏季（深居内陆／背风侧）", fname="09_温带大陆性气候.png",
   regs=[
     ("东欧",              [(28,52),(40,53),(48,55),(60,55),(64,52),(60,47),(48,45),(38,47),(28,48)]),
     ("中亚",              [(46,34),(56,36),(66,38),(76,42),(88,46),(88,51),(76,53),(64,52),(52,46),(44,40)]),
     ("北美中部平原",      [(-106,50),(-96,50),(-86,50),(-80,38),(-86,31),(-98,31),(-104,37)]),
     ("巴塔哥尼亚高原",    [(-72,-39),(-66,-39),(-63,-44),(-66,-53),(-71,-54),(-73,-48)]),
   ],
   labels=[("东欧",(37,50),(16,64)), ("中亚",(64,45),(66,26)),
           ("北美中部平原",(-95,41),(-126,24)),
           ("巴塔哥尼亚高原",(-68,-46),(-108,-46))]),

 dict(key="温带季风气候", color="温带季风",
   sub="温带 · 夏季高温多雨，冬季寒冷干燥（海陆热力差异）", fname="10_温带季风气候.png",
   regs=[
     ("东亚秦岭—淮河以北地区",[(104,42),(112,44),(120,45),(128,45),(135,46),(135,38),(124,34),(114,34),(104,35)]),
     ("朝鲜半岛",          [(125,38),(129,39),(129,35),(126,34)]),
     ("日本群岛北部",      [(139,37),(143,40),(145,43),(142,41),(139,36)]),
   ],
   labels=[("东亚秦岭—淮河以北地区",(117,39),(120,60)),
           ("朝鲜半岛",(127,36),(134,14)),
           ("日本群岛北部",(140.5,38),(152,16))]),

 dict(key="亚寒带针叶林气候", color="亚寒带针叶林",
   sub="亚寒带 · 冬季漫长严寒，夏季短促温暖，降水集中于暖季", fname="11_亚寒带针叶林气候.png",
   regs=[
     ("北欧",              [(5,60),(13,62),(20,66),(28,68),(33,66),(30,60),(24,57),(12,57)]),
     ("北亚（西伯利亚）",  [(35,58),(75,58),(110,57),(140,54),(145,50),(140,45),(120,47),(90,48),(60,50),(40,52)]),
     ("北美洲北部（加拿大）",[(-165,63),(-140,66),(-120,64),(-100,60),(-76,53),(-60,50),(-58,56),(-80,60),(-105,68),(-130,70),(-155,69)]),
   ],
   labels=[("北欧",(18,63),(-30,74)), ("北亚（西伯利亚）",(100,52),(104,76)),
           ("北美洲北部（加拿大）",(-105,58),(-116,32))]),

 dict(key="极地气候", color="极地",
   sub="寒带 · 终年严寒、降水稀少、多大风（受极地高气压带或极地东风带控制）", fname="12_极地气候.png",
   regs=[
     ("北冰洋沿岸（欧亚）",[(-10,68),(-10,72),(20,73),(45,74),(70,74),(100,76),(130,73),(150,70),(160,66),(120,70),(80,70),(40,68),(10,66)]),
     ("加拿大北部群岛",    [(-130,68),(-110,69),(-90,69),(-70,65),(-60,60),(-70,56),(-90,60),(-110,64),(-128,66)]),
     ("格陵兰岛",          [(-58,60),(-48,62),(-30,68),(-22,70),(-20,76),(-30,82),(-45,82),(-58,76),(-68,70),(-63,63)]),
   ],
   labels=[("北冰洋沿岸",(78,72),(-26,58)), ("北亚北冰洋沿岸",(120,73),(114,56)),
           ("加拿大北部群岛",(-100,66),(-142,50)),
           ("格陵兰岛",(-42,72),(-72,54))]),

 dict(key="高原山地气候", color="高原山地",
   sub="海拔高 · 热量和水分垂直变化，气候垂直分异明显", fname="13_高原山地气候.png",
   regs=[
     ("青藏高原",          [(76,37),(86,36),(97,34),(103,31),(102,26),(94,27),(84,29),(78,31)]),
     ("帕米尔—天山",       [(68,38),(76,42),(84,43),(90,43),(88,38),(78,36)]),
     ("落基山脉",          [(-126,52),(-118,52),(-106,46),(-106,34),(-114,32),(-122,42)]),
     ("安第斯山脉",        [(-79,2),(-76,-4),(-73,-15),(-68,-22),(-69,-33),(-71,-45),(-73,-52),(-75,-45),(-72,-30),(-72,-15),(-77,-2)]),
     ("埃塞俄比亚高原",    [(35,14),(40,12),(40,6),(36,5),(35,9)]),
     ("东非高原山地",      [(29,0),(34,1),(36,-3),(33,-8),(29,-5),(28,-2)]),
   ],
   labels=[("青藏高原",(90,31),(92,16)), ("帕米尔—天山",(80,40),(52,52)),
           ("落基山脉",(-115,44),(-146,56)), ("安第斯山脉",(-70,-20),(-94,-46)),
           ("埃塞俄比亚高原",(37.5,9),(44,-10)), ("东非高原山地",(32,-3),(14,-30))]),
]

for _s in FS:
    assert _s["color"] in TYPE_COLOR, _s["color"]

# ---------------- clipping to land ----------------
def point_in_ring(x, y, ring):
    inside = False
    n = len(ring); j = n - 1
    for i in range(n):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside

def on_land(x, y):
    for c in CO:
        for r in c["px"]:
            if point_in_ring(x, y, r):
                return True
    return False

def land_mask():
    """One-channel mask of all land, at map resolution."""
    m = Image.new("L", (IW, IH), 0)
    md = ImageDraw.Draw(m)
    for c in CO:
        for r in c["px"]:
            md.polygon(r, fill=255)
    return m

def stamp_region(target, poly_px, col, alpha, outline_w=3):
    """Fill the polygon with `col`, keeping only the part that falls on land.

    Uses a raster mask intersection, so archipelagos stay intact instead of
    collapsing when the coastline cuts through the ring.
    """
    xs = [p[0] for p in poly_px]; ys = [p[1] for p in poly_px]
    x0 = max(int(min(xs)) - 4, 0); y0 = max(int(min(ys)) - 4, 0)
    x1 = min(int(max(xs)) + 4, IW - 1); y1 = min(int(max(ys)) + 4, IH - 1)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 2 or h <= 2:
        return
    shape = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shape).polygon([(p[0] - x0, p[1] - y0) for p in poly_px], fill=255)
    shape = Image.composite(shape, Image.new("L", (w, h), 0),
                            LMASK.crop((x0, y0, x1 + 1, y1 + 1)))
    if outline_w:
        edge = shape.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
        target.paste(col + (255,), (x0, y0), edge)
    body = shape.point(lambda v: alpha if v > 0 else 0)
    tile = Image.new("RGBA", (w, h), col + (0,))
    tile.putalpha(body)
    target.alpha_composite(tile, (x0, y0))

# global land mask used for clipping climate regions
LMASK = land_mask()

# ---------------- fonts ----------------
FONT_TITLE = font(os.path.join(FZ, "msyhbd.ttc"), 44)
FONT_CN20  = font(os.path.join(FZ, "simsun.ttc"), 20)
FONT_CN18  = font(os.path.join(FZ, "simsun.ttc"), 18)
FONT_CN17  = font(os.path.join(FZ, "simsun.ttc"), 17)
FONT_LAT26 = font(os.path.join(FZ, "times.ttf"), 26)
FONT_LAT15 = font(os.path.join(FZ, "times.ttf"), 15)
FONT_LAT13 = font(os.path.join(FZ, "times.ttf"), 13)

def wrap_cn(text, n):
    return [text[i:i + n] for i in range(0, len(text), n)] or [""]

def draw_label(d, x, y, text, col, offset):
    f = FONT_CN18
    lines = wrap_cn(text, 11) if len(text) > 11 else [text]
    lh = 23
    wmax = max(d.textlength(s, font=f) for s in lines)
    bw, bh = wmax + 14, lh * len(lines) + 8
    if offset is None:
        bx, by = x - bw / 2, y - bh / 2
    else:
        bx, by = x + 13, y - bh / 2
    bx = min(max(bx, PAD_L + 3), PAD_L + W - bw - 3)
    by = min(max(by, PAD_T + 3), PAD_T + H - bh - 3)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=5,
                        fill=(255, 255, 255, 242), outline=col + (255,), width=2)
    for i, s in enumerate(lines):
        d.text((bx + 7, by + 4 + i * lh), s, font=f, fill=(28, 36, 50))

def render(spec, idx, total):
    col = TYPE_COLOR[spec["color"]]
    img = Image.new("RGB", (IW, IH), (255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")

    # ocean + graticule
    d.rectangle([PAD_L, PAD_T, PAD_L + W, PAD_T + H], fill=C_OCEAN)
    for lon in range(-180, 181, 30):
        x = px(lon, 0)[0]
        d.line([(x, PAD_T), (x, PAD_T + H)], fill=C_GRID, width=1)
    for lat in range(-60, 85, 15):
        y = px(0, lat)[1]
        d.line([(PAD_L, y), (PAD_L + W, y)], fill=C_GRID, width=1)
    for lat, lab in ((0, "赤道 0°"), (23.5, "北回归线 23.5°N"), (-23.5, "南回归线 23.5°S")):
        y = px(0, lat)[1]
        d.line([(PAD_L, y), (PAD_L + W, y)], fill=C_EQ, width=2)
        d.text((PAD_L + 10, y + 4), lab, font=FONT_LAT13, fill=(92, 128, 160))

    # land = pure geographic context
    for c in CO:
        for r in c["px"]:
            d.polygon(r, fill=C_LAND, outline=C_LINE)

    # climate regions, filled and clipped to land
    layer = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer, "RGBA")
    for name, ring in spec["regs"]:
        stamp_region(layer, [px(x, y) for x, y in ring], col, 205, outline_w=3)
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # labels
    for text, anchor, off in spec["labels"]:
        ax, ay = px(*anchor)
        if off is not None:
            lx, ly = px(*off)
            d.line([(ax, ay), (lx, ly)], fill=col + (235,), width=3)
        else:
            lx, ly = ax, ay
        d.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], fill=col, outline=(255, 255, 255), width=2)
        draw_label(d, lx, ly, text, col, off)

    d.rectangle([PAD_L, PAD_T, PAD_L + W, PAD_T + H], outline=(140, 148, 158), width=2)

    # title block
    d.text((PAD_L, 12), spec["key"], font=FONT_TITLE, fill=C_TITLE)
    tw = d.textlength(spec["key"], font=FONT_TITLE)
    d.text((PAD_L + tw + 14, 30), f"{idx} / {total}", font=FONT_LAT26, fill=(160, 170, 182))
    d.text((PAD_L, 62), spec["sub"], font=FONT_CN20, fill=(52, 62, 78))

    # footer
    fy = PAD_T + H + 12
    d.text((PAD_L, fy),
           "底图：Natural Earth 世界国界数据（真实国界）。着色块 = 该气候类型的气候区范围；国界线仅作参照。",
           font=FONT_CN17, fill=(84, 92, 106))
    d.text((PAD_L, fy + 24),
           "气候区范围为依据原课件描述绘制的示意范围，非实测气候区划数据；圆点 = 所标地名位置。",
           font=FONT_CN17, fill=(84, 92, 106))

    path = os.path.join(OUT, spec["fname"])
    img.save(path)
    return path

if __name__ == "__main__":
    problems = []
    for s in FS:
        for name, ring in s["regs"]:
            if len(ring) < 3:
                problems.append(f"{s['key']}: region {name} has <3 points")
        for text, anchor, off in s["labels"]:
            if not on_land(*px(*anchor)):
                problems.append(f"{s['key']}: label '{text}' anchor {anchor} not on land")
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("validation ok: all region rings valid, all label anchors on land")

    total = len(FS)
    for i, spec in enumerate(FS, 1):
        render(spec, i, total)
        print(f"[{i:>2}/{total}] {spec['key']}")
    print("done ->", OUT)
