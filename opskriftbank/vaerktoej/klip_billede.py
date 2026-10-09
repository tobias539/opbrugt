"""Klip madbilledet ud af forsiden på et scannet HelloFresh-kort.

Brug:  python vaerktoej/klip_billede.py <scanning.pdf> <side> <opskrift-id>
       (side er 1-baseret; billedet gemmes som billeder/<opskrift-id>.jpg)

Finder det store fotofelt i venstre del af siden ved at lede efter det
længste sammenhængende område, der ikke er hvidt papir.
"""
import io
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

BANK = Path(__file__).resolve().parent.parent


def longest_run(mask):
    best, start = (0, 0), None
    for i, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    return best


def klip(pdf, side, rid):
    doc = pymupdf.open(pdf)
    xref = doc[side - 1].get_images(full=True)[0][0]
    img = Image.open(io.BytesIO(doc.extract_image(xref)["image"])).convert("RGB")
    a = np.asarray(img).astype(np.int16)
    h, w, _ = a.shape
    mx, mn = a.max(2), a.min(2)
    ikke_papir = (mx < 228) | ((mx - mn) > 30)

    rows = ikke_papir[:, int(w * 0.10):int(w * 0.70)].mean(1) > 0.6
    y0, y1 = longest_run(rows)
    # lav tærskel: lyse tallerkener og servietter i fotoet må ikke forveksles med papir
    cols = ikke_papir[y0:y1, :int(w * 0.84)].mean(0) > 0.2
    x0, x1 = longest_run(cols)

    if (x1 - x0) < w * 0.4 or (y1 - y0) < h * 0.4:
        sys.exit(f"Fandt ikke et tydeligt fotofelt på side {side} (fundet {x1-x0}x{y1-y0} px). Klip manuelt.")

    pad = int(w * 0.006)
    ud = BANK / "billeder" / f"{rid}.jpg"
    ud.parent.mkdir(exist_ok=True)
    img.crop((x0 + pad, y0 + pad, x1 - pad, y1 - pad)).save(ud, quality=88)
    print(f"{ud.relative_to(BANK)}  {x1-x0-2*pad}x{y1-y0-2*pad} px  ({(x1-x0)/w:.0%} x {(y1-y0)/h:.0%} af siden)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    klip(sys.argv[1], int(sys.argv[2]), sys.argv[3])
