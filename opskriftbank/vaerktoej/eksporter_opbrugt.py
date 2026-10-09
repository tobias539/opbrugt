"""Eksportér opskriftbanken til Opbrugt-appen.

Brug:  python vaerktoej/byg.py && python vaerktoej/eksporter_opbrugt.py <udmappe>

Skriver <udmappe>/opskrifter.js (window.OPSKRIFTBANK = {...}) og <udmappe>/billeder/<id>.jpg
(nedskaleret til 560 px bredde). Appen indlæser filen med <script src="opskrifter.js">.
"""
import json
import sys
from pathlib import Path

from PIL import Image

BANK = Path(__file__).resolve().parent.parent

# Opbrugts egne varenøgler (P i appen) -> ingrediens-id i banken. Bruges til at se, hvad der er i skabet.
P_TIL_BANK = {
    "okse": "hakket-oksekoed", "kylling": "kyllingebryst", "bacon": "bacon", "aeg": "aeg",
    "floede": "madlavningsfloede", "maelk": "maelk", "mozz": "mozzarella", "parm": "parmesan",
    "smoer": "smoer", "cremef": "creme-fraiche", "loeg": "loeg", "hvidloeg": "hvidloeg",
    "gulerod": "gulerod", "broccoli": "broccoli", "porre": "porre", "peber": "peberfrugt",
    "squash": "zucchini", "champ": "champignon", "spinat": "spinat", "salat": "romainesalat",
    "tomat": "tomat", "agurk": "agurk", "kartof": "kartofler", "citron": "citrusfrugt",
    "spaghetti": "pasta", "ris": "ris", "flaaede": "hakkede-tomater", "pure": "tomatpure",
    "kokos": "kokosmaelk", "pizzadej": "pizzadej", "tortilla": "tortillabroed",
}
# Bankens basisvarer -> Opbrugts BASIS-nøgler (så "løbet tør for" virker)
BASIS_TIL_OPBRUGT = {"olie": "olie", "salt": "salt", "peber": "peberk", "hvedemel": "mel",
                     "sukker": "sukker", "bouillon": "bouillon", "sojasauce": "soja"}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ud = Path(sys.argv[1])
    (ud / "billeder").mkdir(parents=True, exist_ok=True)
    b = json.load(open(BANK / "opskriftbank.json", encoding="utf-8"))
    K = b["kategorier"]

    ing = {}
    for vid, v in b["ingredienser"].items():
        d = {"n": v["navn"], "afd": v["afdeling"], "be": v["basisenhed"]}
        if v.get("synonymer"): d["syn"] = v["synonymer"]
        if v.get("gram_pr_stk"): d["gps"] = v["gram_pr_stk"]
        if v.get("omregning"): d["omr"] = v["omregning"]
        if v.get("basisvare"): d["bv"] = 1
        if v.get("krydderiblanding"):
            d["hf"] = 1
            if v.get("erstatning"): d["erst"] = v["erstatning"]
        if vid in BASIS_TIL_OPBRUGT: d["basis"] = BASIS_TIL_OPBRUGT[vid]
        ing[vid] = d
    for p, vid in P_TIL_BANK.items():
        assert vid in ing, f"{p} -> {vid} findes ikke i banken"

    grupper = {g: {"n": v["navn"], "m": v["medlemmer"], **({"smag": 1} if v.get("bytte") == "efter smag" else {})}
               for g, v in b["variabelgrupper"].items()}

    ops = []
    for o in b["opskrifter"]:
        r = {
            "id": o["id"], "t": o["titel"], "u": o.get("undertitel", ""),
            "k": [K["koekken"][k]["navn"] for k in o["kategorier"]["koekken"]],
            "reg": [K["region"][x] for x in o["beregnet"]["region"]],
            "pr": [K["hovedprotein"][x] for x in o["kategorier"]["hovedprotein"]],
            "tags": o.get("tags", []),
            "pb": o["portioner"]["basis"], "pv": o["portioner"].get("valg", []),
            "ing": [], "trin": [],
            "al": o["beregnet"]["allergener"],
        }
        if o.get("tid"): r["tid"] = [o["tid"].get("min"), o["tid"].get("max")]
        if o.get("noter"): r["noter"] = o["noter"]
        if o["kilde"].get("url"): r["url"] = o["kilde"]["url"]
        if o["kilde"].get("type") == "hellofresh": r["kilde"] = "HelloFresh" + (" " + o["kilde"]["uge"] if o["kilde"].get("uge") else "")
        for l in o["ingredienser"]:
            x = {"i": l["ingrediens"], "n": l["navn"], "m": l.get("maengde"), "e": l["enhed"]}
            if l.get("tabel"): x["t"] = l["tabel"]
            if l.get("basisvare"): x["b"] = 1
            if l.get("variabel"): x["v"] = l["variabel"]
            if l.get("note"): x["note"] = l["note"]
            r["ing"].append(x)
        for t in o["trin"]:
            x = {"t": t.get("titel", ""), "x": t["tekst"]}
            if t.get("tip"): x["tip"] = t["tip"]
            if t.get("vigtigt"): x["vig"] = t["vigtigt"]
            r["trin"].append(x)
        if o.get("billede"):
            kilde = BANK / o["billede"]
            im = Image.open(kilde).convert("RGB")
            im.thumbnail((560, 560))
            im.save(ud / "billeder" / f"{o['id']}.jpg", quality=78, optimize=True)
            r["img"] = f"billeder/{o['id']}.jpg"
        ops.append(r)

    data = {"version": b["genereret"], "ingredienser": ing, "grupper": grupper, "opskrifter": ops,
            "pTilBank": P_TIL_BANK}
    js = "window.OPSKRIFTBANK=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ud / "opskrifter.js").write_text(js, encoding="utf-8")
    billeder = sum(f.stat().st_size for f in (ud / "billeder").glob("*.jpg"))
    print(f"{len(ops)} opskrifter, {len(ing)} ingredienser -> opskrifter.js ({len(js)//1024} KB), "
          f"{len(list((ud / 'billeder').glob('*.jpg')))} billeder ({billeder//1024} KB)")


if __name__ == "__main__":
    main()
