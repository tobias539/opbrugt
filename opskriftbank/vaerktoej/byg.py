"""Tjek alle opskrifter og saml dem i opskriftbank.json.

Brug:  python vaerktoej/byg.py

Fejl (stopper bygningen):
  - opskrift følger ikke skema/opskrift.schema.json
  - id passer ikke med filnavnet, eller findes to gange
  - ingrediens, kategori, tag eller allergen findes ikke i ingredienser.json / kategorier.json
  - 'tabel' har et portionsantal, der ikke står i portioner.valg
  - billedet findes ikke
Advarsler (bygningen fortsætter):
  - en ingredienslinjes allergener står ikke i opskriftens samlede allergenliste
  - en mængde kan ikke regnes om til ingrediensens basisenhed
Til sidst listes scanninger i kilder/scanninger, som ingen opskrift henviser til endnu.
"""
import json
import sys
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

BANK = Path(__file__).resolve().parent.parent
VOLUMEN = {"ml": 1, "dl": 100, "l": 1000, "tsk": 5, "spsk": 15}
VAEGT = {"g": 1, "kg": 1000}


def laes(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def omregn(maengde, enhed, vare):
    """Mængde i ingrediensens basisenhed, eller None hvis det ikke kan regnes om."""
    if maengde is None:
        return None
    base = vare["basisenhed"]
    if enhed == base:
        return maengde
    for tabel in (VOLUMEN, VAEGT):
        if enhed in tabel and base in tabel:
            return maengde * tabel[enhed] / tabel[base]
    if enhed in vare.get("omregning", {}):
        return maengde * vare["omregning"][enhed]
    return None


def maengde_til(linje, n, basis):
    """Kildens egen mængde for n portioner, ellers lineær skalering."""
    if linje.get("maengde") is None:
        return None
    if str(n) in linje.get("tabel", {}):
        return linje["tabel"][str(n)]
    return linje["maengde"] * n / basis


def gram(maengde, enhed, vare):
    """Mængde i gram (ml regnes som g), eller None. Bruges når ingredienser byttes efter vægt."""
    v = omregn(maengde, enhed, vare)
    if v is None:
        return None
    if vare["basisenhed"] in ("g", "ml"):
        return v
    if vare.get("gram_pr_stk") and vare["basisenhed"] in ("stk", "fed"):
        return v * vare["gram_pr_stk"]
    return None


def som_maengde(g, vare):
    """Gram omsat til en mængde i erstatningens egen enhed: hele/halve stk eller runde gram/ml."""
    if g is None:
        return None, None
    base = vare["basisenhed"]
    if base in ("g", "ml"):
        return max(5, round(g / 5) * 5), base
    if vare.get("gram_pr_stk"):
        return max(0.5, round(g / vare["gram_pr_stk"] * 2) / 2), base
    return None, None


def main():
    kat = laes(BANK / "kategorier.json")
    varer = {k: v for k, v in laes(BANK / "ingredienser.json").items() if not k.startswith("_")}

    # --forslag: tag forslag fra _forslag/*.json med i tjekket, men skriv ikke opskriftbank.json
    proeve = "--forslag" in sys.argv
    if proeve:
        for f in sorted((BANK / "_forslag").glob("*.json")):
            fs = laes(f)
            varer.update(fs.get("nye_ingredienser", {}))
            for felt, nye in fs.get("nye_kategorier", {}).items():
                kat[felt].update(nye)
    validator = Draft202012Validator(laes(BANK / "skema" / "opskrift.schema.json"))
    allergen_ok = {k for k in kat["allergener"] if not k.startswith("_")}
    grupper = {k: v for k, v in laes(BANK / "variabler.json").items() if not k.startswith("_")}
    fejl = []
    for g, gv in grupper.items():
        for m in gv["medlemmer"]:
            if m not in varer:
                fejl.append(f"variabler.json: '{m}' i gruppen '{g}' findes ikke i ingredienser.json")

    advarsler, opskrifter, set_ids = [], [], set()

    for fil in sorted((BANK / "opskrifter").glob("*.json")):
        navn = fil.name
        try:
            o = laes(fil)
        except json.JSONDecodeError as e:
            fejl.append(f"{navn}: ugyldig JSON ({e})")
            continue
        skemafejl = sorted(validator.iter_errors(o), key=lambda e: list(e.path))
        for e in skemafejl:
            sti = "/".join(str(x) for x in e.path) or "(rod)"
            fejl.append(f"{navn}: {sti}: {e.message}")
        if skemafejl:
            continue

        rid = o["id"]
        if rid != fil.stem:
            fejl.append(f"{navn}: id '{rid}' passer ikke med filnavnet")
        if rid in set_ids:
            fejl.append(f"{navn}: id '{rid}' findes allerede")
        set_ids.add(rid)

        for felt, vaerdier in o["kategorier"].items():
            for v in vaerdier:
                if v not in kat[felt]:
                    fejl.append(f"{navn}: kategorier.{felt} '{v}' findes ikke i kategorier.json")
        for t in o.get("tags", []):
            if t not in kat["tags"]:
                fejl.append(f"{navn}: tag '{t}' findes ikke i kategorier.json")

        al = o.get("allergener", {})
        for a in al.get("indeholder", []) + al.get("spor_af", []):
            if a not in allergen_ok:
                fejl.append(f"{navn}: allergen '{a}' findes ikke i kategorier.json")

        if o.get("billede") and not (BANK / o["billede"]).exists():
            fejl.append(f"{navn}: billedet {o['billede']} findes ikke")

        basis = o["portioner"]["basis"]
        valg = o["portioner"].get("valg", [basis])
        for i, linje in enumerate(o["ingredienser"]):
            vid = linje["ingrediens"]
            hvor = f"{navn}: ingredienser[{i}] ({linje['navn']})"
            if vid not in varer:
                fejl.append(f"{hvor}: '{vid}' findes ikke i ingredienser.json")
                continue
            for n in linje.get("tabel", {}):
                if int(n) not in valg:
                    fejl.append(f"{hvor}: tabel har {n} portioner, men portioner.valg er {valg}")
            # Kilden deklarerer kun det, den selv leverer, så basisvarer tjekkes ikke mod kildens liste
            for a in linje.get("allergener", []):
                if a not in allergen_ok:
                    fejl.append(f"{hvor}: allergen '{a}' findes ikke i kategorier.json")
                elif al and not linje.get("basisvare") and a not in al.get("indeholder", []):
                    advarsler.append(f"{hvor}: indeholder '{a}', men det står ikke i opskriftens allergener")
            for a in linje.get("spor_af", []):
                if al and not linje.get("basisvare") and a not in al.get("spor_af", []):
                    advarsler.append(f"{hvor}: spor af '{a}', men det står ikke i opskriftens spor_af")

            # Beregnede mængder i basisenhed, så appen kan sammenligne direkte med køleskab og tilbud
            vare = varer[vid]
            pr = {}
            for n in valg:
                v = omregn(maengde_til(linje, n, basis), linje["enhed"], vare)
                if v is not None:
                    pr[str(n)] = round(v, 2)
            if linje.get("maengde") is not None and not pr and not linje.get("basisvare"):
                advarsler.append(f"{hvor}: {linje['enhed']} kan ikke regnes om til {vare['basisenhed']}")
            linje["beregnet"] = {"basisenhed": vare["basisenhed"], "pr_portioner": pr}

            # Variabel: alternativer fra gruppen, med mængde til basis-portioner (byttes efter vægt)
            g = linje.get("variabel")
            if g:
                if g not in grupper:
                    fejl.append(f"{hvor}: variabel '{g}' findes ikke i variabler.json")
                    continue
                if vid not in grupper[g]["medlemmer"]:
                    fejl.append(f"{hvor}: '{vid}' er ikke medlem af gruppen '{g}'")
                    continue
                g_orig = gram(linje.get("maengde"), linje["enhed"], vare)
                efter_smag = grupper[g].get("bytte") == "efter smag"
                egen = grupper[g]["medlemmer"][vid]
                alt = []
                for m, kval in grupper[g]["medlemmer"].items():
                    if m == vid:
                        continue
                    # Et bytte er kun 'god', hvis både originalen og erstatningen er 'god' i gruppen
                    kval = "god" if kval == egen == "god" else "ok"
                    mg, me = (None, "efter smag") if efter_smag else som_maengde(g_orig, varer[m])
                    alt.append({"ingrediens": m, "navn": varer[m]["navn"], "kvalitet": kval, "maengde": mg, "enhed": me})
                linje["beregnet"]["gram"] = round(g_orig) if g_orig is not None else None
                linje["beregnet"]["alternativer"] = alt

        koekken = o["kategorier"]["koekken"]
        tid = o.get("tid", {})
        indeholder = set(al.get("indeholder", []))
        spor = set(al.get("spor_af", []))
        for linje in o["ingredienser"]:
            indeholder |= set(linje.get("allergener", []))
            spor |= set(linje.get("spor_af", []))
        o["beregnet"] = {
            "region": sorted({kat["koekken"][k]["region"] for k in koekken if k in kat["koekken"]}),
            "tid_max_min": tid.get("max", tid.get("min")),
            "allergener": {"indeholder": sorted(indeholder), "spor_af": sorted(spor - indeholder)},
            "ingredienser": sorted({l["ingrediens"] for l in o["ingredienser"] if not l.get("basisvare")}),
            "basisvarer": sorted({l["ingrediens"] for l in o["ingredienser"] if l.get("basisvare")}),
            # Den løse udgave af retten: faste ingredienser + pladser, der kan fyldes fra en gruppe
            "skabelon": {
                "faste": [l["ingrediens"] for l in o["ingredienser"]
                          if not l.get("basisvare") and not l.get("variabel")],
                "variable": [{"gruppe": l["variabel"], "navn": grupper[l["variabel"]]["navn"],
                              "original": l["ingrediens"], "gram": l.get("beregnet", {}).get("gram")}
                             for l in o["ingredienser"] if l.get("variabel") in grupper],
            },
        }
        opskrifter.append(o)

    for o in opskrifter:
        v = o.get("variant_af")
        if v and v not in set_ids:
            fejl.append(f"{o['id']}.json: variant_af '{v}' findes ikke")

    for a in advarsler:
        print("ADVARSEL", a)
    if fejl:
        for f in fejl:
            print("FEJL    ", f)
        sys.exit(f"\n{len(fejl)} fejl. opskriftbank.json er ikke opdateret.")
    if proeve:
        print(f"PRØVE OK: {len(opskrifter)} opskrifter, {len(advarsler)} advarsler (med forslag, intet skrevet)")
        return

    bruges_i = {}
    for o in opskrifter:
        for vid in o["beregnet"]["ingredienser"] + o["beregnet"]["basisvarer"]:
            bruges_i.setdefault(vid, []).append(o["id"])
    # Omvendt opslag: hvor kan en ingrediens bruges – som original eller som erstatning
    kan_bruges = {}
    for o in opskrifter:
        for l in o["ingredienser"]:
            if l.get("basisvare"):
                continue
            kan_bruges.setdefault(l["ingrediens"], []).append(
                {"opskrift": o["id"], "erstatter": None, "kvalitet": "original"})
            for a in l["beregnet"].get("alternativer", []):
                kan_bruges.setdefault(a["ingrediens"], []).append(
                    {"opskrift": o["id"], "erstatter": l["ingrediens"], "kvalitet": a["kvalitet"],
                     "maengde": a["maengde"], "enhed": a["enhed"]})
    katalog = {vid: {**v, "bruges_i": bruges_i.get(vid, []), "kan_bruges_i": kan_bruges.get(vid, [])}
               for vid, v in varer.items()}

    ud = {
        "format": "opskriftbank",
        "version": 1,
        "genereret": date.today().isoformat(),
        "antal_opskrifter": len(opskrifter),
        "skalering": "Mængde til n portioner = linjens tabel[n], hvis den findes, ellers maengde * n / portioner.basis. 'beregnet.pr_portioner' er allerede regnet om til ingrediensens basisenhed.",
        "variabler": "En linje med 'variabel' kan byttes med de andre i gruppen (se 'variabelgrupper'). 'beregnet.alternativer' viser mængden til basis-portioner, regnet efter vægt. 'beregnet.skabelon' på hver opskrift er den løse udgave. 'kan_bruges_i' på hver ingrediens viser alle retter, den kan bruges i – også som erstatning.",
        "kategorier": {k: v for k, v in kat.items() if not k.startswith("_")},
        "variabelgrupper": grupper,
        "ingredienser": katalog,
        "opskrifter": opskrifter,
    }
    with open(BANK / "opskriftbank.json", "w", encoding="utf-8") as f:
        json.dump(ud, f, ensure_ascii=False, indent=1)
    print(f"OK: {len(opskrifter)} opskrifter, {len(katalog)} ingredienser, {len(advarsler)} advarsler → opskriftbank.json")

    brugte = {o["kilde"].get("scanning") for o in opskrifter}
    for pdf in sorted((BANK / "kilder" / "scanninger").glob("*.pdf")):
        sti = pdf.relative_to(BANK).as_posix()
        if sti not in brugte:
            print(f"IKKE BEHANDLET: {sti}")


if __name__ == "__main__":
    main()
