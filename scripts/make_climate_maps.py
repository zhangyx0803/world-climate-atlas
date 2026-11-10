# -*- coding: utf-8 -*-
"""
One world map per climate type (13 maps).
Base map  : Natural Earth 110m country boundaries (real geometry).
Highlight : countries in which the climate type occurs, coloured by type.
Labels    : Chinese place names; regional climate sub-zones drawn as polygons.
Renderer  : Pillow only.
"""
import json, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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

F_TITLE = os.path.join(FZ, "msyhbd.ttc")   # 微软雅黑 Bold
F_BOLD  = os.path.join(FZ, "msyhbd.ttc")
F_CN    = os.path.join(FZ, "simsun.ttc")   # 宋体
F_LAT   = os.path.join(FZ, "times.ttf")    # Times New Roman

# ---------------- view window ----------------
LON0, LON1, LAT0, LAT1 = -180.0, 180.0, -58.0, 84.0
SCALE = 10.0                                  # px per degree
W = int(round((LON1 - LON0) * SCALE))
H = int(round((LAT1 - LAT0) * SCALE))
PAD_L, PAD_R, PAD_T, PAD_B = 26, 26, 88, 84
IW, IH = W + PAD_L + PAD_R, H + PAD_T + PAD_B

def px(lon, lat):
    return (PAD_L + (lon - LON0) * SCALE, PAD_T + (LAT1 - lat) * SCALE)

def to_px_ring(ring):
    return [px(x, y) for x, y in ring]

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
    CO.append({
        "name": p.get("ADMIN") or p.get("NAME"),
        "zh":   p.get("NAME_ZH") or p.get("ADMIN"),
        "a3":   p.get("ADM0_A3"),
        "px":   [to_px_ring(r) for r in rings],
    })
A3 = {}
NAME = {}
for c in CO:
    if c["a3"] and c["a3"] != "-99":
        A3[c["a3"]] = c
    NAME[c["name"]] = c
    NAME[c["zh"]] = c

# ---------------- palette ----------------
C_TITLE = (28, 42, 66)
C_OCEAN = (222, 235, 245)
C_LAND  = (233, 231, 224)
C_LINE  = (170, 172, 168)
C_GRAT  = (196, 214, 230)
C_EQ    = (146, 178, 205)

TYPE_COLOR = {
    "热带雨林":     (28, 138, 74),
    "热带稀树草原": (150, 190, 62),
    "热带沙漠":     (224, 168, 46),
    "热带季风":     (18, 158, 140),
    "地中海":       (226, 120, 40),
    "亚热带季风":   (70, 110, 190),
    "亚热带湿润":   (120, 160, 214),
    "温带海洋性":   (46, 106, 166),
    "温带大陆性":   (168, 132, 82),
    "温带季风":     (110, 76, 160),
    "亚寒带针叶林": (40, 96, 126),
    "极地":         (128, 172, 202),
    "高原山地":     (150, 112, 178),
}

def lighten(rgb, f=0.55):
    return tuple(int(v + (255 - v) * f) for v in rgb)

