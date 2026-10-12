"""Hold de scannede kvitteringer op mod indkøbslisten, tilbudsaviserne og hyldepriserne.

Brug:  python priser/kvitteringer.py            rapport over nye kvitteringer (skrives også til kvitteringer/rapporter/)
       python priser/kvitteringer.py --marker   marker dem i rapporten som behandlet (køres efter rapporten er læst)
       python priser/kvitteringer.py --alle     tag også kvitteringer, der allerede er behandlet
       python priser/kvitteringer.py --mappe D  brug kvitteringerne i mappen D (til afprøvning)

Kvitteringerne gemmes af appen via Google Apps Script i Google Drive › Privat › mad › kvitteringer › <måned>
(se feedback-modtager/), som synkroniseres til kvitteringer/ her. Mappen er udeladt fra git.

For hver kvittering:
  Priser   normalpriserne (ikke tilbud) holdt op mod hyldeprisen i priser/til_opbrugt/<kæde>.json. En stor forskel
           tyder på, at match-<kæde>.json peger på en forkert vare. Normalpriserne er allerede lagt i den fælles
           prisfil (kvitteringer/priser.json), som appen henter, så appens priser er opdateret.
  Tilbud   Har appen sendt indkøbslisten med (fra v64, "Færdig" i butikken), holdes hvert foreslået tilbud op mod
           kvitteringen: købt som foreslået, købt men ikke til tilbudsprisen (avisen/matchet tog fejl, eller tilbuddet
           gjaldt ikke), købt noget andet (samme byttegruppe), valgt fra (✕) eller ikke købt. Uden liste holdes
           kvitteringen op mod ugens avis.
  Ukendte  linjer uden ingrediens: kandidater til ingredienser.json eller synonymer.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

MAD = Path(__file__).resolve().parent.parent
KVIT = Path(sys.argv[sys.argv.index("--mappe") + 1]) if "--mappe" in sys.argv else MAD / "kvitteringer"
STATUS = KVIT / "_behandlet.json"
KAEDE = {"netto": "netto", "føtex": "foetex", "foetex": "foetex", "rema1000": "rema-1000", "rema": "rema-1000", "lidl": "lidl"}
PR = {"g": "kg", "ml": "l", "stk": "stk"}


def laes(sti, standard=None):
    try:
        return json.loads(Path(sti).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return standard


def kr(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(",00", "") + " kr"


def enhedspris(linje):
    pr = PR.get(linje.get("enhed"))
    m, p = linje.get("maengde") or 0, linje.get("pris") or 0
    if not pr or m <= 0 or p <= 0:
        return None, None
    return p / (m if pr == "stk" else m / 1000), pr


def kaede(butik):
    n = re.sub(r"[^a-zæøå0-9]", "", str(butik or "").lower())
    return next((v for k, v in KAEDE.items() if n.startswith(k)), None)


def main():
    alle, marker = "--alle" in sys.argv, "--marker" in sys.argv
    status = laes(STATUS, {"behandlet": {}})
    filer = sorted(f for f in KVIT.glob("*/*.json"))
    nye = [f for f in filer if alle or f.name not in status["behandlet"]]
    if marker:
        for f in nye:
            status["behandlet"][f.name] = date.today().isoformat()
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(nye)} kvitteringer markeret som behandlet.")
        return
    if not nye:
        print("Ingen nye kvitteringer.")
        return

    ing = {k: v for k, v in laes(MAD / "opskriftbank" / "ingredienser.json", {}).items() if not k.startswith("_")}
    grupper = [g for k, g in laes(MAD / "opskriftbank" / "variabler.json", {}).items() if not k.startswith("_")]
    navn = lambda i: (ing.get(i) or {}).get("navn", i)
    samme_gruppe = lambda a, b: any(a in g["medlemmer"] and b in g["medlemmer"] for g in grupper)

    ud = [f"# Kvitteringer {date.today().isoformat()}", ""]
    for f in nye:
        k = laes(f, {})
        kd = kaede(k.get("butik"))
        dag = (k.get("modtaget") or f.name)[:10]
        linjer = k.get("linjer") or []
        hylde = (laes(MAD / "priser" / "til_opbrugt" / f"{kd}.json", {}) or {}).get("varer", {}) if kd else {}
        avis = [t for t in ((laes(MAD / "tilbud" / "til_opbrugt" / f"{kd}.json", {}) or {}).get("tilbud", []) if kd else [])
                if t.get("i") and t.get("f", "") <= dag <= t.get("t", "")]
        i_alt = sum(x.get("pris") or 0 for x in linjer)
        ud += [f"## {k.get('butik') or 'Ukendt butik'} · {k.get('modtaget', dag)} · {len(linjer)} linjer · {kr(i_alt)}",
               f"Fil: `{KVIT.name}/{f.relative_to(KVIT).as_posix()}` · app-version {k.get('version', '?')}"
               + (f" · billede gemt: {k['billedeGrund']}" if k.get("billedeGrund") else ""), ""]

        # Priser
        rk = []
        for x in linjer:
            if not x.get("i") or x.get("rabat"):
                continue
            ep, pr = enhedspris(x)
            h = hylde.get(x["i"])
            if ep is None:
                continue
            if h and h.get("pr") == pr and h.get("ep"):
                d = (ep - h["ep"]) / h["ep"]
                note = " ⚠ stor forskel: tjek match-filen" if abs(d) > .25 else ""
                rk.append(f"| {navn(x['i'])} | {x['tekst']} | {kr(ep)}/{pr} | {kr(h['ep'])}/{pr} ({h.get('n', '')}) | {d:+.0%}{note} |")
            else:
                rk.append(f"| {navn(x['i'])} | {x['tekst']} | {kr(ep)}/{pr} | ingen hyldepris | ny |")
        if rk:
            ud += ["### Normalpriser", "Lagt i den fælles prisfil, som appen henter.", "",
                   "| Ingrediens | Kvittering | Pris | Hyldepris | Forskel |", "|---|---|---|---|---|", *rk, ""]

        # Tilbud
        ud.append("### Tilbud")
        varer = [v for t in (k.get("indkob") or []) for v in (t.get("varer") or [])]
        brugt = set()

        def find(v):
            for n, x in enumerate(linjer):
                if x.get("i") and x.get("i") == v.get("id"):
                    return n, x, "samme"
            for n, x in enumerate(linjer):
                if x.get("i") and v.get("id") and samme_gruppe(x["i"], v["id"]):
                    return n, x, "andet"
            return None, None, None

        if varer:
            uden = any(t.get("uden_faerdig") for t in k.get("indkob") or [])
            ud.append(f"Holdt op mod indkøbslisten{' (som den så ud, da kvitteringen blev scannet – der blev ikke trykket Færdig)' if uden else ''}:")
            ud.append("")
            spm = []
            for v in varer:
                n, x, slags = find(v)
                if n is not None:
                    brugt.add(n)
                t = v.get("tilbud")
                til = f" – til {', '.join(v['retter'])}" if v.get("retter") else ""
                if not t:
                    continue
                tekst = f"**{v['navn']}** (tilbud: {t.get('o')}, {kr(t.get('p') or 0)})"
                if slags == "samme":
                    ep, pr = enhedspris(x)
                    ok = (t.get("ep") and ep and pr == t.get("pr") and abs(ep - t["ep"]) <= t["ep"] * .1) or abs((x.get("pris") or 0) - (t.get("p") or 0)) <= (t.get("p") or 0) * .1
                    ud.append(f"- {tekst}: " + ("købt som foreslået." if ok else
                              f"købt, men ikke til tilbudsprisen ({x['tekst']} {kr(x.get('pris') or 0)}). Avisen eller matchet kan tage fejl, eller tilbuddet gjaldt ikke."))
                elif slags == "andet":
                    ud.append(f"- {tekst}: købt noget andet i stedet: {x['tekst']} ({kr(x.get('pris') or 0)}).")
                elif v.get("mark") == "nej":
                    ud.append(f"- {tekst}: valgt fra i butikken (✕){til}.")
                    spm.append(v["navn"])
                else:
                    ud.append(f"- {tekst}: ikke på kvitteringen{til}.")
                    spm.append(v["navn"])
            ikke = [v["navn"] for v in varer if not v.get("tilbud") and find(v)[0] is None]
            if ikke:
                ud.append(f"- Fra listen, men ikke på kvitteringen: {', '.join(ikke)}.")
            uden_for = [x["tekst"] for n, x in enumerate(linjer) if n not in brugt]
            if uden_for:
                ud.append(f"- Købt uden for listen: {', '.join(uden_for)}.")
            if spm:
                ud += ["", f"**Spørgsmål:** Hvorfor blev {', '.join(spm)} ikke købt? Havde I det hjemme (fx på frost), "
                           "fandtes det ikke, var tilbuddet forkert, eller blev noget andet købt?"]
        else:
            ud.append("Ingen indkøbsliste med kvitteringen (sendt fra en ældre version af appen). Holdt op mod ugens avis i stedet:")
            ud.append("")
            for n, x in enumerate(linjer):
                match = [t for t in avis if t["i"] == x.get("i")]
                if match:
                    t = min(match, key=lambda t: abs((t.get("p") or 0) - (x.get("pris") or 0)))
                    ok = abs((x.get("pris") or 0) - (t.get("p") or 0)) <= (t.get("p") or 0) * .1
                    ud.append(f"- {x['tekst']} {kr(x.get('pris') or 0)}: " + (f"købt på tilbud ({t['o']}, {kr(t['p'])})." if ok else
                              f"avisen havde {t['o']} til {kr(t['p'])} – der blev købt en anden vare eller til en anden pris."))
                elif x.get("rabat"):
                    ud.append(f"- {x['tekst']} {kr(x.get('pris') or 0)}: rabat på kvitteringen, men ikke fundet i avisen.")
            paa = sorted({navn(t["i"]) for t in avis if not (ing.get(t["i"]) or {}).get("basisvare")}
                         - {navn(x.get("i")) for x in linjer if x.get("i")})
            if paa:
                ud.append(f"- På tilbud i {k.get('butik')}, men ikke købt: {', '.join(paa)}. Uden indkøbslisten kan det ikke ses, hvad appen foreslog.")
        ud.append("")

        ukendte = [f"{x['tekst']} ({kr(x.get('pris') or 0)})" for x in linjer if not x.get("i")]
        if ukendte:
            ud += ["### Ukendte varer", "Uden ingrediens i kataloget: " + ", ".join(ukendte) + ".", ""]

    tekst = "\n".join(ud)
    (KVIT / "rapporter").mkdir(exist_ok=True)
    (KVIT / "rapporter" / f"{date.today().isoformat()}.md").write_text(tekst, encoding="utf-8")
    print(tekst)


if __name__ == "__main__":
    main()
