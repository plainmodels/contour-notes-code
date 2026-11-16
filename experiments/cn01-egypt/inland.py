"""cn01: share of each country's city-list population that is inland and far from the river (> 50 km from the river
line and > 10 km from the sea coast). Coast = the country's outline minus vertices shared with a neighbour. -> inland.json"""
import json, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib")); import ne
HERE = pathlib.Path(__file__).resolve().parent
def coast_of(name):
    g, _ = ne.country(name); ring = np.array(max(g[1], key=len))
    nb = np.array([q for gg, a in ne.layer("countries") if gg and a["ADMIN"] != name for r in gg[1] for q in r])
    near = [np.min(np.hypot(nb[:, 0] - x, nb[:, 1] - y)) < 0.02 for x, y in ring]; out, cur = [], []
    for i, (x, y) in enumerate(ring):
        if not near[i]: cur.append((x, y))
        elif cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return [c for c in out if len(c) > 1]
res = {}
for name, rivers in (("Egypt", ["Nile", "Rosetta Branch", "Damietta Branch"]), ("Sudan", ["Nile", "El Bahr el Abyad", "El Bahr el Azraq", "Atbara"])):
    riv = [p for p in ne.river_parts(rivers) if not (name == "Egypt" and max(q[1] for q in p) < 22.5)]; co = coast_of(name); cs = ne.places(name); P = sum(c["pop_max"] for c in cs)
    rows = []
    for c in cs:
        X, Y = np.array([[c["lon"]]]), np.array([[c["lat"]]])
        rows.append({"name": c["name"], "pop_max": c["pop_max"], "river_km": round(float(ne.dist_km(X, Y, riv)[0, 0]), 1), "coast_km": round(float(ne.dist_km(X, Y, co)[0, 0]), 1)})
    far = [r for r in rows if r["river_km"] > 50 and r["coast_km"] > 10]
    res[name] = {"far_inland_share": round(sum(r["pop_max"] for r in far) / P, 4), "far_inland": sorted(far, key=lambda r: -r["pop_max"])}
    print(name, res[name]["far_inland_share"], [(r["name"], r["pop_max"], r["river_km"]) for r in res[name]["far_inland"][:8]])
json.dump(res, open(HERE / "inland.json", "w"))
