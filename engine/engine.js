/* Contour Notes: deterministic canvas renderer. renderAt(T) draws the frame for global time T (seconds); the same T always
   gives the same pixels. Episode content comes from window.EP (data.js). Visual system: a night-blue survey sheet with gold
   contour lines, cream type, serif headings (C059), geometric sans labels (URW Gothic). Deliberately unlike Under Test (dark
   terminal panels, Noto Sans) and Earth Worked Out (warm paper, Lato). */
"use strict";
const W = 1920, H = 1080;
const C = { bg: "#14203a", bg2: "#1b2a48", panel: "#1f3052", line: "#2c4068", ink: "#f4ead2", dim: "#a9b3c7", faint: "#5d6c8c",
            gold: "#e8c170", goldDim: "rgba(232,193,112,0.16)", river: "#6fb7d6", land: "#24365a", landHi: "#33497a", green: "#8fd19e",
            red: "#e8775a", sand: "#c9a86a" };
const SERIF = '"C059", "P052", serif', SANS = '"URW Gothic", "Liberation Sans", sans-serif';
let ctx;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const prog = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, x) => a + (b - a) * x;
const fadeIn = (t, at, d = 0.5) => ease(prog(t, at, at + d));
const fmt = (n) => Math.round(n).toLocaleString("en-US");
function font(px, fam, weight) { ctx.font = `${weight || 400} ${px}px ${fam === "serif" ? SERIF : SANS}`; }
function text(s, x, y, o = {}) {
  font(o.px || 40, o.serif ? "serif" : "sans", o.weight || (o.serif ? 700 : 400));
  ctx.fillStyle = o.color || C.ink; ctx.textAlign = o.align || "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(s, x, y);
}
function measure(s, px, serif, weight) { font(px, serif ? "serif" : "sans", weight || (serif ? 700 : 400)); return ctx.measureText(s).width; }
function rect(x, y, w, h, fill, r = 0, stroke = null, lw = 2) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r); if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function sheet(x, y, w, h, label) {           // a survey-sheet panel: darker blue, thin gold frame, corner ticks, a label
  rect(x, y, w, h, C.bg2, 4, "rgba(232,193,112,0.55)", 2);
  ctx.strokeStyle = C.gold; ctx.lineWidth = 3; [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([a, b, sx, sy]) => {
    ctx.beginPath(); ctx.moveTo(a + sx * 26, b); ctx.lineTo(a, b); ctx.lineTo(a, b + sy * 26); ctx.stroke(); });
  if (label) { const lw = measure(label.toUpperCase(), 22, false, 700) + 34; rect(x + 30, y - 17, lw, 34, C.gold, 3); text(label.toUpperCase(), x + 47, y + 8, { px: 22, weight: 700, color: C.bg }); }
}
function line(pts, col, lw = 4, dash) { ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineJoin = "round"; ctx.lineCap = "round"; ctx.setLineDash(dash || []); ctx.beginPath(); pts.forEach(([a, b], i) => i ? ctx.lineTo(a, b) : ctx.moveTo(a, b)); ctx.stroke(); ctx.setLineDash([]); }
function underline(x, y, w, col, g) { ctx.strokeStyle = col; ctx.lineWidth = 5; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + w * g, y); ctx.stroke(); ctx.lineCap = "butt"; }

/* background: contour lines of a smooth made-up terrain, computed once, drifting very slowly */
let bgCache = null;
function background() {
  if (!bgCache) {
    bgCache = document.createElement("canvas"); bgCache.width = W + 200; bgCache.height = H + 200; const c = bgCache.getContext("2d");
    const f = (u, v) => Math.exp(-((u - 0.2) ** 2 + (v - 0.3) ** 2) / 0.05) + 0.7 * Math.exp(-((u - 0.75) ** 2 + (v - 0.7) ** 2) / 0.04) + 0.5 * Math.exp(-((u - 0.55) ** 2 + (v - 0.1) ** 2) / 0.06) + 0.4 * Math.exp(-((u - 0.95) ** 2 + (v - 0.2) ** 2) / 0.03);
    c.fillStyle = C.goldDim;
    for (let px = 0; px < bgCache.width; px += 3) for (let py = 0; py < bgCache.height; py += 3) {
      const v = f(px / bgCache.width, py / bgCache.height) * 9; if (v > 0.4 && Math.abs(v - Math.round(v)) < 0.05) c.fillRect(px, py, 2, 2); }
  }
  return bgCache;
}