# =====================================================================
# climate-type data
#   countries : ADM0_A3 codes fully belonging to this climate type
#   polys     : regional sub-zones inside a country
#               (a3, [(lon,lat), ...], place name, exists)
#   labels    : (text, anchor lon/lat, label lon/lat or None)
# =====================================================================
FS = [
 dict(key="热带雨林气候", sub="热带 · 全年高温多雨", fname="01_热带雨林气候.png",
   countries=["COD","COG","GAB","GNQ","CMR","CAF","UGA","IDN","MYS","BRN","PNG","BRA","COL","PER","ECU","MDG","GIN","SLE","LBR","CIV","GHA","TGO","NGA","PHL","TLS","AUS"],
   polys=[
     ("BRA", [(-74,-9),(-50,-9),(-50,4),(-74,4)], "亚马孙平原", True),
     ("BRA", [(-56,-25),(-38,-25),(-38,-4),(-56,-4)], "巴西高原东南部", True),
     ("MDG", [(47,-25),(51,-25),(51,-13),(47,-13)], "马达加斯加岛东部", True),
     ("GIN",[(-15,12),(-7,12),(-7,4),(-15,4)], "几内亚湾沿岸", True),
     ("SLE",[(-13.5,10),(-10,10),(-10,6.8),(-13.5,6.8)], "几内亚湾沿岸", False),
     ("LBR",[(-12,8.6),(-7.4,8.6),(-7.4,4.4),(-12,4.4)], "几内亚湾沿岸", False),
     ("CIV",[(-8.7,10.8),(-2.5,10.8),(-2.5,4.3),(-8.7,4.3)], "几内亚湾沿岸", False),
     ("GHA",[(-3.3,11),(-2.5,11),(-2.5,4.7),(-3.3,4.7)], "几内亚湾沿岸", False),
     ("TGO",[(-0.2,11),(1.8,11),(1.8,6.1),(-0.2,6.1)], "几内亚湾沿岸", False),
     ("NGA",[(2.7,14),(14.7,14),(14.7,4.3),(2.7,4.3)], "几内亚湾沿岸", False),
     ("AUS",[(142,-30),(153.6,-30),(153.6,-10),(142,-10)], "澳大利亚东北部", True),
     ("COL",[(-79,12),(-66,12),(-66,0),(-79,0)], "0°—10°N 南美西海岸", True),
     ("ECU",[(-81,2),(-75,2),(-75,-5),(-81,-5)], "0°—10°N 南美西海岸", False),
     ("PER",[(-80,0),(-73,0),(-73,-10),(-80,-10)], "0°—10°N 南美西海岸", False),
     ("MYS",[(99,7),(119,7),(119,0.5),(99,0.5)], "东南亚马来群岛", False),
     ("PHL",[(116,20),(127,20),(127,4),(116,4)], "东南亚马来群岛", False),
   ],
   labels=[("刚果盆地", 20.0, -2.5, None), ("马达加斯加岛东部", 48.5, -19.0, (33.0, -40.0)),
           ("几内亚湾沿岸", -2.0, 7.0, (-24.0, -10.0)), ("亚马孙平原", -62.0, -3.0, None),
           ("巴西高原东南部", -46.0, -18.0, (-36.0, -34.0)),
           ("0°—10°N 南美西海岸", -77.0, 4.0, (-96.0, 14.0)),
           ("东南亚马来群岛", 110.0, -3.0, None), ("新几内亚", 143.0, -6.0, None),
           ("澳大利亚东北部", 147.0, -19.0, (150.0, -38.0))]),

 dict(key="热带稀树草原气候", sub="热带 · 全年高温，明显干湿季", fname="02_热带稀树草原气候.png",
   countries=["SDN","TCD","NER","MLI","BFA","SEN","GMB","GIN","CIV","GHA","TGO","BEN",
              "NGA","CMR","CAF","ETH","KEN","TZA","UGA","RWA","BDI","AGO","ZMB","MWI","MOZ","ZWE",
              "BWA","NAM","ZAF","SOM","MDG","BRA","BOL","PRY","AUS"],
   polys=[
     ("ETH",[(33,15),(48,15),(48,3.5),(33,3.5)], "东非高原", True),
     ("SOM",[(41,12),(51,12),(51,-1),(41,-1)], "东非高原", False),
     ("KEN",[(34,5),(42,5),(42,-4.7),(34,-4.7)], "东非高原", False),
     ("TZA",[(30,-1),(40.5,-1),(40.5,-11.7),(30,-11.7)], "东非高原", False),
     ("UGA",[(29.5,4.2),(35,4.2),(35,-1.5),(29.5,-1.5)], "东非高原", False),
     ("RWA",[(28.8,-1.1),(30.9,-1.1),(30.9,-2.9),(28.8,-2.9)], "东非高原", False),
     ("BDI",[(29,-2.3),(31,-2.3),(31,-4.5),(29,-4.5)], "东非高原", False),
     ("BRA",[(-52,-22),(-40,-22),(-40,-8),(-52,-8)], "巴西高原", True),
     ("AUS",[(122,-26),(146,-26),(146,-10),(122,-10)], "澳大利亚北部", True),
     ("SDN",[(21,22),(38,22),(38,8),(21,8)], "非洲大草原", True),
   ],
   labels=[("非洲大草原", 18.0, 13.0, (-42.0, 6.0)), ("东非高原", 37.0, 2.0, (44.0, -22.0)),
           ("巴西高原", -46.0, -14.0, (-64.0, -24.0)), ("澳大利亚北部", 133.0, -18.0, (136.0, -40.0))]),

 dict(key="热带沙漠气候", sub="热带 · 全年炎热干燥", fname="03_热带沙漠气候.png",
   countries=["EGY","LBY","DZA","TUN","MLI","NER","TCD","SDN","MRT","MAR","SAU","YEM","OMN",
              "ARE","QAT","KWT","IRQ","JOR","NAM","BWA","ZAF","AUS","MEX","USA","CHL","PER"],
   polys=[
     ("USA",[(-124.5,41.5),(-104,41.5),(-104,28),(-124.5,28)], "加利福尼亚寒流沿岸", True),
     ("CHL",[(-76,-17),(-68,-17),(-68,-32),(-76,-32)], "阿塔卡马沙漠", True),
     ("PER",[(-83,-2),(-68,-2),(-68,-19),(-83,-19)], "南美西海岸 30°S—20°S", True),
   ],
   labels=[("撒哈拉沙漠", 13.0, 23.0, None), ("纳米布沙漠", 15.0, -24.0, (16.0, -44.0)),
           ("阿拉伯半岛", 45.0, 22.0, None), ("阿塔卡马沙漠", -70.0, -24.0, (-86.0, -34.0)),
           ("南美西海岸 30°S—20°S", -76.0, -10.0, (-105.0, -6.0)),
           ("加利福尼亚寒流沿岸", -112.0, 34.0, (-134.0, 24.0)),
           ("澳大利亚西部沙漠", 129.0, -25.0, (128.0, -46.0))]),

 dict(key="热带季风气候", sub="热带 · 全年高温，明显旱雨季", fname="04_热带季风气候.png",
   countries=["IND","BGD","LKA","MMR","THA","LAO","KHM","VNM","MYS","CHN"],
   labels=[("南亚印度半岛", 78.0, 20.0, None), ("东南亚中南半岛", 103.0, 15.0, (112.0, 4.0))]),

 dict(key="地中海气候", sub="亚热带 · 夏季高温少雨，冬季温和多雨", fname="05_地中海气候.png",
   countries=["ESP","PRT","ITA","GRC","HRV","BIH","MNE","ALB","MKD","MAR","DZA","TUN","LBY","ZAF",
              "TUR","SYR","LBN","ISR","CHL","USA","AUS","FRA","EGY"],
   polys=[
     ("FRA",[(-2,44),(8,44),(8,43),(-2,43)], "南欧", False),
     ("EGY",[(24,32),(35,32),(35,30.5),(24,30.5)], "北非地中海沿岸", False),
   ],
   labels=[("南欧", 3.0, 41.0, (-24.0, 60.0)), ("北非地中海沿岸", 10.0, 34.0, (-14.0, 50.0)),
           ("南非西南部（好望角）", 20.0, -33.5, (24.0, -50.0)),
           ("南美西海岸 30°S—40°S", -72.0, -35.0, (-96.0, -44.0)),
           ("西亚地中海沿岸", 36.0, 37.0, (44.0, 54.0)),
           ("美国西海岸", -121.0, 37.0, (-140.0, 46.0))]),

 dict(key="亚热带季风气候", sub="亚热带 · 夏季高温多雨，冬季温和少雨", fname="06_亚热带季风气候.png",
   countries=["CHN","JPN","TWN"],
   polys=[("CHN",[(103.5,33.5),(122.5,33.5),(122.5,21),(103.5,21)], "东亚秦岭—淮河以南地区", True)],
   labels=[("东亚秦岭—淮河以南地区", 112.0, 27.0, (120.0, 6.0))]),

 dict(key="亚热带湿润气候", sub="亚热带 · 夏季高温多雨，冬季温和少雨（年较差较小）", fname="07_亚热带湿润气候.png",
   countries=["ARG","URY","AUS","USA","BRA","PRY"],
   polys=[("BRA",[(-58,-34),(-50,-34),(-50,-23),(-58,-23)], "南美拉普拉塔平原", False),
          ("PRY",[(-63,-27),(-54,-27),(-54,-19),(-63,-19)], "南美拉普拉塔平原", False),
          ("AUS",[(140,-39),(154,-39),(154,-28),(140,-28)], "澳大利亚东南部", True),
          ("USA",[(-92,37),(-75,37),(-75,25),(-92,25)], "美国东南部", True)],
   labels=[("南美拉普拉塔平原", -58.0, -32.0, (-46.0, -52.0)),
           ("澳大利亚东南部", 148.0, -33.0, (150.0, -50.0)),
           ("美国东南部", -84.0, 31.0, None)]),

 dict(key="温带海洋性气候", sub="温带 · 全年温和湿润", fname="08_温带海洋性气候.png",
   countries=["GBR","IRL","FRA","BEL","NLD","LUX","DEU","DNK","CHE","AUT","CZE","SVK","POL","NOR","SWE","USA","CAN","NZL","CHL","ARG"],
   polys=[("USA",[(-125,49),(-116,49),(-116,38),(-125,38)], "美国西北沿海", True),
          ("CAN",[(-139,60),(-120,60),(-120,49),(-139,49)], "美国西北沿海", False),
          ("CHL",[(-79,-39),(-71,-39),(-71,-55),(-79,-55)], "南美西海岸 40°S—60°S", True),
          ("ARG",[(-73,-40),(-66,-40),(-66,-55),(-73,-55)], "南美西海岸 40°S—60°S", False)],
   labels=[("西欧", 5.0, 47.0, (-14.0, 58.0)),
           ("南美西海岸 40°S—60°S", -74.0, -47.0, (-100.0, -54.0)),
           ("美国西北沿海", -122.0, 44.0, (-146.0, 40.0))]),

 dict(key="温带大陆性气候", sub="温带 · 夏热冬冷，降水稀少（夏季略多）", fname="09_温带大陆性气候.png",
   countries=["UKR","BLR","RUS","KAZ","UZB","TKM","KGZ","TJK","MNG","CHN","CAN","USA","ARG","CHL"],
   polys=[
     ("ARG",[(-73,-39),(-62,-39),(-62,-55),(-73,-55)], "巴塔哥尼亚高原", True),
     ("CHL",[(-76,-42),(-68,-42),(-68,-55),(-76,-55)], "巴塔哥尼亚高原", False),
     ("USA",[(-103,49),(-80,49),(-80,31),(-103,31)], "北美中部平原", True),
     ("CAN",[(-128,60),(-96,60),(-96,49),(-128,49)], "北美中部平原", True),
     ("RUS",[(40,60),(90,60),(90,50),(40,50)], "东欧", True),
     ("KAZ",[(46,55),(88,55),(88,40),(46,40)], "中亚", True),
   ],
   labels=[("东欧", 38.0, 55.0, (30.0, 68.0)), ("中亚", 66.0, 45.0, (68.0, 32.0)),
           ("北美中部平原", -100.0, 44.0, (-128.0, 28.0)),
           ("巴塔哥尼亚高原", -68.0, -47.0, (-106.0, -48.0))]),

 dict(key="温带季风气候", sub="温带 · 夏季高温多雨，冬季寒冷干燥", fname="10_温带季风气候.png",
   countries=["CHN","PRK","KOR","JPN"],
   polys=[("CHN",[(104,44),(136,44),(136,33),(104,33)], "东亚秦岭—淮河以北地区", True)],
   labels=[("东亚秦岭—淮河以北地区", 116.0, 37.0, (114.0, 60.0))]),

 dict(key="亚寒带针叶林气候", sub="亚寒带 · 冬季漫长严寒，夏季短促温暖", fname="11_亚寒带针叶林气候.png",
   countries=["NOR","SWE","FIN","RUS","CAN","USA"],
   labels=[("欧洲北部（北欧）", 20.0, 65.0, (-30.0, 76.0)), ("北亚（西伯利亚）", 100.0, 62.0, (100.0, 80.0)),
           ("北美洲北部（加拿大）", -100.0, 58.0, (-130.0, 40.0))]),

 dict(key="极地气候", sub="寒带 · 终年严寒、降水稀少、多大风", fname="12_极地气候.png",
   countries=["NOR","RUS","CAN","GRL","USA","ISL"],
   labels=[("北冰洋沿岸", 60.0, 71.0, (26.0, 56.0)), ("北亚北冰洋沿岸", 130.0, 72.0, (118.0, 60.0)),
           ("加拿大北部", -100.0, 72.0, (-120.0, 55.0)),
           ("格陵兰岛（丹麦）", -42.0, 74.0, (-62.0, 60.0))]),

 dict(key="高原山地气候", sub="海拔高 · 热量和水分垂直变化", fname="13_高原山地气候.png",
   countries=["CHN","USA","CAN","NPL","BTN","IND","PAK","KGZ","TJK","AFG","PER","BOL","CHL","ARG",
              "ECU","COL","ETH","KEN","TZA","IRN","ARM","GEO","ITA","CHE","AUT","ESP","FRA","MEX",
              "RUS","MNG","NZL","JPN","TUR"],
   polys=[("CHN",[(73,40),(105,40),(105,26),(73,26)], "青藏高原", True)],
   labels=[("青藏高原", 89.0, 33.0, (96.0, 18.0)),
           ("落基山脉", -114.0, 44.0, (-140.0, 56.0)),
           ("安第斯山脉", -70.0, -20.0, (-88.0, -46.0))]),
]

