"""Natural Earth helpers for Contour Notes episodes (pure Python + numpy, no GIS libraries).

    import sys; sys.path.insert(0, "contour/lib"); import ne
    eg = ne.country("Egypt")                      # (geometry, attributes); geometry = ("poly", [rings])
    nile = ne.river_parts(["Nile", "Rosetta Branch"])
    cities = ne.places("Egypt")                   # list of attribute dicts with lon/lat added
    grid = ne.Grid((24.6, 21.9, 37.0, 31.8), 0.01)   # cell centres + true spherical cell areas (km2)
    inside = grid.inside(ring); d = grid.dist_km(polylines)

Files live in contour/data/naturalearth/ (1:50m land, countries, rivers; 1:10m populated places). Areas use a
sphere of R = 6371.0088 km; distances use a local equirectangular projection per segment (fine below ~500 km).
"""
import math, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import shp
R = 6371.0088
NE = pathlib.Path(__file__).resolve().parent.parent / "data" / "naturalearth"
_cache = {}
def layer(name):
    paths = {"countries": "ne_50m_admin_0_countries/ne_50m_admin_0_countries", "rivers": "ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines",
             "land": "ne_50m_land/ne_50m_land", "places": "ne_10m_populated_places_simple/ne_10m_populated_places_simple"}
    if name not in _cache: _cache[name] = shp.layer(NE / paths[name])
    return _cache[name]
def country(name, key="ADMIN"): return next(x for x in layer("countries") if x[1][key] == name)
def river_parts(names, cla="River"):
    return [part for g, a in layer("rivers") if g and a["featurecla"] == cla and a["name"] in names for part in g[1]]
def places(adm0):
    out = []
    for g, a in layer("places"):
        if a["adm0name"] == adm0: d = dict(a); d["lon"], d["lat"] = g[1]; out.append(d)
    return out
def ring_area_km2(ring):           # signed; shapefile outer rings (clockwise) come out negative
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, list(ring[1:]) + [ring[0]]): a += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return a * R * R / 2
def poly_area_km2(rings): return abs(sum(-ring_area_km2(r) for r in rings))
def length_km(pts):
    L = 0.0
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        p1, p2 = math.radians(ay), math.radians(by); dl = math.radians(bx - ax)
        L += 2 * R * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
    return L
def inside(ring, X, Y):
    ring = np.asarray(ring); res = np.zeros(np.shape(X), bool)
    for (a, b), (c, d) in zip(ring[:-1], ring[1:]):
        if b == d: continue
        res ^= ((b > Y) != (d > Y)) & (X < a + (Y - b) * (c - a) / (d - b))
    return res
def dist_km(X, Y, polylines):
    best = np.full(np.shape(X), 1e9)
    for s in polylines:
        for (ax, ay), (bx, by) in zip(s[:-1], s[1:]):
            k = math.cos(math.radians((ay + by) / 2)) * math.radians(1) * R; j = math.radians(1) * R
            px, py = (X - ax) * k, (Y - ay) * j; vx, vy = (bx - ax) * k, (by - ay) * j; L2 = vx * vx + vy * vy or 1e-12
            t = np.clip((px * vx + py * vy) / L2, 0, 1); best = np.minimum(best, np.hypot(px - t * vx, py - t * vy))
    return best
class Grid:
    def __init__(self, bbox, step):
        lon = np.arange(bbox[0], bbox[2], step) + step / 2; lat = np.arange(bbox[1], bbox[3], step) + step / 2
        self.LON, self.LAT = np.meshgrid(lon, lat); self.step = step
        self.area = (R ** 2) * math.radians(step) * (np.sin(np.radians(self.LAT + step / 2)) - np.sin(np.radians(self.LAT - step / 2)))
    def inside(self, ring): return inside(ring, self.LON, self.LAT)
    def dist_km(self, polylines): return dist_km(self.LON, self.LAT, polylines)
def rounded(pts, nd=3): return [[round(x, nd), round(y, nd)] for x, y in pts]
