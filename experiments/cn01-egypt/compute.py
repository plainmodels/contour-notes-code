"""cn01: how much of Egypt lies near the Nile, and how many of its cities do. Natural Earth only. -> results.json

Grid: 0.01 degree cells over Egypt's bounding box; each cell's true area on a sphere (R = 6371.0088 km):
  R^2 * dlon * (sin lat2 - sin lat1). Inside-Egypt test: ray casting against the Natural Earth 1:50m polygon.
River: Natural Earth 1:50m 'Nile' river line north of Aswan plus the 'Rosetta Branch' and 'Damietta Branch'
(Lake Nasser's centre line is left out: a reservoir, not a farmed valley). Distance: local equirectangular
projection around each segment (error well under 1% at these distances).
Delta: the land between the two branches and the sea, closed by Natural Earth's own coastline of Egypt.
Cities: Natural Earth 1:10m populated places in Egypt, pop_max (metropolitan estimate), not a census.
"""
import json, math, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib")); import shp
NE = pathlib.Path("contour/data/naturalearth"); R = 6371.0088
countries = shp.layer(NE / "ne_50m_admin_0_countries/ne_50m_admin_0_countries")
eg_geom, eg_attr = next(x for x in countries if x[1]["ADMIN"] == "Egypt"); ring = np.array(eg_geom[1][0])
rivers = shp.layer(NE / "ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines")
lines = {}
for g, a in rivers:
    if a["featurecla"] == "River" and a["name"] in ("Nile", "Rosetta Branch", "Damietta Branch"):
        for part in g[1]:
            if a["name"] == "Nile" and max(p[1] for p in part) < 22.5: continue      # Sudan reach, south of Lake Nasser
            lines.setdefault(a["name"], []).append(part)
nile = [np.array(p) for k in lines for p in lines[k]]
step = 0.01; lon = np.arange(24.6, 37.0, step) + step / 2; lat = np.arange(21.9, 31.8, step) + step / 2
LON, LAT = np.meshgrid(lon, lat)
cell = (R ** 2) * math.radians(step) * (np.sin(np.radians(LAT + step / 2)) - np.sin(np.radians(LAT - step / 2)))
def inside(poly, X, Y):
    res = np.zeros(X.shape, bool); x0, y0 = poly[:-1, 0], poly[:-1, 1]; x1, y1 = poly[1:, 0], poly[1:, 1]
    for a, b, c, d in zip(x0, y0, x1, y1):
        if b == d: continue
        m = ((b > Y) != (d > Y)); xi = a + (Y - b) * (c - a) / (d - b); res ^= m & (X < xi)
    return res
IN = inside(ring, LON, LAT)
def dist_km(X, Y, segs):
    best = np.full(X.shape, 1e9)
    for s in segs:
        for (ax, ay), (bx, by) in zip(s[:-1], s[1:]):
            k = math.cos(math.radians((ay + by) / 2)) * math.radians(1) * R; j = math.radians(1) * R
            px, py = (X - ax) * k, (Y - ay) * j; vx, vy = (bx - ax) * k, (by - ay) * j; L2 = vx * vx + vy * vy
            t = np.clip((px * vx + py * vy) / L2, 0, 1); best = np.minimum(best, np.hypot(px - t * vx, py - t * vy))
    return best
D = dist_km(LON, LAT, nile)
# delta polygon: Rosetta branch (Cairo->sea) + Egypt's coast from the Rosetta mouth east to the Damietta mouth + Damietta branch back to Cairo
ros = np.array(lines["Rosetta Branch"][0]); dam = np.array(lines["Damietta Branch"][0])
def nearest(pt): return int(np.argmin(((ring[:, 0] - pt[0]) ** 2 + (ring[:, 1] - pt[1]) ** 2)))
i0, i1 = nearest(ros[-1]), nearest(dam[-1])
coast = ring[i0:i1 + 1] if i0 < i1 else ring[i1:i0 + 1][::-1]
delta = np.vstack([ros, coast, dam[::-1], ros[:1]]); DEL = inside(delta, LON, LAT) & IN
total = float(cell[IN].sum()); res = {"egypt_area_km2": round(total), "egypt_area_ne_note": "Natural Earth 1:50m polygon, spherical cell areas",
       "delta_area_km2": round(float(cell[DEL].sum())), "bands": []}
for km in (2, 5, 10, 20, 50):
    band = IN & ((D <= km) | DEL); res["bands"].append({"km": km, "area_km2": round(float(cell[band].sum())), "share": round(float(cell[band].sum()) / total, 4),
                                                       "area_no_delta_km2": round(float(cell[IN & (D <= km)].sum()))})
