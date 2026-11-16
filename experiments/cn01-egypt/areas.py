"""Spherical areas of every Natural Earth 1:50m country (R = 6371.0088 km), to compare the Nile strip with whole countries.
Ring area by the Chamberlain-Duquette formula; holes come out with the opposite sign and subtract. -> areas.json"""
import json, math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib")); import shp
R = 6371.0088; NE = pathlib.Path("contour/data/naturalearth")
def ring_area(r):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        a += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return a * R * R / 2
out = {}
for g, at in shp.layer(NE / "ne_50m_admin_0_countries/ne_50m_admin_0_countries"):
    if not g: continue
    out[at["NAME"]] = round(abs(sum(-ring_area(r) for r in g[1])))           # shapefile outer rings run clockwise
json.dump(out, open(pathlib.Path(__file__).parent / "areas.json", "w"), indent=0)
strip = json.load(open(pathlib.Path(__file__).parent / "results.json"))["bands"][2]["area_km2"]
print("Egypt", out["Egypt"], "strip", strip)
for k, v in sorted(out.items(), key=lambda kv: abs(kv[1] - strip))[:8]: print(k, v)