/* ---------- map projection: equirectangular around the view's centre latitude ---------- */
function proj(view, box) {           // view = [lon0, lat0, lon1, lat1], box = [x, y, w, h]
  const k = Math.cos(((view[1] + view[3]) / 2) * Math.PI / 180), dx = (view[2] - view[0]) * k, dy = view[3] - view[1];
  const s = Math.min(box[2] / dx, box[3] / dy), cx = box[0] + box[2] / 2, cy = box[1] + box[3] / 2, lc = (view[0] + view[2]) / 2, pc = (view[1] + view[3]) / 2;
  const P = (lon, lat) => [cx + (lon - lc) * k * s, cy - (lat - pc) * s];
  P.pxPerKm = s / 111.32; P.s = s; return P;
}
function lerpView(a, b, x) { return a.map((v, i) => lerp(v, b[i], x)); }
function poly(P, ring, fill, stroke, lw) { ctx.beginPath(); ring.forEach(([x, y], i) => { const [a, b] = P(x, y); i ? ctx.lineTo(a, b) : ctx.moveTo(a, b); }); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 2; ctx.lineJoin = "round"; ctx.stroke(); } }
function pline(P, pts, col, lw, upto) { const n = upto === undefined ? pts.length : Math.max(0, Math.floor(upto * (pts.length - 1)) + 1); if (n < 2) return;
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineJoin = "round"; ctx.lineCap = "round"; ctx.beginPath();
  for (let i = 0; i < n; i++) { const [a, b] = P(pts[i][0], pts[i][1]); i ? ctx.lineTo(a, b) : ctx.moveTo(a, b); } ctx.stroke(); }