# attach a palette key to every climate-type spec
for _s in FS:
    _s["color"] = _s["key"].replace("气候", "")
_missing = [(_s["key"], _s["color"]) for _s in FS if _s["color"] not in TYPE_COLOR]
assert not _missing, _missing

# ---------------- geometry clipping ----------------
def point_in_ring(x, y, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside

def clip_ring_to_country(ring, c):
    """Keep only the vertices of `ring` that fall inside the country's polygons."""
    out = []
    for (x, y) in ring:
        for cr in c["px"]:
            if point_in_ring(x, y, cr):
                out.append((x, y))
                break
    return out

def clip_segments_to_country(poly_px, c):
    """Sample the polygon's edges and keep the in-country stretches as line segments."""
    segs = []
    n = len(poly_px)
    for i in range(n):
        p, q = poly_px[i], poly_px[(i + 1) % n]
        L = max(abs(q[0] - p[0]), abs(q[1] - p[1]))
        steps = max(2, int(L / 3))
        run = []
        for s in range(steps + 1):
            t = s / steps
            x = p[0] + (q[0] - p[0]) * t
            y = p[1] + (q[1] - p[1]) * t
            if any(point_in_ring(x, y, cr) for cr in c["px"]):
                run.append((x, y))
            else:
                if len(run) > 1:
                    segs.append(run)
                run = []
        if len(run) > 1:
            segs.append(run)
    return segs

def clip_into(target, poly_px, col, step=14, width=5):
    """Diagonal hatch of `col`, drawn only inside `poly_px` (already clipped)."""
    if len(poly_px) < 3:
        return
    xs = [p[0] for p in poly_px]; ys = [p[1] for p in poly_px]
    x0, y0, x1, y1 = int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 2, int(max(ys)) + 2
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w <= 1 or h <= 1:
        return
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    for k in range(-h, w + h, step):
        td.line([(k, 0), (k + h, h)], fill=col + (175,), width=width)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(p[0] - x0, p[1] - y0) for p in poly_px], fill=255)
    tile.putalpha(Image.composite(tile.getchannel("A"), Image.new("L", (w, h), 0), m))
    target.alpha_composite(tile, (x0, y0))