places = shp.layer(NE / "ne_10m_populated_places_simple/ne_10m_populated_places_simple")
cities = []
for g, a in places:
    if a["adm0name"] != "Egypt": continue
    x, y = g[1]; d = float(dist_km(np.array([[x]]), np.array([[y]]), nile)[0, 0]); dl = bool(inside(delta, np.array([[x]]), np.array([[y]]))[0, 0])
    cities.append({"name": a["name"], "lon": round(x, 3), "lat": round(y, 3), "pop_max": int(a["pop_max"]), "dist_km": round(d, 1), "in_delta": dl})
cities.sort(key=lambda c: -c["pop_max"]); P = sum(c["pop_max"] for c in cities)
for b in res["bands"]:
    near = [c for c in cities if c["dist_km"] <= b["km"] or c["in_delta"]]
    b["cities"] = len(near); b["city_pop"] = sum(c["pop_max"] for c in near); b["city_pop_share"] = round(b["city_pop"] / P, 4)
res.update({"cities": cities, "cities_total": len(cities), "cities_pop_total": P, "ne_pop_est": eg_attr["POP_EST"], "ne_pop_year": eg_attr["POP_YEAR"],
            "outline": [[round(x, 3), round(y, 3)] for x, y in ring[::1]], "nile": [[[round(x, 3), round(y, 3)] for x, y in p] for p in nile],
            "delta_poly": [[round(x, 3), round(y, 3)] for x, y in delta]})
# a coarse mask for the map: which 0.1-degree cells are within 10 km of the river or in the delta (drawn as the 'sliver')
m = IN & ((D <= 10) | DEL); co = m.reshape(m.shape[0] // 10, 10, m.shape[1] // 10, 10).mean(axis=(1, 3)) if m.shape[0] % 10 == 0 and m.shape[1] % 10 == 0 else None
json.dump(res, open(pathlib.Path(__file__).parent / "results.json", "w"))
print("Egypt", res["egypt_area_km2"], "km2; delta", res["delta_area_km2"])
for b in res["bands"]: print(f"{b['km']:>3} km: {b['share']*100:5.2f}% of area ({b['area_km2']} km2), cities {b['cities']}/{len(cities)}, city pop {b['city_pop_share']*100:.1f}%")
print("NE city pop", P, "NE POP_EST", eg_attr["POP_EST"], eg_attr["POP_YEAR"]); print([ (c['name'], c['pop_max'], c['dist_km'], c['in_delta']) for c in cities[:12]])

# ---- extras for the video: river length, map layers around Egypt ----
def length_km(p):
    L = 0.0
    for (ax, ay), (bx, by) in zip(p[:-1], p[1:]):
        p1, p2 = math.radians(ay), math.radians(by); dl = math.radians(bx - ax)
        L += 2 * R * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
    return L
res["nile_main_km"] = round(sum(length_km(p) for p in lines["Nile"]))          # Aswan reservoir outlet to the delta head, Natural Earth line
res["branches_km"] = {k: round(sum(length_km(p) for p in lines[k])) for k in ("Rosetta Branch", "Damietta Branch")}
BB = (18.0, 15.0, 42.0, 36.0)
def in_bb(parts): return any(BB[0] <= x <= BB[2] and BB[1] <= y <= BB[3] for part in parts for x, y in part)
land = shp.layer(NE / "ne_50m_land/ne_50m_land")
res["land"] = [[[round(x, 2), round(y, 2)] for x, y in part[::2]] for g, a in land if g and in_bb(g[1]) for part in g[1] if len(part) > 8]
res["neighbours"] = [{"name": a["NAME"], "rings": [[[round(x, 2), round(y, 2)] for x, y in part] for part in g[1]]} for g, a in countries
                     if a["ADMIN"] != "Egypt" and g and in_bb(g[1]) and a["NAME"] in ("Libya", "Sudan", "Israel", "Jordan", "Saudi Arabia", "Palestine", "Chad", "S. Sudan", "Eritrea", "Ethiopia")]
res["lake_nasser"] = [[[round(x, 3), round(y, 3)] for x, y in part] for g, a in rivers if a["featurecla"] == "Lake Centerline" and a["name"] == "Nile" for part in g[1]]
json.dump(res, open(pathlib.Path(__file__).parent / "results.json", "w"))
print("Nile main", res["nile_main_km"], "km; branches", res["branches_km"], "; land rings", len(res["land"]), "; neighbours", [n["name"] for n in res["neighbours"]])
