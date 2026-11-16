"""cn01 extras: (1) city population against distance from the river, (2) Egypt's sea coast as a second strip,
(3) the same strip measured for Sudan. Natural Earth only. -> extras.json"""
import json, math, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib")); import ne
HERE = pathlib.Path(__file__).resolve().parent; RES = json.loads((HERE / "results.json").read_text()); out = {}
# (1) cumulative share of the city-list population by distance from the river line (delta interior counts as 0 km)
C = RES["cities"]; P = sum(c["pop_max"] for c in C)
pts = sorted(((0.0 if c["in_delta"] else c["dist_km"]), c["pop_max"], c["name"]) for c in C)
cum, acc = [], 0
for d, p, n in pts: acc += p; cum.append([round(d, 1), round(acc / P, 4), n])
out["cumulative"] = cum
for km in (1, 2, 5, 10, 25, 50, 60, 100, 150, 600): out.setdefault("cum_at", {})[str(km)] = round(sum(p for d, p, n in pts if d <= km) / P, 4)
# (2) the coast: Egypt's outline minus its land borders (vertices shared with a neighbour's outline)
eg_geom, _ = ne.country("Egypt"); ring = np.array(eg_geom[1][0])
nb_pts = np.array([q for g, a in ne.layer("countries") if g and a["ADMIN"] != "Egypt" for r in g[1] for q in r])
near = np.array([np.min(np.hypot(nb_pts[:, 0] - x, nb_pts[:, 1] - y)) < 0.02 for x, y in ring])
coast, cur = [], []
for i, (x, y) in enumerate(ring):
    if not near[i]: cur.append((x, y))
    elif cur: coast.append(cur); cur = []
if cur: coast.append(cur)
coast = [c for c in coast if len(c) > 1]
out["coast_km"] = round(sum(ne.length_km(c) for c in coast)); out["coast_lines"] = [ne.rounded(c) for c in coast]
grid = ne.Grid((24.6, 21.9, 37.0, 31.8), 0.01); IN = grid.inside(ring); total = grid.area[IN].sum()
nile = [np.array(p) for p in RES["nile"]]; delta = np.array(RES["delta_poly"])
D_r = grid.dist_km(nile); DEL = ne.inside(delta, grid.LON, grid.LAT) & IN; D_c = grid.dist_km(coast)
strip = IN & ((D_r <= 10) | DEL); cst = IN & (D_c <= 10)
out["coast10_share"] = round(float(grid.area[cst].sum() / total), 4); out["coast10_km2"] = round(float(grid.area[cst].sum()))
out["both10_share"] = round(float(grid.area[strip | cst].sum() / total), 4)
for c in C: c["coast_km"] = round(float(ne.dist_km(np.array([[c["lon"]]]), np.array([[c["lat"]]]), coast)[0, 0]), 1)
on_strip = lambda c: c["dist_km"] <= 10 or c["in_delta"]
out["city_pop_strip_or_coast10"] = round(sum(c["pop_max"] for c in C if on_strip(c) or c["coast_km"] <= 10) / P, 4)
out["city_pop_coast10_only"] = round(sum(c["pop_max"] for c in C if c["coast_km"] <= 10 and not on_strip(c)) / P, 4)
out["coast_cities"] = sorted([{"name": c["name"], "coast_km": c["coast_km"], "pop_max": c["pop_max"]} for c in C if c["coast_km"] <= 10 and not on_strip(c)], key=lambda c: -c["pop_max"])
# (3) Sudan: the same 10 km strip around the Nile, the White Nile, the Blue Nile and the Atbara
sd_geom, sd_attr = ne.country("Sudan"); sring = np.array(sd_geom[1][0])
riv = [np.array(p) for p in ne.river_parts(["Nile", "El Bahr el Abyad", "El Bahr el Azraq", "Atbara"])]
sg = ne.Grid((21.8, 8.6, 38.7, 22.3), 0.01); SIN = sg.inside(sring); stot = sg.area[SIN].sum(); SD = sg.dist_km(riv)
out["sudan_area_km2"] = round(float(stot)); out["sudan_strip10_share"] = round(float(sg.area[SIN & (SD <= 10)].sum() / stot), 4)
sc = ne.places("Sudan"); SP = sum(c["pop_max"] for c in sc)
for c in sc: c["dist_km"] = round(float(ne.dist_km(np.array([[c["lon"]]]), np.array([[c["lat"]]]), riv)[0, 0]), 1)
out["sudan_cities"] = len(sc); out["sudan_city_pop_strip10"] = round(sum(c["pop_max"] for c in sc if c["dist_km"] <= 10) / SP, 4)
out["sudan_city_pop_strip10_no_khartoum"] = round(sum(c["pop_max"] for c in sc if c["dist_km"] <= 10 and c["name"] not in ("Khartoum", "Omdurman", "Khartoum North")) / sum(c["pop_max"] for c in sc if c["name"] not in ("Khartoum", "Omdurman", "Khartoum North")), 4)
out["sudan_top"] = sorted([{"name": c["name"], "pop_max": c["pop_max"], "dist_km": c["dist_km"], "lon": round(c["lon"], 3), "lat": round(c["lat"], 3)} for c in sc], key=lambda c: -c["pop_max"])
out["sudan_outline"] = ne.rounded(sring[::2]); out["sudan_rivers"] = [ne.rounded(p) for p in riv]
json.dump(out, open(HERE / "extras.json", "w"))
print("cum_at", out["cum_at"]); print("coast", out["coast_km"], "km;", out["coast10_share"], "of land within 10 km of the coast; strip or coast", out["both10_share"])
print("city pop strip or coast10", out["city_pop_strip_or_coast10"], "coast only", out["city_pop_coast10_only"], [(c["name"], c["coast_km"]) for c in out["coast_cities"]])
print("Sudan", out["sudan_area_km2"], "strip10", out["sudan_strip10_share"], "city pop", out["sudan_city_pop_strip10"], "without Khartoum", out["sudan_city_pop_strip10_no_khartoum"])
print([(c["name"], c["dist_km"]) for c in out["sudan_top"][:12]])
