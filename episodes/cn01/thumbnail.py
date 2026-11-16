"""Draw the cn01 thumbnail (1280x720) with the channel engine: the real Egypt map with the 10 km strip, plus two lines of type."""
import base64, pathlib, sys
sys.path.insert(0, "youtube/pipeline")
from playwright.sync_api import sync_playwright
import render
ep = pathlib.Path(__file__).resolve().parent
JS = r"""() => {
  const big = document.createElement('canvas'); big.width = W; big.height = H; const keep = ctx; ctx = big.getContext('2d');
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); ctx.drawImage(background(), 0, 0);
  S.map(99, 1, { view: [24.0, 21.4, 37.0, 32.0], box: [0, 0, 1200, H], band: 10, bandAt: 0, cities: true, citiesAt: 0, rk: 0.011, scale: false });
  text('3%', 1240, 400, { px: 300, serif: true, color: C.green });
  text('OF EGYPT', 1250, 520, { px: 92, serif: true, color: C.ink });
  text('73% of the', 1250, 650, { px: 84, serif: true, color: C.gold }); text('city population', 1250, 750, { px: 76, serif: true, color: C.gold });
  ctx = keep; const c = document.createElement('canvas'); c.width = 1280; c.height = 720; c.getContext('2d').drawImage(big, 0, 0, 1280, 720);
  return c.toDataURL('image/png').split(',')[1]; }"""
with sync_playwright() as pw:
    b, p = render.open_page(pw, render.write_page(ep))
    (ep / "publish").mkdir(exist_ok=True); out = ep / "publish" / "thumbnail.png"; out.write_bytes(base64.b64decode(p.evaluate(JS))); b.close()
print("wrote", out)
