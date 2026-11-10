# 世界气候类型分布图集 · World Climate Atlas

**13 张图，认识一个星球的气候 / Thirteen maps, one planet's climates**

<p>
  <img alt="types" src="https://img.shields.io/badge/climate%20types-13-3ba55d">
  <img alt="renderer" src="https://img.shields.io/badge/renderer-Pillow%20only-3776AB">
  <img alt="basemap" src="https://img.shields.io/badge/basemap-Natural%20Earth%20110m-0079C1">
</p>

---

## 这是什么 / What this is

一个专题制图练习：把柯本气候分类的主要气候类型，**一种一张世界地图**。

热带雨林 · 热带稀树草原 · 热带沙漠 · 热带季风 · 地中海 · 亚热带季风 · 亚热带湿润 ·
温带海洋性 · 温带大陆性 · 温带季风 · 亚寒带针叶林 · 极地 · 高原山地

每张图回答三个问题：**分布在哪、为什么在那、典型地名是什么**。

*One world map per Köppen climate type — where it occurs, why there, and the places that best represent it.*

> 仓库只放**生成脚本**；成品图件未公开。
> *Only the rendering scripts are published — the finished maps are not.*

---

## 做法 / How it is made

- **底图**：Natural Earth 110m 国界（真实几何），Pillow 直接栅格化，不依赖 GIS 平台。
- **高亮**：把气候区画成多边形本身（裁剪到陆地），国界保留为上下文——而不是整国填充。
- **标注**：中文地名（撒哈拉沙漠、亚马孙平原、中南半岛……），配合区域范围示意。
- **风格统一**：同一套配色、同一投影范围、同一字号阶梯，13 张图可并排比较。

| 脚本 | 作用 |
| --- | --- |
| `scripts/make_climate_maps.py` | v1：按国家填充高亮 |
| `scripts/make_climate_maps_v2.py` | v2：按气候区多边形填充（当前版本） |
| `scripts/build_map_atlas.py` | 生成总览拼版与 Word 图集（每类一页） |

---

## 运行 / Run

```bash
pip install pillow python-docx
python scripts/make_climate_maps_v2.py   # 输出到 maps/
python scripts/build_map_atlas.py        # 总览拼版 + docx
```

底图请自行下载 Natural Earth 110m 国界 GeoJSON，放到 `data/countries_110m.geojson`。

---

## 诚实说明 / Caveat

> **区域轮廓是基于课程描述整理的示意性范围，不是实测的气候边界数据集。**
> 高亮区只表达「大致在哪里」，不能用于面积统计或边界精度要求高的分析。
> 需要严谨边界时应改用栅格化的 Köppen–Geiger 产品（如 Beck et al., 2018）。

*The highlighted outlines are schematic extents, not a surveyed climate-boundary dataset.
For quantitative work, use a gridded Köppen–Geiger product instead.*

---

## 目录 / Layout

```
scripts/   三个生成脚本（Pillow）
```

底图与产出不随仓库分发。