# ---------------- drawing ----------------
def render(spec, idx, total):
    col = TYPE_COLOR[spec["color"]]
    img = Image.new("RGB", (IW, IH), (255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")

    # ocean
    d.rectangle([PAD_L, PAD_T, PAD_L + W, PAD_T + H], fill=C_OCEAN)
    # graticule
    for lon in range(-180, 181, 30):
        x = px(lon, 0)[0]
        d.line([(x, PAD_T), (x, PAD_T + H)], fill=C_GRAT, width=1)
    for lat in range(-60, 85, 15):
        y = px(0, lat)[1]
        d.line([(PAD_L, y), (PAD_L + W, y)], fill=C_GRAT, width=1)
    # equator + tropics
    for lat, lab in ((0, "赤道 0°"), (23.5, "北回归线 23.5°N"), (-23.5, "南回归线 23.5°S")):
        y = px(0, lat)[1]
        d.line([(PAD_L, y), (PAD_L + W, y)], fill=C_EQ, width=2)
        d.text((PAD_L + 10, y + 4), lab, font=FONT_LAT13, fill=(96, 132, 164))

    # base land
    for c in CO:
        for r in c["px"]:
            d.polygon(r, fill=C_LAND, outline=C_LINE)

    # highlighted countries (climate type occurs here)
    hi = set(spec["countries"])
    fill_c = lighten(col, 0.45)
    for a3 in hi:
        c = A3.get(a3)
        if not c:
            continue
        for r in c["px"]:
            d.polygon(r, fill=fill_c + (255,), outline=col)

    # regional sub-zones: hatch + outline, CLIPPED to the country's real borders
    overlay = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
    for a3, ring, _place, _ex in spec.get("polys", []):
        c = A3.get(a3)
        if not c:
            continue
        poly = [px(x, y) for x, y in ring]
        clipped = clip_ring_to_country(poly, c)
        if len(clipped) >= 3:
            clip_into(overlay, clipped, col)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for a3, ring, _place, _ex in spec.get("polys", []):
        c = A3.get(a3)
        if not c:
            continue
        poly = [px(x, y) for x, y in ring]
        clipped = clip_ring_to_country(poly, c)
        if len(clipped) >= 3:
            d.polygon(clipped, outline=col + (255,), width=3)
            continue
        # rectangle sits entirely inside the country: draw its border instead
        segs = clip_segments_to_country(poly, c)
        for s in segs:
            if len(s) >= 2:
                d.line(s, fill=col + (255,), width=3)

    # labels
    for text, alon, alat, llab in spec.get("labels", []):
        ax, ay = px(alon, alat)
        if llab is not None:
            lx, ly = px(llab[0], llab[1])
            d.line([(ax, ay), (lx, ly)], fill=col + (235,), width=3)
            d.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], fill=col, outline=(255, 255, 255), width=2)
        else:
            lx, ly = ax, ay
            d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=col, outline=(255, 255, 255), width=2)
        draw_label(d, lx, ly, text, col, llab is not None)

    # frame
    d.rectangle([PAD_L, PAD_T, PAD_L + W, PAD_T + H], outline=(140, 148, 158), width=2)

    # title
    d.text((PAD_L, 14), spec["key"], font=FONT_TITLE, fill=C_TITLE)
    tw = d.textlength(spec["key"], font=FONT_TITLE)
    d.text((PAD_L + tw + 14, 34), f"{idx} / {total}", font=FONT_LAT28, fill=(158, 168, 180))
    d.text((PAD_L, 64), spec["sub"], font=FONT_CN20, fill=(52, 62, 78))
    d.text((PAD_L + tw + 122, 64), f"共 {len(spec['countries'])} 个国家／地区",
           font=FONT_CN20, fill=(120, 132, 148))

    # footer note
    fy = PAD_T + H + 14
    d.text((PAD_L, fy),
           "底图：Natural Earth 世界国界数据（真实国界）。浅色国家 = 该气候类型在此国出现；斜纹区 = 该国内部的典型分布地段；圆点 = 所标地名位置。",
           font=FONT_CN18, fill=(84, 92, 106))
    d.text((PAD_L, fy + 26),
           "同一国家可属多种气候（如巴西兼有热带雨林、热带稀树草原、亚热带湿润气候），故各国会在多张图中重复出现。",
           font=FONT_CN18, fill=(84, 92, 106))

    path = os.path.join(OUT, spec["fname"])
    img.save(path)
    return path