/* ---------- generic scenes: draw(t, dur, p), t local to the beat ---------- */
const S = {};
S.title = (t, d, p) => {
  const n = p.title.length, y0 = H / 2 - (n - 1) * 62 - 30;
  p.title.forEach((l, i) => { const a = fadeIn(t, 0.15 + i * 0.45, 0.6); ctx.globalAlpha = a;
    text(l, 170, y0 + i * 124 + (1 - a) * 20, { px: 100, serif: true, color: i === n - 1 ? C.gold : C.ink }); });
  ctx.globalAlpha = 1; underline(174, y0 + (n - 1) * 124 + 36, measure(p.title[n - 1], 100, true), C.gold, ease(prog(t, 0.6 + n * 0.4, 1.6 + n * 0.4)));
  if (p.sub) { ctx.globalAlpha = fadeIn(t, 0.6 + n * 0.45, 0.6); text(p.sub, 174, y0 + n * 124 + 34, { px: 34, color: C.dim }); }
  ctx.globalAlpha = 1;
};
S.statement = (t, d, p) => {
  const n = p.lines.length, step = Math.min(1.6, (d * 0.55) / n), y0 = H / 2 - (n - 1) * 54 - (p.sub ? 30 : 0);
  p.lines.forEach((l, i) => { const a = fadeIn(t, 0.2 + i * step, 0.6), acc = (p.accent || []).includes(i); ctx.globalAlpha = a;
    text(l, W / 2, y0 + i * 108 + (1 - a) * 16, { px: 70, serif: true, align: "center", color: acc ? C.gold : C.ink }); });
  if (p.sub) { ctx.globalAlpha = fadeIn(t, 0.4 + n * step, 0.8); text(p.sub, W / 2, y0 + n * 108 + 30, { px: 32, align: "center", color: C.dim }); }
  ctx.globalAlpha = 1;
};
S.bullets = (t, d, p) => {
  const n = p.items.length, step = (d * 0.72) / (n + 0.6), x = 300, y0 = 320 - (n > 3 ? 40 : 0);
  ctx.globalAlpha = fadeIn(t, 0.1); text(p.head, x, y0, { px: 62, serif: true, color: C.gold });
  p.items.forEach((it, i) => { const a = fadeIn(t, 0.5 + i * step, 0.6), y = y0 + 130 + i * 128; ctx.globalAlpha = a;
    ctx.strokeStyle = C.gold; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x + 26, y - 16, 26, 0, 7); ctx.stroke();
    text(p.numbered ? String(i + 1) : "·", x + 26, y - 4, { px: 32, weight: 700, align: "center", color: C.gold });
    text(it, x + 90 + (1 - a) * 20, y, { px: 46 }); });
  ctx.globalAlpha = 1;
};
S.quote = (t, d, p) => {
  const n = p.lines.length, lh = 74, h = n * lh + 170, x = 220, w = W - 440, y = (H - h) / 2 - 20;
  sheet(x, y, w, h, p.src_short || "source");
  const step = Math.min(1.2, (d * 0.5) / n);
  p.lines.forEach((l, i) => { ctx.globalAlpha = fadeIn(t, 0.3 + i * step, 0.6); const hot = (p.hl || []).includes(i);
    if (hot) { ctx.fillStyle = "rgba(232,193,112,0.22)"; ctx.fillRect(x + 70, y + 72 + i * lh, measure(l, 46, true) + 20, 58); }
    text(l, x + 80, y + 116 + i * lh, { px: 46, serif: true, weight: hot ? 700 : 400 }); });
  ctx.globalAlpha = fadeIn(t, 0.5 + n * step, 0.6); text(p.src, x + 80, y + h - 36, { px: 26, color: C.dim });
  if (p.foot) text(p.foot, W / 2, y + h + 86, { px: 40, align: "center", color: C.gold, weight: 700 });
  ctx.globalAlpha = 1;
};
S.card = (t, d, p) => {
  sheet(360, 260, W - 720, 420, p.label || "the method");
  ctx.globalAlpha = fadeIn(t, 0.3, 0.6); text(p.big, W / 2, 470, { px: 100, serif: true, align: "center" });
  (p.where || []).forEach((w, i) => { ctx.globalAlpha = fadeIn(t, 1.0 + i * 0.6, 0.5); text(w, W / 2, 560 + i * 48, { px: 32, align: "center", color: C.dim }); });
  ctx.globalAlpha = fadeIn(t, d * 0.55, 0.6); if (p.foot) text(p.foot, W / 2, 790, { px: 42, align: "center", weight: 700, color: C.gold }); ctx.globalAlpha = 1;
};
S.endcard = (t, d, p) => {
  text("Contour Notes", 150, 300, { px: 108, serif: true }); underline(154, 334, measure("Contour Notes", 108, true), C.gold, ease(prog(t, 0.3, 1.3)));
  text("Why places are the way they are, drawn from the data.", 154, 400, { px: 38, color: C.gold });
  text(p.next_label || "Next", 154, 560, { px: 30, color: C.dim });
  (p.next || []).forEach((l, i) => text(l, 154, 628 + i * 66, { px: 52, serif: true }));
  text("Data sources and the map code are in the description.", 154, 900, { px: 30, color: C.dim });
  ctx.setLineDash([10, 10]); rect(1220, 170, 560, 315, null, 6, C.faint, 3); ctx.beginPath(); ctx.arc(1500, 790, 170, 0, 7); ctx.strokeStyle = C.faint; ctx.stroke(); ctx.setLineDash([]);
};
S.hbars = (t, d, p) => {
  const R = p.rows, x0 = p.x0 || 640, y0 = p.y0 || 280, lh = p.lh || 104, bw = p.bw || 960, max = p.max;
  text(p.head, 200, y0 - 60, { px: 30, color: C.dim });
  R.forEach((r, i) => { const s = d * (0.06 + i * (p.step || 0.1)), a = fadeIn(t, s, 0.5), g = ease(prog(t, s, s + 0.9)), y = y0 + i * lh; ctx.globalAlpha = a;
    text(r.label, x0 - 30, y + 50, { px: 34, align: "right", weight: 700 }); const len = Math.max(0, (r.value / max) * bw * g);
    rect(x0, y + 12, len, 56, r.col || C.gold, 3); text(r.txt, x0 + len + 20, y + 54, { px: 44, weight: 700, color: r.tcol || C.ink }); });
  ctx.globalAlpha = 1; if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot, 200, y0 + R.length * lh + 40, { px: 30, color: C.dim }); ctx.globalAlpha = 1; }
};
S.table = (t, d, p) => {
  const x0 = p.x0 || 240, y0 = p.y0 || 250, lh = p.lh || 70, cols = p.cols;
  text(p.head, x0, y0 - 56, { px: 30, color: C.dim });
  p.hdr.forEach((h, j) => text(h, x0 + cols[j], y0, { px: 24, weight: 700, color: C.gold, align: j ? "right" : "left" }));
  p.rows.forEach((r, i) => { ctx.globalAlpha = fadeIn(t, d * (0.05 + i * (p.step || 0.05)), 0.4); const y = y0 + 26 + i * lh, hi = (p.hl || []).includes(i);
    rect(x0 - 20, y, cols[cols.length - 1] + 40, lh - 10, hi ? "rgba(232,119,90,0.18)" : C.bg2, 3, C.line, 1);
    r.forEach((c, j) => text(String(c), x0 + cols[j], y + lh / 2 + 6, { px: 32, weight: j === 0 ? 700 : 400, align: j ? "right" : "left", color: hi ? C.red : C.ink })); });
  ctx.globalAlpha = 1; if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot, x0, y0 + 70 + p.rows.length * lh, { px: 28, color: C.dim }); ctx.globalAlpha = 1; }
};
S.splitbar = (t, d, p) => {         // two 100% bars: share of land against share of people
  const x0 = 260, w = 1400; text(p.head, x0, 230, { px: 30, color: C.dim });
  p.bars.forEach((b, i) => { const y = 330 + i * 270, a = fadeIn(t, d * (0.05 + i * 0.3), 0.6); ctx.globalAlpha = a;
    text(b.label, x0, y - 22, { px: 40, serif: true }); let x = x0; rect(x0, y, w, 110, C.land, 3);
    b.parts.forEach((pt, j) => { const g = ease(prog(t, d * (0.12 + i * 0.3 + j * 0.06), d * (0.12 + i * 0.3 + j * 0.06) + 1)), ww = w * pt.share * g;
      rect(x, y, ww, 110, pt.col, 0); if (pt.share > 0.06 && g > 0.9) text(pt.txt, x + ww / 2, y + 70, { px: 36, weight: 700, align: "center", color: C.bg });
      pt._x = x + ww; pt._g = g; x += ww; });
    b.parts.forEach((pt, j) => { if (pt.out && pt.share <= 0.06 && pt._g > 0.9) { const yy = y + 110 + 44; ctx.fillStyle = pt.col; ctx.fillRect(pt._x - 2, y + 110, 3, 16); text(pt.txt, pt._x, yy, { px: 34, weight: 700, color: pt.col, align: "center" }); } }); });
  ctx.globalAlpha = 1; if (p.legend) p.legend.forEach((l, i) => { ctx.globalAlpha = fadeIn(t, d * 0.7, 0.5); rect(x0 + i * 390, 930, 34, 34, l.col, 3); text(l.txt, x0 + 50 + i * 390, 958, { px: 28 }); });
  ctx.globalAlpha = 1;
};
S.rainbars = (t, d, p) => {
  const M = EP.data.rain.monthly, x0 = 300, y0 = 820, w = 1320, h = 480, mx = 8, bw = w / 12;
  text(p.head || "Cairo, average rain each month, 1981–2010 · WMO, Egyptian Meteorological Authority", x0, 220, { px: 30, color: C.dim });
  ctx.fillStyle = C.line; [2, 4, 6, 8].forEach((v) => { ctx.fillRect(x0, y0 - (v / mx) * h, w, 1); text(v + " mm", x0 - 16, y0 - (v / mx) * h + 9, { px: 22, color: C.dim, align: "right" }); });
  M.forEach((v, i) => { const g = ease(prog(t, d * (0.05 + i * 0.03), d * (0.05 + i * 0.03) + 0.6)), bh = (v / mx) * h * g;
    rect(x0 + i * bw + 14, y0 - bh, bw - 28, bh, C.river, 2); text("JFMAMJJASOND"[i], x0 + i * bw + bw / 2, y0 + 40, { px: 28, align: "center", color: C.dim });
    if (g > 0.95) text(v.toFixed(1), x0 + i * bw + bw / 2, y0 - bh - 14, { px: 24, align: "center" }); });
  ctx.fillStyle = C.ink; ctx.fillRect(x0, y0, w, 2);
  ctx.globalAlpha = fadeIn(t, d * 0.55, 0.6); text(p.total || ("a whole year: " + EP.data.rain.total_mm.toFixed(1) + " mm"), x0 + w, 300, { px: 56, serif: true, align: "right", color: C.gold });
  if (p.sub) text(p.sub, x0 + w, 360, { px: 30, align: "right", color: C.dim }); ctx.globalAlpha = 1;
};

