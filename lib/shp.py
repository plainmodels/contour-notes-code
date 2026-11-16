"""Minimal pure-Python reader for ESRI shapefiles (.shp points/polylines/polygons) and dBASE (.dbf) attribute tables."""
import struct, pathlib

def read_dbf(path):
    b = pathlib.Path(path).read_bytes()
    n, hlen, rlen = struct.unpack("<IHH", b[4:12])
    fields, off = [], 32
    while b[off] != 0x0D:
        name = b[off:off + 11].split(b"\0")[0].decode("latin1"); typ = chr(b[off + 11]); ln = b[off + 16]; dec = b[off + 17]
        fields.append((name, typ, ln, dec)); off += 32
    rows = []
    for i in range(n):
        r = b[hlen + i * rlen: hlen + (i + 1) * rlen]
        if r[:1] == b"*": rows.append(None); continue
        p, row = 1, {}
        for name, typ, ln, dec in fields:
            raw = r[p:p + ln]; p += ln
            s = raw.decode("utf-8", "replace").replace("\x00", "").strip()
            if typ in "NF":
                try: row[name] = float(s) if (dec or "." in s or "e" in s.lower()) else int(s)
                except ValueError: row[name] = None
            else: row[name] = s
        rows.append(row)
    return rows

def read_shp(path):
    b = pathlib.Path(path).read_bytes(); off, out = 100, []
    while off < len(b):
        _, clen = struct.unpack(">II", b[off:off + 8]); off += 8; rec = b[off:off + clen * 2]; off += clen * 2
        st = struct.unpack("<i", rec[:4])[0]
        if st == 0: out.append(None)
        elif st == 1: out.append(("point", struct.unpack("<2d", rec[4:20])))
        elif st in (3, 5):
            nparts, npts = struct.unpack("<2i", rec[36:44]); parts = list(struct.unpack(f"<{nparts}i", rec[44:44 + 4 * nparts]))
            pts = struct.unpack(f"<{2 * npts}d", rec[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts])
            xy = [(pts[2 * i], pts[2 * i + 1]) for i in range(npts)]; parts.append(npts)
            out.append(("line" if st == 3 else "poly", [xy[parts[k]:parts[k + 1]] for k in range(nparts)]))
        else: raise ValueError(f"shape type {st}")
    return out

def layer(stem):
    return list(zip(read_shp(str(stem) + ".shp"), read_dbf(str(stem) + ".dbf")))
