"""Foreslå 'variabel' for ingredienslinjer ud fra variabler.json.

Brug:  python vaerktoej/tildel_variabler.py            (viser forslag, ændrer intet)
       python vaerktoej/tildel_variabler.py --skriv    (skriver de sikre forslag ind)

- Linjer, der allerede har feltet 'variabel' (også null), røres ikke. Sæt "variabel": null
  på en linje for at låse den fast (fx agurk i tzatziki).
- Basisvarer får ingen variabel.
- Findes ingrediensen i flere grupper, afgøres gruppen af fremgangsmåden: sætninger, der
  nævner ingrediensen, scannes for ord som 'ovn/bageplade', 'steg/pande/wok', 'kog/gryde/simre'
  og 'salat/salsa/slaw/skål' (først i sætningen, ellers i hele trinnet). Navne på de andre
  ingredienser fjernes først, så 'tomat' ikke findes i 'tomatpuré'. Kan det ikke afgøres, vises linjen
  som UAFKLARET.
"""
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

BANK = Path(__file__).resolve().parent.parent
ORD = {
    "ovn": r"\bovn|bageplade|\bbag\b|\bbages\b|ovnbag",
    "pande": r"\bsteg|pande|\bwok|svits|falde sammen|falder sammen",
    "kogt": r"\bkog|simre|gryde|suppe|curry|sauce",
    "raa": r"salat|salsa|slaw|\bsylt|lille skål|\bskål|\brå\b|dressing|dip\b|top med",
}


VARER = {}


def laes(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def noegleord(linje, vare):
    ord_ = set()
    for n in (linje["navn"], vare["navn"]):
        for w in re.findall(r"[a-zæøå]{4,}", n.lower()):
            ord_.add(w[:6] if len(w) > 6 else w)
    return ord_


def andre_navne(o, linje, varer):
    """Navne på de ANDRE ingredienser i retten, længste først. De fjernes fra teksten før søgning,
    så fx 'tomat' ikke findes i 'tomatpuré' eller 'hakkede tomater'."""
    navne = set()
    for l in o["ingredienser"]:
        if l["ingrediens"] != linje["ingrediens"]:
            v = varer.get(l["ingrediens"], {})
            navne |= {n.lower() for n in (l["navn"], v.get("navn", ""), *v.get("synonymer", [])) if len(n) > 3}
    return sorted(navne, key=len, reverse=True)


def saetninger(o):
    """(trin-indeks, sætning) for alle sætninger i alle trin, titlen med som første 'sætning'."""
    ud = []
    for i, t in enumerate(o["trin"]):
        ud.append((i, (t.get("titel") or "").lower()))
        for afsnit in t["tekst"]:
            for s in re.split(r"(?<=[.!?])\s+", afsnit):
                ud.append((i, s.lower()))
    return ud


def roller_i(tekst):
    return {r for r, rx in ORD.items() if re.search(rx, tekst)}


def afgoer(o, linje, vare, kandidater, grupper):
    kw = noegleord(linje, vare)
    alle = saetninger(o)
    fjern = andre_navne(o, linje, VARER)

    def renset(s):
        for n in fjern:
            s = s.replace(n, " ")
        return s
    nævnt = [(i, s) for i, s in alle if any(re.search(r"\b" + re.escape(k), renset(s)) for k in kw)]
    mulige = {r for g in kandidater for r in grupper[g].get("tilberedning", [])}
    # 1) sætninger der nævner ingrediensen, 2) hele trinnet (titel + tekst)
    for udvid in (0, 1):
        fundet = set()
        for i, s in nævnt:
            if udvid == 0:
                fundet |= roller_i(s)
            else:
                fundet |= roller_i(" ".join(t for j, t in alle if j == i))
        hit = [g for g in kandidater if set(grupper[g].get("tilberedning", [])) & fundet & mulige]
        if len(hit) == 1:
            return hit[0], [s for _, s in nævnt][:3]
        if len(hit) > 1:
            return None, [s for _, s in nævnt][:3]
    return None, [s for _, s in nævnt][:3]


def main():
    skriv = "--skriv" in sys.argv
    grupper = {k: v for k, v in laes(BANK / "variabler.json").items() if not k.startswith("_")}
    varer = {k: v for k, v in laes(BANK / "ingredienser.json").items() if not k.startswith("_")}
    VARER.update(varer)
    i_grupper = {}
    for g, v in grupper.items():
        for m in v["medlemmer"]:
            i_grupper.setdefault(m, []).append(g)

    antal = {"sat": 0, "uafklaret": 0, "fast": 0}
    for fil in sorted((BANK / "opskrifter").glob("*.json")):
        o = laes(fil)
        aendret = False
        for linje in o["ingredienser"]:
            if "variabel" in linje or linje.get("basisvare"):
                continue
            kand = i_grupper.get(linje["ingrediens"], [])
            if not kand:
                antal["fast"] += 1
                continue
            if len(kand) == 1:
                g, kontekst = kand[0], []
            else:
                g, kontekst = afgoer(o, linje, varer[linje["ingrediens"]], kand, grupper)
            if g:
                antal["sat"] += 1
                print(f"  {o['id'][:45]:45} {linje['navn'][:28]:28} -> {g}" + (f"   [{len(kand)} muligheder]" if len(kand) > 1 else ""))
                if skriv:
                    linje["variabel"] = g
                    aendret = True
            else:
                antal["uafklaret"] += 1
                print(f"UAFKLARET {o['id'][:40]:40} {linje['navn'][:28]:28} kandidater={kand}")
                for s in kontekst:
                    print(f"            » {s[:140]}")
        if aendret:
            with open(fil, "w", encoding="utf-8") as f:
                json.dump(o, f, ensure_ascii=False, indent=2)
    print(f"\n{antal['sat']} linjer får en variabel, {antal['uafklaret']} er uafklarede, "
          f"{antal['fast']} er faste (ingen gruppe). {'Skrevet.' if skriv else 'Intet skrevet (brug --skriv).'}")


if __name__ == "__main__":
    main()