/* cumulative share against a distance: p.points = [[x, share, label]], p.xmax, p.marks = [[x, "text"]] */
S.stepcurve = (t, d, p) => {
  const x0 = 260, y0 = 860, w = 1400, h = 560, xm = p.xmax || 150, X = (v) => x0 + (Math.min(v, xm) / xm) * w, Y = (v) => y0 - v * h, pts = p.points;
  text(p.head, x0, 200, { px: 30, color: C.dim });
  ctx.fillStyle = C.line; [0.25, 0.5, 0.75, 1].forEach((v) => { ctx.fillRect(x0, Y(v), w, 1); text(Math.round(v * 100) + "%", x0 - 16, Y(v) + 9, { px: 24, color: C.dim, align: "right" }); });
  for (let v = 0; v <= xm; v += (p.xstep || 25)) text(v + " km", X(v), y0 + 40, { px: 24, color: C.dim, align: "center" });
  ctx.fillStyle = C.ink; ctx.fillRect(x0, y0, w, 2);
  const g = ease(prog(t, d * 0.05, d * 0.7)), xg = xm * g; ctx.strokeStyle = C.gold; ctx.lineWidth = 6; ctx.lineJoin = "round"; ctx.beginPath(); ctx.moveTo(X(0), Y(0)); let last = 0;
  pts.forEach(([x, v]) => { if (x > xg) return; ctx.lineTo(X(x), Y(last)); ctx.lineTo(X(x), Y(v)); last = v; }); ctx.lineTo(X(xg), Y(last)); ctx.stroke();
  (p.marks || []).forEach(([x, s], i) => { if (x > xg) return; const v = pts.filter((q) => q[0] <= x).reduce((m, q) => q[1], 0); ctx.globalAlpha = fadeIn(t, d * 0.05 + (x / xm) * d * 0.65, 0.5);
    ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(X(x), Y(v), 9, 0, 7); ctx.fill(); text(s, X(x) + 16, Y(v) + (i % 2 ? 40 : -16), { px: 30, weight: 700 }); ctx.globalAlpha = 1; });
  if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot, x0, y0 + 100, { px: 28, color: C.dim }); ctx.globalAlpha = 1; }
};

