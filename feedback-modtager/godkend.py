"""Godkend eller afvis opskrifter, som nogen har delt fra appen.

Delte opskrifter gemmes af Google Apps Script i Google Drive › Privat › mad › opskrifter-delt › afventer, som
synkroniseres til opskrifter-delt/afventer/ (udeladt fra git). Andre kan først se en opskrift i appen, når den
er flyttet op i opskrifter-delt/. En afvist opskrift flyttes til opskrifter-delt/afvist/, så den kan findes igen.

Brug:  python feedback-modtager/godkend.py                  vis de opskrifter, der venter
       python feedback-modtager/godkend.py --godkend <id>   vis den for alle, der bruger appen
       python feedback-modtager/godkend.py --afvis <id>     vis den ikke for andre
<id> er filnavnet uden .json, eller et stykke af id'et eller titlen, der kun passer på én opskrift.
"""
import json
import os
import sys
from pathlib import Path

DELT = Path(__file__).resolve().parent.parent / "opskrifter-delt"
AFVENTER = DELT / "afventer"
AFVIST = DELT / "afvist"


def laes(fil):
    try:
        return json.loads(fil.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def venter():
    return sorted(AFVENTER.glob("*.json")) if AFVENTER.is_dir() else []


def vis(fil):
    o = laes(fil)
    print(f"===== {fil.stem} =====")
    print(f"{o.get('t', '?')}{' – ' + o['u'] if o.get('u') else ''}")
    kilde = [o.get("kilde"), o.get("ig"), o.get("url")]
    print("Kilde:", " · ".join(k for k in kilde if k) or "ingen")
    if o.get("udgave"):
        print("Appens egen udgave af en ret fra Instagram (ikke skaberens opskrift).")
    if (DELT / fil.name).exists():
        print("Ny udgave af en godkendt opskrift: den gamle bliver vist, til denne er godkendt.")
    print("Ingredienser:", ", ".join(str(l.get("n", "")) for l in o.get("ing", [])))
    for i, t in enumerate(o.get("trin", []), 1):
        print(f"  {i}. {t.get('t', '')}: {' '.join(t.get('x', []))}")
    print()


def find(soeg):
    filer = venter()
    for f in filer:
        if f.stem == soeg:
            return f
    s = soeg.lower()
    passer = [f for f in filer if s in f.stem.lower() or s in str(laes(f).get("t", "")).lower()]
    if len(passer) == 1:
        return passer[0]
    if not passer:
        sys.exit(f"Ingen opskrift, der venter, passer på '{soeg}'.")
    sys.exit(f"Flere passer på '{soeg}': " + ", ".join(f.stem for f in passer))


def main():
    if len(sys.argv) == 3 and sys.argv[1] in ("--godkend", "--afvis"):
        fil = find(sys.argv[2])
        titel = laes(fil).get("t", fil.stem)
        if sys.argv[1] == "--godkend":
            os.replace(fil, DELT / fil.name)
            print(f"Godkendt: {titel}. Den bliver vist for alle, der bruger appen, når Drive har synkroniseret.")
        else:
            AFVIST.mkdir(exist_ok=True)
            os.replace(fil, AFVIST / fil.name)
            print(f"Afvist: {titel}. Den ligger i opskrifter-delt/afvist/ og bliver ikke vist for andre.")
        return
    if len(sys.argv) > 1:
        sys.exit(__doc__)
    filer = venter()
    if not filer:
        print("Ingen delte opskrifter venter på godkendelse.")
        return
    print(f"{len(filer)} delt(e) opskrift(er) venter på godkendelse:\n")
    for f in filer:
        vis(f)


if __name__ == "__main__":
    main()
