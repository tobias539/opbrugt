"""Lav læsbare udsnit af et scannet HelloFresh-kort, så teksten kan skrives af.

Brug:  python vaerktoej/udsnit.py <scanning.pdf> <side> <bagside|forside> <udmappe> [--drej 0|90|180|270]

bagside: drejer automatisk siden rigtigt (QR-koden skal sidde nederst til højre) og gemmer
    <side>_venstre_top.png   ingredienser
    <side>_venstre_bund.png  næringsindhold, allergener og ugekode
    <side>_hoejre_top.png    trin 1-3
    <side>_hoejre_bund.png   trin 4-6
forside: gemmer <side>_hoved.png (titel, undertitel, tid) og <side>_hel.png (hele siden, lav opløsning).
         Brug --drej, hvis forsiden ligger forkert.
"""
import io
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image


def hent(pdf, side):
    doc = pymupdf.open(pdf)
    x = doc.extract_image(doc[side - 1].get_images(full=True)[0][0])
    return Image.open(io.BytesIO(x["image"])).convert("RGB")


def er_paa_hovedet(im):
    """QR-boksen er grøn. Sidder den øverst til venstre, ligger kortet på hovedet."""
    w, h = im.size
    def groen(box):
        a = np.asarray(im.crop(box)).astype(int)
        return ((a[:, :, 1] - a[:, :, 0]) > 40).mean()
    return groen((0, 0, int(w * .15), int(h * .15))) > groen((int(w * .85), int(h * .85), w, h))


def gem(im, f, navn, bredde):
    w, h = im.size
    c = im.crop((int(w * f[0]), int(h * f[1]), int(w * f[2]), int(h * f[3])))
    c.resize((bredde, int(bredde * c.height / c.width))).save(navn)
    print(navn)


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        sys.exit(__doc__)
    pdf, side, slags, ud = a[0], int(a[1]), a[2], Path(a[3])
    drej = int(a[a.index("--drej") + 1]) if "--drej" in a else None
    ud.mkdir(parents=True, exist_ok=True)
    im = hent(pdf, side)
    if slags == "bagside":
        if drej is None:
            drej = 180 if er_paa_hovedet(im) else 0
        im = im.rotate(drej, expand=True)
        print(f"drejet {drej} grader")
        gem(im, (0, 0, .27, .55), ud / f"{side}_venstre_top.png", 750)
        gem(im, (0, .45, .27, 1), ud / f"{side}_venstre_bund.png", 750)
        gem(im, (.24, 0, 1, .52), ud / f"{side}_hoejre_top.png", 1600)
        gem(im, (.24, .48, 1, 1), ud / f"{side}_hoejre_bund.png", 1600)
    else:
        im = im.rotate(drej or 0, expand=True)
        gem(im, (0, 0, 1, .22), ud / f"{side}_hoved.png", 1400)
        gem(im, (0, 0, 1, 1), ud / f"{side}_hel.png", 900)


if __name__ == "__main__":
    main()