/* ---------- the map ---------- */
S.map = (t, d, p) => {
  const D0 = EP.data, L = p.set ? Object.assign({}, D0, D0[p.set]) : D0, D = L, box = p.box || [140, 130, 1640, 860], z = p.view2 ? ease(prog(t, d * (p.zfrom || 0.1), d * (p.zto || 0.6))) : 0;
  const view = p.view2 ? lerpView(p.view, p.view2, z) : (p.view || [24.0, 21.2, 37.4, 32.2]), P = proj(view, box);
  ctx.save(); ctx.beginPath(); ctx.rect(box[0], box[1], box[2], box[3]); ctx.clip();
  rect(box[0], box[1], box[2], box[3], "#101a30", 0);
  D.land.forEach((r) => poly(P, r, C.land, null)); D.neighbours.forEach((n) => n.rings.forEach((r) => poly(P, r, null, "rgba(169,179,199,0.35)", 1.5)));
  poly(P, D.outline, C.landHi, C.gold, 3);
  if (p.grid) { ctx.strokeStyle = "rgba(232,193,112,0.18)"; ctx.lineWidth = 1; for (let la = 22; la <= 32; la += 2) { const [a, b] = P(view[0], la), [c] = P(view[2], la); ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(c, b); ctx.stroke(); } }
  const nileG = p.draw ? ease(prog(t, d * (p.draw[0] || 0.05), d * (p.draw[1] || 0.5))) : 1;
  if (p.band) {            // the sliver: everything within `band` km of the river, plus the land between the branches
    const g = fadeIn(t, d * (p.bandAt || 0.2), 1.0), km = p.band; ctx.globalAlpha = 0.85 * g;
    if (D.delta_poly && D.delta_poly.length) poly(P, D.delta_poly, C.green, null); D.nile.forEach((s) => pline(P, s, C.green, Math.max(2, 2 * km * P.pxPerKm)));
    ctx.globalAlpha = 1;
  }
  if (p.belgium) { const g = fadeIn(t, d * (p.belgiumAt || 0.4), 0.8); ctx.globalAlpha = g; poly(P, D.belgium_moved, "rgba(232,119,90,0.30)", C.red, 3);
    const bx = D.belgium_moved.reduce((s, q) => s + q[0], 0) / D.belgium_moved.length, by = Math.min(...D.belgium_moved.map((q) => q[1])), [lx, ly] = P(bx, by);
    text("Belgium, same scale", lx, ly + 40, { px: 30, weight: 700, align: "center", color: C.red }); ctx.globalAlpha = 1; }
  if (p.coast) { const g = fadeIn(t, d * (p.coastAt || 0.3), 1.0); ctx.globalAlpha = 0.85 * g; (D.coast_lines || []).forEach((s) => pline(P, s, "#6fb7d6", Math.max(2, 2 * p.coast * P.pxPerKm))); ctx.globalAlpha = 1; }
  if (p.nasser) D.lake_nasser.forEach((s) => pline(P, s, C.river, 7));
  D.nile.forEach((s) => pline(P, s, C.river, p.thin ? 2.5 : 4.5, nileG));
  if (p.cities) {
    const list = D.cities.filter((c) => c.pop_max >= (p.minPop || 0)), cg = fadeIn(t, d * (p.citiesAt || 0.3), 0.8);
    const rad = (c) => Math.max(4, Math.sqrt(c.pop_max) * (p.rk || 0.012) * Math.sqrt(P.s / 120));
    list.forEach((c, i) => { const [x, y] = P(c.lon, c.lat), r = rad(c);
      const near = c.dist_km <= (p.nearKm || 10) || c.in_delta; ctx.globalAlpha = cg * fadeIn(t, d * (p.citiesAt || 0.3) + i * 0.04, 0.4);
      ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = p.colourNear ? (near ? "rgba(232,193,112,0.85)" : "rgba(232,119,90,0.85)") : "rgba(232,193,112,0.85)"; ctx.fill();
      ctx.strokeStyle = C.bg; ctx.lineWidth = 2; ctx.stroke(); });
    (p.labels || []).forEach((nm, i) => { const c = D.cities.find((q) => q.name === nm); if (!c) return; const [x, y] = P(c.lon, c.lat);
      ctx.globalAlpha = fadeIn(t, d * (p.labelsAt || 0.45) + i * 0.15, 0.4); const right = !(p.labelLeft || []).includes(nm);
      const off = rad(c) + 12, NM = { "Bur Said": "Port Said", "Ismaïlia": "Ismailia", "Dumyat": "Damietta", "Rashid": "Rosetta", "Damanhûr": "Damanhur" };
      ctx.save(); ctx.shadowColor = "rgba(8,12,24,0.9)"; ctx.shadowBlur = 8; text(NM[nm] || nm, x + (right ? off : -off), y + 10, { px: 30, weight: 700, align: right ? "left" : "right" }); ctx.restore(); });
    ctx.globalAlpha = 1;
  }
  ctx.restore();
  if (p.scale !== false) { const km = p.scaleKm || 200, L = km * P.pxPerKm, x = box[0] + 40, y = box[1] + box[3] - 40;
    ctx.fillStyle = C.ink; ctx.fillRect(x, y, L, 4); ctx.fillRect(x, y - 10, 3, 14); ctx.fillRect(x + L - 3, y - 10, 3, 14); text(km + " km", x + L / 2, y - 16, { px: 24, align: "center" }); }
  if (p.head) text(p.head, box[0], box[1] - 24, { px: 28, color: C.dim });
  if (p.note) { ctx.globalAlpha = fadeIn(t, d * (p.noteAt || 0.5), 0.6); const lines = p.note, nh = 50 + lines.length * 52, ny = p.notePos === "br" ? box[1] + box[3] - 30 - nh : box[1] + 30;
    rect(box[0] + box[2] - 620, ny, 590, nh, "rgba(20,32,58,0.92)", 4, C.gold, 2);
    lines.forEach((l, i) => text(l, box[0] + box[2] - 590, ny + 62 + i * 52, { px: i === 0 ? 40 : 30, serif: i === 0, color: i === 0 ? C.gold : C.ink })); ctx.globalAlpha = 1; }
  if (p.legend) { const ly = box[1] + box[3] + 22; p.legend.forEach((l, i) => { ctx.globalAlpha = fadeIn(t, d * 0.4, 0.5); rect(box[0] + 10 + i * 460, ly, 28, 28, l.col, 14); text(l.txt, box[0] + 50 + i * 460, ly + 24, { px: 28 }); }); ctx.globalAlpha = 1; }
};

