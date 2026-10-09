"""Foreslå, hvilken REMA-vare hver ingrediens i opskriftbanken svarer til.

Brug:  python priser/foreslaa_match.py            (vis forslag for ingredienser, der ikke er i match-filen)
       python priser/foreslaa_match.py --skriv    (skriv forslagene ind i match-rema-1000.json)

Forslagene er kun et udgangspunkt: gennemgå listen og ret forkerte valg i match-rema-1000.json
(sæt værdien til null, hvis REMA ikke har varen). Eksisterende linjer i match-filen ændres aldrig.
"""
import gzip
import json
import re
import sys
from pathlib import Path

MAPPE = Path(__file__).resolve().parent
BANK = MAPPE.parent / "opskriftbank" / "ingredienser.json"
RAA = MAPPE / "raa" / "rema-1000.json.gz"
MATCH = MAPPE / "match-rema-1000.json"

# Ord, der betyder, at varen er forarbejdet og ikke selve råvaren
FORARB = re.compile(r"SAUCE|DRESSING|CHIPS|SNACK|MARINADE|SALAT\b.*MED|SUPPE|PATE|POSTEJ|PÅLÆG|SPREAD|DIP|JUICE|SAFT|SLIK|KAGE|"
                    r"PIZZA|LASAGNE|FÆRDIGRET|NUGGETS|FRIKADELLE|KROKET|BØRNEMAD|BABY|HUNDE|KATTE|GRYDERET|BURGER\b|POMFRITTER")
ENHED = {"g": "kg", "ml": "l", "stk": "stk", "fed": "stk"}


def norm(t):
    return re.sub(r"[^A-ZÆØÅ0-9 ]", " ", t.upper()).split()


def score(ingr, v):
    navn = " ".join(norm(v["n"]))
    hele = navn + " " + " ".join(norm(v.get("u", "")))
    bedst = 0
    for i, term in enumerate([ingr["navn"], *ingr.get("synonymer", [])]):
        ord_ = norm(term)
        if not ord_:
            continue
        if all(re.search(r"(^| )" + re.escape(o) + r"(ER|E|R|N|NE)?( |$)", navn) for o in ord_):
            bedst = max(bedst, 10 - min(i, 4) + (3 if navn.startswith(ord_[0]) else 0))
        elif all(o in hele for o in ord_):
            bedst = max(bedst, 4)
    if not bedst:
        return 0
    if FORARB.search(navn):
        bedst -= 6
    if "ØKO" in navn:
        bedst -= 1
    if v.get("pr") != ENHED.get(ingr.get("basisenhed"), v.get("pr")):
        bedst -= 2
    return bedst


def main():
    bank = {k: v for k, v in json.load(open(BANK, encoding="utf-8")).items() if not k.startswith("_")}
    varer = [v for v in json.load(gzip.open(RAA, "rt", encoding="utf-8"))["varer"] if v.get("p") is not None]
    match = json.loads(MATCH.read_text(encoding="utf-8")) if MATCH.exists() else {}
    nye = {}
    for iid, ingr in sorted(bank.items()):
        if iid in match or ingr.get("krydderiblanding"):
            continue
        kand = sorted(((score(ingr, v), v) for v in varer), key=lambda x: (-x[0], x[1].get("ep") or 9e9))
        kand = [(s, v) for s, v in kand if s > 0][:4]
        valg = kand[0][1]["id"] if kand and kand[0][0] >= 6 else None
        nye[iid] = valg
        print(f"{iid:32} {ingr['navn'][:24]:24} -> " + (" | ".join(f"{'*' if v['id']==valg else ' '}{v['id']} {v['n'][:28]} ({v.get('u','')[:18]}) {v.get('ep')}/{v.get('pr')} s{s}" for s, v in kand) or "INGEN"))
    if "--skriv" in sys.argv:
        match.update(nye)
        MATCH.write_text(json.dumps(dict(sorted(match.items())), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"skrev {len(nye)} forslag til {MATCH.name}")


if __name__ == "__main__":
    main()
