"""cn01 data.json from experiments/cn01-egypt/results.json plus verified outside figures (see factcheck.csv)."""
import json, math, pathlib
H = pathlib.Path(__file__).resolve().parent; R = json.loads((H.parent / "experiments/cn01-egypt/results.json").read_text())
cities = R["cities"]; P = R["cities_pop_total"]
COAST = {"Alexandria", "Bur Said", "Ismaïlia", "Suez", "El Arish", "Hurghada", "Matruh", "Bur Safaga", "El Tur", "El Daba", "El Alamein", "Salum", "Berenice"}
OASES = {"El Kharga", "Siwa", "Qasr Farafra", "El Qasr"}
def grp(c):
    if c["dist_km"] <= 10 or c["in_delta"]: return "strip"
    if c["name"] in COAST: return "coast"
    if c["name"] in OASES: return "oases"
    return "edges"                                     # canal-fed land at the valley's edge: Damanhur, Zagazig, El Faiyum
groups = {}
for c in cities: c["group"] = grp(c); groups.setdefault(c["group"], {"n": 0, "pop": 0, "names": []}); g = groups[c["group"]]; g["n"] += 1; g["pop"] += c["pop_max"]; g["names"].append(c["name"])
for g in groups.values(): g["share"] = round(g["pop"] / P, 4)
rain = [4.8, 4.1, 5.7, 1.1, 0.4, 0.0, 0.0, 0.0, 0.1, 0.4, 3.7, 4.5]          # WMO WWIS, Cairo, 1981-2010 (EMA)
off = {"unicef_inhabited_share": 0.077, "unicef_pop_m": 105, "unicef_pop_date": "3 June 2023"}
inh_km2 = off["unicef_inhabited_share"] * R["egypt_area_km2"]
data = {k: R[k] for k in ("egypt_area_km2", "delta_area_km2", "bands", "cities_total", "cities_pop_total", "outline", "nile", "delta_poly", "land", "neighbours", "lake_nasser", "nile_main_km", "branches_km")}
data.update({"cities": cities, "groups": groups, "rain": {"monthly": rain, "total_mm": round(sum(rain), 1)}, "official": off,
             "density_inhabited": round(off["unicef_pop_m"] * 1e6 / inh_km2), "density_all": round(off["unicef_pop_m"] * 1e6 / R["egypt_area_km2"]),
             "band10_square_side_km": round(math.sqrt(next(b for b in R["bands"] if b["km"] == 10)["area_km2"]))})
# rainfall by city, WMO WWIS (Egyptian Meteorological Authority), 1981-2010, sum of monthly means
RAIN = {"Alexandria": [52.9, 40.2, 13.1, 2.6, 1.0, 0, 0, 0, 0.5, 7.8, 27.8, 46.7], "Cairo": rain, "Hurghada": [0.6, 0, 0.3, 0, 0, 0, 0, 0, 0, 0.9, 2.2, 1.5],
        "Luxor": [1.6, 0.1, 0.4, 0.3, 0.8, 0, 0, 0, 0.4, 1.0, 0.5, 0.1], "Aswan": [0.1, 0, 0.1, 0.2, 0.1, 0, 0, 0, 0, 0.6, 0, 0.1]}
data["rain_cities"] = [{"name": k, "total_mm": round(sum(v), 1)} for k, v in RAIN.items()]
# country areas (spherical, Natural Earth 1:50m) and Belgium moved, shape and size kept, onto Egypt for a same-scale comparison
A = json.loads((H.parent / "experiments/cn01-egypt/areas.json").read_text()); data["areas"] = {k: A[k] for k in ("Egypt", "Belgium", "Armenia", "Albania")}
import sys; sys.path.insert(0, str(H.parent / "lib")); import shp
NE = pathlib.Path("contour/data/naturalearth")
bel = next(g for g, a in shp.layer(NE / "ne_50m_admin_0_countries/ne_50m_admin_0_countries") if a["NAME"] == "Belgium")
ring = max(bel[1], key=len); cx = sum(x for x, y in ring) / len(ring); cy = sum(y for x, y in ring) / len(ring); tx, ty = 28.0, 26.2
data["belgium_moved"] = [[round(tx + (x - cx) * math.cos(math.radians(cy)) / math.cos(math.radians(ty + (y - cy))), 3), round(ty + (y - cy), 3)] for x, y in ring]
X = json.loads((H.parent / "experiments/cn01-egypt/extras.json").read_text())
data["cumulative"] = X["cumulative"]; data["cum_at"] = X["cum_at"]; data["coast_lines"] = X["coast_lines"]
data["coast"] = {k: X[k] for k in ("coast_km", "coast10_share", "coast10_km2", "both10_share", "city_pop_strip_or_coast10", "city_pop_coast10_only", "coast_cities")}
sdc = [{"name": c["name"], "lon": c["lon"], "lat": c["lat"], "pop_max": c["pop_max"], "dist_km": c["dist_km"], "in_delta": False} for c in X["sudan_top"]]
data["sudan"] = {"outline": X["sudan_outline"], "nile": X["sudan_rivers"], "cities": sdc, "delta_poly": [], "area_km2": X["sudan_area_km2"],
                 "strip10_share": X["sudan_strip10_share"], "city_pop_strip10": X["sudan_city_pop_strip10"], "city_pop_strip10_no_capital": X["sudan_city_pop_strip10_no_khartoum"], "n_cities": X["sudan_cities"]}
data["inland"] = json.loads((H.parent / "experiments/cn01-egypt/inland.json").read_text())
rest = [c for c in cities if c["name"] not in ("Cairo", "Giza")]
data["egypt_strip10_no_capital"] = round(sum(c["pop_max"] for c in rest if c["dist_km"] <= 10 or c["in_delta"]) / sum(c["pop_max"] for c in rest), 4)
(H / "data.json").write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
print({k: (v["n"], v["share"], v["names"][:6]) for k, v in groups.items()}); print("density", data["density_inhabited"], data["density_all"], "square", data["band10_square_side_km"], "rain", data["rain"]["total_mm"])