/* ---------- frame ---------- */
function renderAt(T) {
  const tl = EP.timeline.beats; let k = 0;
  while (k < tl.length - 1 && T >= tl[k + 1].start) k++;
  const b = tl[k], beat = EP.storyboard.beats[k], t = Math.max(0, T - b.start), last = k === tl.length - 1, d = last ? (EP.timeline.total - b.start) : b.dur;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const dr = (T * 3) % 200; ctx.drawImage(background(), -dr, -dr * 0.5);
  const g = ctx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1300); g.addColorStop(0, "rgba(20,32,58,0)"); g.addColorStop(1, "rgba(8,12,24,0.55)");
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const edge = Math.min(ease(prog(t, 0, 0.35)), last ? 1 : 1 - ease(prog(t, d - 0.25, d)));
  const z = 1 + 0.01 * prog(t, 0, d) + 0.02 * (1 - edge);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
  S[beat.scene](t, b.speech + 0.01, beat.p || {});
  ctx.restore(); ctx.globalAlpha = 1;
  if (edge < 1) { ctx.globalAlpha = 1 - edge; ctx.fillStyle = C.bg; ctx.fillRect(0, 100, W, H - 112); ctx.globalAlpha = 1; }
  if (beat.chapter) {   // chapter label, top left, like a sheet title
    const fresh = k === 0 || EP.storyboard.beats[k - 1].chapter !== beat.chapter, s1 = fresh ? ease(prog(t, 0.05, 0.6)) : 1;
    const label = beat.chapter.toUpperCase(), w = measure(label, 22, false, 700) + 40; ctx.globalAlpha = s1;
    rect(60 - (1 - s1) * 40, 38, w, 42, null, 3, C.gold, 2); text(label, 80 - (1 - s1) * 40, 67, { px: 22, weight: 700, color: C.gold }); ctx.globalAlpha = 1;
  }
  ctx.fillStyle = C.bg2; ctx.fillRect(0, H - 8, W, 8); ctx.fillStyle = C.gold; ctx.fillRect(0, H - 8, W * (T / EP.timeline.total), 8);
}
function init() { const c = document.getElementById("c"); ctx = c.getContext("2d");
  return Promise.all([document.fonts.load(`700 40px ${SERIF}`), document.fonts.load(`400 40px ${SERIF}`), document.fonts.load(`400 40px ${SANS}`), document.fonts.load(`700 40px ${SANS}`)]).then(() => true); }
