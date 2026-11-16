"""Write cn01/storyboard.json. Numbers come from data.json (the Natural Earth computation) and verified figures."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent; D = json.loads((H / "data.json").read_text())
B = {b["km"]: b for b in D["bands"]}; G = D["groups"]; off = D["official"]
pc = lambda x, nd=0: f"{x * 100:.{nd}f}"
nice = {"Bur Said": "Port Said", "Ismaïlia": "Ismailia", "Damanhûr": "Damanhur", "Dumyat": "Damietta", "Rashid": "Rosetta"}
def nm(n): return nice.get(n, n)
SAY = {"Damanhur": "Daman-hoor", "Zagazig": "Zaga-zeeg", "Faiyum": "Fay-yoom", "Mansura": "Man-soora", "Sohag": "So-haag", "Minya": "Min-ya", "Asyut": "As-yoot", "Qena": "Keena", "Kharga": "Kharga", "Siwa": "See-wa", "Farafra": "Fara-fra"}
OUT = []
def beat(id, chapter, scene, p, text, visual):
    b = {"id": id, "chapter": chapter, "scene": scene, "p": p, "text": text, "visual": visual}
    say = text
    for k, v in SAY.items(): say = say.replace(k, v)
    if say != text: b["say"] = say
    OUT.append(b)
EG = [24.0, 21.2, 37.4, 32.2]
top = ["Cairo", "Alexandria", "Giza", "Luxor", "Aswan", "Asyut", "Bur Said", "Suez"]
s10 = B[10]
beat("b01", "", "map", {"view": EG, "cities": True, "citiesAt": 0.08, "draw": [0.55, 0.9], "labels": ["Cairo", "Alexandria", "Luxor", "Aswan"], "labelsAt": 0.3, "rk": 0.010},
     f"This is Egypt, a little over a million square kilometres. These are its {D['cities_total']} towns and cities in Natural Earth, the free public map data I am using. The dots are sized by population. Now let me add one thing: the river.",
     "Egypt outline; city dots appear; the Nile draws in at the end")
beat("b02", "", "map", {"view": EG, "cities": True, "band": 10, "bandAt": 0.1, "rk": 0.010, "note": [f"{pc(s10['share'], 1)}% of the land", f"{pc(s10['city_pop_share'])}% of the city population"], "noteAt": 0.45},
     f"Most of the people sit on it. Draw a strip ten kilometres either side of the Nile, and add the land between its two branches in the delta. That strip is {pc(s10['share'], 1)} percent of Egypt. It holds {pc(s10['city_pop_share'])} percent of the people in those cities. About three percent of the land, nearly three quarters of the people.",
     "the 10 km strip in green; note card with the two shares")
beat("b03", "", "title", {"title": ["Why most Egyptians live", "on a sliver of the map"], "sub": "measured from Natural Earth's map data, cell by cell"},
     "So why does a country this big live on a line this thin? And who are the people who do not?", "title card")
beat("b04", "In this video", "bullets", {"head": "We will find out", "items": ["How thin the sliver really is", "Why the rest of the map is empty", "Who lives off the line, and why", "What these numbers can and cannot tell you"]},
     "We will measure how thin the sliver really is, see why the rest of the map is empty, find the people who live off the line, and be honest about what these numbers can and cannot tell you.",
     "four bullets")
ch = "1 · The sliver"
beat("b05", ch, "card", {"label": "the method", "big": "1.2 million squares", "where": ["each 0.01 degrees, about one kilometre across", "each with its true area on the curved Earth", "inside Egypt? how far from the river?"], "foot": "then add them up"},
     "Here is how I measured it. I used Natural Earth, a free public map dataset, for Egypt's border, the river and the cities. I covered Egypt with a grid of about one point two million squares, each about a kilometre across, and gave each one its true area on the curved Earth. For every square I asked two questions: is it inside Egypt, and how far is it from the river line? Then I added them up.",
     "method card")
beat("b06", ch, "hbars", {"head": "share of Egypt's land this close to the Nile, plus the land between its branches · computed from Natural Earth",
                         "rows": [{"label": f"{k} km", "value": B[k]["share"] * 100, "txt": f"{pc(B[k]['share'], 1)}%", "col": "#8fd19e" if k == 10 else "#e8c170"} for k in (2, 5, 10, 20, 50)], "max": 12,
                         "foot": f"the 10 km strip: {s10['area_km2']:,} km², a square {D['band10_square_side_km']} km on each side"},
     f"Within two kilometres of the river: {pc(B[2]['share'], 1)} percent of the country. Within five: {pc(B[5]['share'], 1)}. Within ten: {pc(s10['share'], 1)}. Even fifty kilometres either side, a hundred kilometres wide, is only {pc(B[50]['share'])} percent. The ten kilometre strip covers about {round(s10['area_km2'], -3):,} square kilometres, which would fit in a square {D['band10_square_side_km']} kilometres on each side.",
     "bars: share of land by distance")
beat("b06b", ch, "map", {"view": EG, "band": 10, "bandAt": 0.05, "belgium": True, "belgiumAt": 0.25, "scaleKm": 200},
     f"To put that in perspective, here is Belgium, the whole country, moved onto the map at the same scale. By Natural Earth's outlines, Belgium is about {D['areas']['Belgium']:,} square kilometres. The ten kilometre strip along the Nile is a little smaller than that, inside a country {round(D['areas']['Egypt'] / D['areas']['Belgium'])} times Belgium's size.",
     "Belgium outline moved onto Egypt at the same scale, next to the strip")
beat("b07", ch, "map", {"view": EG, "view2": [31.6, 24.9, 33.8, 27.2], "zfrom": 0.1, "zto": 0.55, "band": 10, "bandAt": 0.05, "cities": True, "rk": 0.010, "labels": ["Luxor", "Qena", "Isna"], "labelsAt": 0.6, "scaleKm": 20, "thin": True},
     f"Zoom in on the valley near Luxor and you can see how narrow it is. In this map data the river runs {D['nile_main_km']} kilometres from the Aswan reservoir to Cairo, and then splits into two branches of about {D['branches_km']['Rosetta Branch']} kilometres each down to the sea. The green strip is twenty kilometres wide, and the towns sit inside it like beads on a string.",
     "zoom into the valley near Luxor; 20 km scale bar")
VAL = sorted([c for c in D["cities"] if 23.9 < c["lat"] < 30.0 and c["lon"] > 30.5 and c["dist_km"] <= 10], key=lambda c: c["lat"])
beat("b07b", ch, "table", {"head": "every city in the list between Aswan and Cairo, south to north · distance from the river line", "hdr": ["city", "population", "from the Nile"], "cols": [0, 760, 1380], "lh": 58, "y0": 220,
                           "rows": [[nm(c["name"]), f"{c['pop_max']:,}", f"{c['dist_km']:.1f} km"] for c in VAL], "step": 0.04, "foot": "Natural Earth populated places; distance to the 1:50m river line"},
     f"Walk down the valley and the pattern does not break. Between Aswan and Cairo, Natural Earth lists {len(VAL)} cities, from Aswan and Luxor to Asyut and Beni Suef. Every single one is within {max(c['dist_km'] for c in VAL):.0f} kilometres of the river line. Several are less than a kilometre and a half away. There is no second row of towns further out, because further out there is nothing to live on.",
     "table of the valley cities with their distance from the river")
beat("b08", ch, "quote", {"lines": ["Only 7.7 per cent of Egypt's area is inhabited.", "The majority of Egyptians live either in the Nile Delta", "or in the narrow Nile Valley south of Cairo."], "hl": [0], "src": "UNICEF Egypt, “Country Background”, read 16 November 2026", "src_short": "UNICEF",
                         "foot": f"about {off['unicef_pop_m']} million people, {off['unicef_pop_date']}"},
     f"The official picture agrees. UNICEF puts it plainly: only 7.7 percent of Egypt's area is inhabited, and most Egyptians live in the Nile Delta or in the narrow valley south of Cairo. It counts about {off['unicef_pop_m']} million people in June 2023. That is a different measure from my strip, inhabited land rather than distance from a river, so it comes out a little wider.",
     "UNICEF quote card")
beat("b09", ch, "statement", {"lines": [f"{off['unicef_pop_m']} million people on 7.7% of the land:", f"about {D['density_inhabited']:,} per square kilometre.", f"Spread over all of Egypt: {D['density_all']}."], "accent": [1], "sub": "worked out from UNICEF's figures and the computed area"},
     f"Put those two figures together. {off['unicef_pop_m']} million people on 7.7 percent of the land means about {D['density_inhabited']:,} people per square kilometre where people actually live. Spread over the whole country, it would be just {D['density_all']}.",
     "statement")
ch = "2 · Why the rest is empty"
beat("b10", ch, "rainbars", {"sub": "the Egyptian Meteorological Authority's averages, published by the WMO"},
     f"Why is the rest empty? Start with the sky. Cairo gets about {D['rain']['total_mm']} millimetres of rain in an average year, and almost none of it from May to October. That is far too little to grow crops on rain alone.",
     "Cairo monthly rainfall bars")
rc = {r["name"]: r["total_mm"] for r in D["rain_cities"]}
beat("b10b", ch, "hbars", {"head": "average rain in a whole year, 1981–2010 · WMO, from the Egyptian Meteorological Authority", "x0": 520, "max": 210,
                           "rows": [{"label": k, "value": rc[k], "txt": f"{rc[k]:.1f} mm", "col": "#6fb7d6"} for k in ("Alexandria", "Cairo", "Hurghada", "Luxor", "Aswan")],
                           "foot": "from the Mediterranean coast south to Aswan"},
     f"And Cairo is one of the wetter places. Alexandria, on the Mediterranean, gets about {rc['Alexandria']:.0f} millimetres a year. Cairo, {rc['Cairo']:.0f}. Hurghada on the Red Sea, {rc['Hurghada']:.1f}. Luxor, {rc['Luxor']:.1f}. And Aswan, in the south, about {rc['Aswan']:.1f} millimetres, barely a single wet day.",
     "bars: yearly rain by city, north to south")
beat("b11", ch, "statement", {"lines": ["The rain does not water Egypt.", "The river does,", "and the river's rain falls far to the south."], "accent": [1]},
     f"So the rain does not water Egypt. The river does. The Nile carries water that fell as rain far to the south, in other countries, and carries it north through the desert, {D['nile_main_km']} kilometres from Aswan to Cairo alone. Where that water can reach, people can farm and live. Where it cannot, there is sand and rock.",
     "statement")
beat("b12", ch, "map", {"view": [26.0, 21.0, 36.5, 31.9], "nasser": True, "band": 10, "bandAt": 0.3, "draw": [0.05, 0.6], "cities": True, "minPop": 300000, "rk": 0.010, "labels": ["Aswan", "Cairo"], "labelsAt": 0.5,
                         "legend": [{"col": "#6fb7d6", "txt": "Nile and Lake Nasser"}, {"col": "#8fd19e", "txt": "within 10 km, and the delta"}]},
     "Follow it from the south. The river enters Egypt through Lake Nasser, the reservoir behind the Aswan dam, and from Aswan it runs north through a valley cut into the desert, until it fans out into the delta north of Cairo.",
     "the river drawn south to north, with Lake Nasser")
dl = [c for c in D["cities"] if c["in_delta"]]
beat("b12b", ch, "map", {"view": [29.6, 29.7, 32.6, 31.7], "band": 10, "bandAt": 0.05, "cities": True, "rk": 0.016, "labels": ["Cairo", "Tanta", "El Mansura", "Kafr el Sheikh", "Dumyat", "Rashid", "Alexandria"], "labelLeft": ["Rashid", "Alexandria"], "labelsAt": 0.3, "scaleKm": 50,
                          "note": [f"{D['delta_area_km2']:,} km²", "between the two branches"], "noteAt": 0.6, "notePos": "br"},
     f"North of Cairo the river splits into the Rosetta branch and the Damietta branch, and the land between them is the heart of the delta: about {D['delta_area_km2']:,} square kilometres in this data. Tanta, Kafr el Sheikh and Shibin el Kom sit between the branches; Mansura, Damietta and Rosetta sit on them. Rosetta and Damietta are the towns that gave the two branches their names, near where each one meets the sea.",
     "zoom on the delta, the two branches and their towns")
ch = "3 · Who lives off the line"
st, co, ed, oa = G["strip"], G["coast"], G["edges"], G["oases"]
beat("b13", ch, "map", {"view": EG, "cities": True, "colourNear": True, "band": 10, "bandAt": 0.05, "rk": 0.010, "labels": ["Alexandria", "Ismaïlia", "Suez", "El Faiyum", "Siwa", "El Kharga"], "labelLeft": ["Alexandria", "El Faiyum", "Siwa"], "labelsAt": 0.35,
                         "legend": [{"col": "#e8c170", "txt": "on the strip"}, {"col": "#e8775a", "txt": "off the strip"}]},
     f"Now the exceptions, because more than a quarter of the city population does not live on the strip. In gold, the {st['n']} places on the strip. In red, the {D['cities_total'] - st['n']} that are not. Most of the red population is in a handful of places: Alexandria on the Mediterranean, and Port Said, Ismailia and Suez along the Suez Canal.",
     "cities coloured on or off the strip")
rows = []
for c in D["cities"][:9]:
    where = "between the branches" if c["in_delta"] else f"{c['dist_km']:.0f} km"
    rows.append([nm(c["name"]), f"{c['pop_max']:,}", where])
beat("b14", ch, "table", {"head": "largest places in Natural Earth's list for Egypt · population estimate · distance from the river line", "hdr": ["place", "population", "from the Nile"], "cols": [0, 760, 1380],
                         "rows": rows, "hl": [i for i, c in enumerate(D["cities"][:9]) if not (c["dist_km"] <= 10 or c["in_delta"])], "foot": "Natural Earth populated places, pop_max: metropolitan estimates, not a census"},
     f"Here are the largest places in the list. Cairo is less than a kilometre from the river, Giza six. Alexandria is {D['cities'][1]['dist_km']:.0f} kilometres from the nearest branch, on the sea. Ismailia, Port Said and Suez are on the canal, the country's other great line of trade.",
     "table of the largest places, off-strip rows highlighted")
beat("b15", ch, "splitbar", {"head": "Egypt: share of the land against share of the population in Natural Earth's city list",
                            "bars": [{"label": "land", "parts": [{"share": s10["share"], "col": "#8fd19e", "txt": f"{pc(s10['share'], 1)}%", "out": True}, {"share": 1 - s10["share"], "col": "#2c4068", "txt": ""}]},
                                     {"label": "people in the city list", "parts": [{"share": st["share"], "col": "#8fd19e", "txt": f"{pc(st['share'])}%"}, {"share": co["share"], "col": "#6fb7d6", "txt": f"{pc(co['share'])}%"},
                                                                                     {"share": ed["share"], "col": "#e8c170", "txt": f"{pc(ed['share'])}%", "out": True}, {"share": oa["share"], "col": "#e8775a", "txt": ""}]}],
                            "legend": [{"col": "#8fd19e", "txt": "the 10 km strip"}, {"col": "#6fb7d6", "txt": "sea and canal coasts"}, {"col": "#e8c170", "txt": "valley edges, by canal"}, {"col": "#e8775a", "txt": "desert oases"}]},
     f"Put it together. The strip is {pc(s10['share'], 1)} percent of the land and holds {pc(st['share'])} percent of the people in the city list. The sea and canal coasts add {pc(co['share'])} percent. Another {pc(ed['share'])} percent live just off the strip, in places like Damanhur, Zagazig and El Faiyum, at the valley's edge where canals carry the river's water out. That leaves {pc(oa['share'], 1)} percent for the oases of the Western Desert.",
     "two 100% bars: land and people")
beat("b16", ch, "map", {"view": [24.5, 23.5, 31.5, 30.0], "cities": True, "colourNear": True, "rk": 0.014, "labels": ["Siwa", "El Kharga", "Qasr Farafra", "El Faiyum"], "labelsAt": 0.2, "scaleKm": 100, "band": 10, "bandAt": 0.05},
     f"The oases are real places, but small. In this data, Siwa has about {next(c for c in D['cities'] if c['name'] == 'Siwa')['pop_max']:,} people and El Kharga about {next(c for c in D['cities'] if c['name'] == 'El Kharga')['pop_max']:,}. They live on water from underground, in a desert that covers most of the map: {pc(1 - B[50]['share'])} percent of Egypt is more than fifty kilometres from the river.",
     "the Western Desert and its oases")
ch = "4 · Two lines, and a neighbour"
cum = D["cumulative"]; ca = D["cum_at"]; CO = D["coast"]; SU = D["sudan"]; IL = D["inland"]
alex = next(c for c in D["cities"] if c["name"] == "Alexandria"); isma = next(c for c in D["cities"] if c["name"] == "Ismaïlia")
eg_far = IL["Egypt"]["far_inland_share"]; eg_far_no_isma = eg_far - isma["pop_max"] / D["cities_pop_total"]
beat("c01", ch, "stepcurve", {"head": "Egypt: city-list population living within this distance of the river line (delta interior = 0 km)",
                             "points": [[x, v] for x, v, n in cum], "xmax": 150, "xstep": 25, "marks": [[0.6, "Cairo"], [10, f"10 km: {pc(ca['10'])}%"], [alex["dist_km"], "Alexandria"], [isma["dist_km"], "Ismailia"]],
                             "foot": "Natural Earth populated places, pop_max"},
     f"Here is the same idea as a curve. Start at the river and walk away from it, adding up people as you pass their city. Half of the city-list population is within a kilometre of the water, and Cairo alone does most of that. By ten kilometres it is {pc(ca['10'])} percent. Then almost nothing: between ten and fifty kilometres the line barely moves, to {pc(ca['50'])} percent. At {alex['dist_km']:.0f} kilometres it jumps. That is Alexandria, with Port Said right behind it, and by a hundred kilometres the curve has reached {pc(ca['100'])} percent. The last small steps are Ismailia at {isma['dist_km']:.0f} kilometres, Suez, and the towns of the Red Sea and Sinai coasts. By a hundred and fifty kilometres it is {pc(ca['150'])} percent, and the rest is the oases.",
     "step curve of cumulative city population against distance from the river")
beat("c02", ch, "map", {"view": EG, "band": 10, "bandAt": 0.05, "coast": 10, "coastAt": 0.25, "cities": True, "rk": 0.010, "labels": ["Alexandria", "Bur Said", "Suez", "Hurghada"], "labelLeft": ["Alexandria"], "labelsAt": 0.5,
                        "legend": [{"col": "#8fd19e", "txt": "10 km of the river"}, {"col": "#6fb7d6", "txt": "10 km of the sea"}]},
     f"That jump is Egypt's second line: the sea. Natural Earth's outline gives Egypt about {CO['coast_km']:,} kilometres of coast, on the Mediterranean, the Red Sea and the two gulfs either side of Sinai. Draw the same ten kilometre strip along it and you cover another {pc(CO['coast10_share'], 1)} percent of the country. Alexandria, Port Said, Suez, Hurghada and the smaller towns along the shore all sit inside it.",
     "the river strip in green and the coastal strip in blue")
beat("c03", ch, "statement", {"lines": [f"River and sea together:", f"{pc(CO['both10_share'], 1)}% of the land,", f"{pc(CO['city_pop_strip_or_coast10'])}% of the city population."], "accent": [2], "sub": "Natural Earth outlines and city list, computed"},
     f"Put the two strips together. Ten kilometres of the river or of the sea is {pc(CO['both10_share'], 1)} percent of Egypt's land, and it holds {pc(CO['city_pop_strip_or_coast10'])} percent of the people in the city list. The other {100 - round(CO['city_pop_strip_or_coast10'] * 100)} percent are mostly Ismailia on the Suez Canal, the canal towns at the valley's edge, and the oases.",
     "statement")
beat("c04", ch, "map", {"set": "sudan", "view": [21.5, 8.5, 39.0, 22.5], "band": 10, "bandAt": 0.1, "cities": True, "colourNear": True, "rk": 0.012, "labels": ["Khartoum", "Nyala", "El Fasher", "Al-Ubayyid", "Kassala", "Port Sudan"], "labelLeft": ["Port Sudan"], "labelsAt": 0.4, "scaleKm": 200,
                        "legend": [{"col": "#e8c170", "txt": "within 10 km of a river"}, {"col": "#e8775a", "txt": "further away"}]},
     f"Is this just what rivers do? Try Egypt's southern neighbour, Sudan, with exactly the same method. By Natural Earth's outline, Sudan is about {SU['area_km2'] / 1e6:.2f} million square kilometres, nearly twice the size of Egypt, and the Nile runs through it too. A ten kilometre strip around the Nile, the White Nile, the Blue Nile and the Atbara is {pc(SU['strip10_share'], 1)} percent of Sudan, almost the same as in Egypt, and it holds {pc(SU['city_pop_strip10'])} percent of Sudan's city-list population. But much of that is one place: Khartoum and Omdurman, at the meeting of the White and Blue Nile. Leave the capital out, and only {pc(SU['city_pop_strip10_no_capital'])} percent of the rest live on the strip. Sudan's main port, Port Sudan, is {next(c for c in SU['cities'] if c['name'] == 'Port Sudan')['dist_km']:.0f} kilometres from the nearest river line, on the Red Sea.",
     "Sudan with its rivers, strip and cities coloured near or far")
beat("c05", ch, "hbars", {"head": "city-list population more than 50 km from the river and more than 10 km from the sea · computed", "x0": 560, "max": 25,
                         "rows": [{"label": "Sudan", "value": IL["Sudan"]["far_inland_share"] * 100, "txt": f"{pc(IL['Sudan']['far_inland_share'], 1)}%", "col": "#e8775a"},
                                  {"label": "Egypt", "value": eg_far * 100, "txt": f"{pc(eg_far, 1)}%", "col": "#e8c170"},
                                  {"label": "Egypt without Ismailia", "value": eg_far_no_isma * 100, "txt": f"{pc(eg_far_no_isma, 1)}%", "col": "#8fd19e"}],
                         "foot": "Sudan: Kassala, Al-Ubayyid, Nyala, El Fasher, Gedaref and others · Egypt: Ismailia and the oases"},
     f"The real difference is what lies off the line. In Sudan, about one person in five in the city list lives more than fifty kilometres from the river and more than ten from the sea: in Kassala, Al-Ubayyid, Nyala, El Fasher and Gedaref. Nyala is {next(r for r in IL['Sudan']['far_inland'] if r['name'] == 'Nyala')['river_km']:.0f} kilometres from the nearest river line. In Egypt the same share is {pc(eg_far, 1)} percent, and almost all of it is Ismailia, on the Suez Canal. Leave Ismailia out and it is the oases: {pc(eg_far_no_isma, 1)} percent.",
     "bars: share of city population far from river and sea")
beat("c06", ch, "statement", {"lines": ["Sudan's inland cities live on water", "from somewhere other than the Nile.", "Egypt has almost nowhere like that."], "accent": [2]},
     "So Sudan's inland cities must live on water from somewhere other than the Nile. Egypt, away from its river and its coasts, has almost nowhere like that: a handful of oases, and the canal. That is the sliver. It is not a choice people made once and could easily unmake. It is the only map of water the country has, drawn by one river and two seas.",
     "statement")
ch = "Limits"
beat("b17", ch, "bullets", {"head": "Limits", "numbered": True, "items": [f"Natural Earth lists {D['cities_total']} places, not every village", "Its populations are estimates, not a census", "Distance to a river line is not the same as farmland", "The 1:50m map leaves out small and seasonal rivers"]},
     f"Now the limits, because they matter here. Natural Earth lists {D['cities_total']} places, not every village, so these are shares of the city list, not of every Egyptian. Its population figures are estimates, and some neighbouring cities, like Cairo and Giza, overlap. And a strip around a river line is not the same as farmland: it includes some desert edges and misses some watered land further out. Finally, this is a world map at one to fifty million, so it leaves out small and seasonal rivers. That hardly matters in Egypt, which has one river, but it does matter in Sudan, so read the comparison as a sketch, not a census.",
     "numbered limits")
beat("b18", "Three things", "bullets", {"head": "Three things", "numbered": True, "items": [f"{pc(s10['share'], 1)}% of Egypt lies within 10 km of the Nile or its delta", f"That strip holds {pc(st['share'])}% of the city population", f"River and sea: {pc(D['coast']['both10_share'])}% of the land, {pc(D['coast']['city_pop_strip_or_coast10'])}% of the city population"]},
     f"Three things. {pc(s10['share'], 1)} percent of Egypt lies within ten kilometres of the Nile or between its branches. That strip holds {pc(st['share'])} percent of the people in the city list. And add a strip along the sea, and {pc(D['coast']['both10_share'])} percent of the land holds {pc(D['coast']['city_pop_strip_or_coast10'])} percent of them.",
     "numbered summary")
beat("b19", "", "endcard", {"next_label": "Next on Contour Notes", "next": ["Why Canada lives within", "reach of the US border"]},
     "This is Contour Notes: why places are the way they are, drawn from the data. The map data and the code are linked below. Next time: why Canada lives within reach of the US border.",
     "end card with space for YouTube end-screen elements")
sb = {"episode": "cn01", "title": "Why Most Egyptians Live on a Sliver of the Map", "voice": "bf_emma", "lang": "en-gb", "speed": 0.95, "gap": 0.6, "tail": 11, "beats": OUT}
(H / "storyboard.json").write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(len(OUT), "beats", sum(len(b["text"].split()) for b in OUT), "words")