def wrap_cn(text, n):
    return [text[i:i + n] for i in range(0, len(text), n)] or [""]

def draw_label(d, x, y, text, col, outside):
    f = FONT_CN20
    lines = wrap_cn(text, 10) if len(text) > 10 else [text]
    lh = 25
    wmax = max(d.textlength(s, font=f) for s in lines)
    bw, bh = wmax + 14, lh * len(lines) + 8
    if outside:
        bx, by = x + 12, y - bh / 2
    else:
        bx, by = x - bw / 2, y - bh / 2
    bx = min(max(bx, PAD_L + 4), PAD_L + W - bw - 4)
    by = min(max(by, PAD_T + 4), PAD_T + H - bh - 4)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=5,
                        fill=(255, 255, 255, 238), outline=col + (255,), width=2)
    for i, s in enumerate(lines):
        d.text((bx + 7, by + 4 + i * lh), s, font=f, fill=(30, 38, 52))

FONT_TITLE = font(F_TITLE, 44)
FONT_CN22  = font(F_CN, 22)
FONT_CN20  = font(F_CN, 20)
FONT_CN21  = font(F_CN, 21)
FONT_CN19  = font(F_CN, 19)
FONT_CN18  = font(F_CN, 18)
FONT_LAT28 = font(F_LAT, 28)
FONT_LAT13 = font(F_LAT, 13)
FONT_LAT14 = font(F_LAT, 14)

if __name__ == "__main__":
    # ---- validate all referenced country codes exist ----
    problems = []
    for s in FS:
        for a3 in s["countries"]:
            if a3 not in A3:
                problems.append(f"{s['key']}: unknown country code {a3}")
        for a3, _ring, _pl, _ex in s.get("polys", []):
            if a3 not in A3:
                problems.append(f"{s['key']}: sub-zone on unknown country {a3}")
            elif a3 not in s["countries"]:
                problems.append(f"{s['key']}: sub-zone {a3} not in countries list "
                                f"(would render unhighlighted)")
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("validation ok: all country codes resolved")

    total = len(FS)
    for i, spec in enumerate(FS, 1):
        p = render(spec, i, total)
        print(f"[{i:>2}/{total}] {spec['key']:<18} -> {os.path.basename(p)}")
    print("done. images in", OUT)