function frameJPEG(T, q) { renderAt(T); return document.getElementById("c").toDataURL("image/jpeg", q || 0.93).split(",")[1]; }

/* ---------- vertical Shorts ---------- */
let shortCanvas = null;
function wrapLines(c2, str, maxW) { const words = str.split(" "), lines = []; let cur = "";
  for (const w of words) { const t = cur ? cur + " " + w : w; if (c2.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines; }
function frameShort(T, cfg) {
  renderAt(T);
  if (!shortCanvas) { shortCanvas = document.createElement("canvas"); shortCanvas.width = 1080; shortCanvas.height = 1920; }
  const c2 = shortCanvas.getContext("2d"), SW = 1080, SH = 1920, main = document.getElementById("c");
  c2.fillStyle = C.bg; c2.fillRect(0, 0, SW, SH);
  const sx = cfg.sx, sw = cfg.sw, sy = cfg.sy || 104, sh = cfg.sh || 968, dh = Math.round(sh * SW / sw), dy = 520;
  if (!cfg.tag) { c2.drawImage(main, sx, sy, sw, sh, 0, dy, SW, dh); c2.fillStyle = C.gold; c2.fillRect(0, dy - 3, SW, 3); c2.fillRect(0, dy + dh, SW, 3); }
  c2.textAlign = "center"; c2.textBaseline = "alphabetic";
  cfg.head.forEach((l, i) => { c2.font = `700 74px ${SERIF}`; c2.fillStyle = i === cfg.head.length - 1 ? C.gold : C.ink; c2.fillText(l, SW / 2, 280 + i * 94); });
  if (cfg.tag) { c2.font = `700 100px ${SERIF}`; c2.fillStyle = C.ink; c2.fillText("Contour Notes", SW / 2, 880);
    c2.font = `400 40px ${SANS}`; c2.fillStyle = C.gold; c2.fillText("Why places are the way they are.", SW / 2, 960);
    c2.font = `700 50px ${SANS}`; c2.fillStyle = C.ink; wrapLines(c2, cfg.cap, 900).forEach((l, i) => c2.fillText(l, SW / 2, 1150 + i * 70)); }
  else if (cfg.cap) { c2.font = `700 50px ${SANS}`; const lines = wrapLines(c2, cfg.cap, 920), y0 = dy + dh + 110; lines.forEach((l, i) => { c2.fillStyle = C.ink; c2.fillText(l, SW / 2, y0 + i * 70); }); }
  c2.font = `700 32px ${SANS}`; c2.fillStyle = C.gold; c2.fillText("CONTOUR NOTES", SW / 2, 130);
  return shortCanvas.toDataURL("image/jpeg", 0.93).split(",")[1];
}
function thumbShort(T, cfg, th) {
  frameShort(T, cfg); const c = shortCanvas.getContext("2d"), SW = 1080;
  c.fillStyle = C.bg; c.fillRect(0, 0, SW, 510); c.textAlign = "center";
  c.font = `700 32px ${SANS}`; c.fillStyle = C.gold; c.fillText("CONTOUR NOTES", SW / 2, 110);
  th.big.forEach((l, i) => { let s = 150; c.font = `700 ${s}px ${SERIF}`; while (c.measureText(l).width > 980) { s -= 4; c.font = `700 ${s}px ${SERIF}`; }
    c.fillStyle = i === th.big.length - 1 ? C.gold : C.ink; c.fillText(l, SW / 2, 270 + i * 160); });
  c.font = `700 60px ${SANS}`; c.fillStyle = C.gold; wrapLines(c, th.small, 940).forEach((l, i) => c.fillText(l, SW / 2, 1540 + i * 80));
  return shortCanvas.toDataURL("image/jpeg", 0.92).split(",")[1];
}
