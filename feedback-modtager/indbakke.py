"""Vis ny feedback fra appen, så den daglige rutine kan vurdere den.
Viser også delte opskrifter, der venter på godkendelse (godkendes med godkend.py).

Brug:  python feedback-modtager/indbakke.py            ny feedback + vurderinger, der venter på et valg
       python feedback-modtager/indbakke.py --marker   marker den viste feedback som vurderet

Feedbacken gemmes af Google Apps Script i Google Drive › Privat › mad › feedback, som synkroniseres til feedback/
(udeladt fra git). Rutinen skriver sin vurdering til feedback/vurderinger/<dato>.md: for hver feedback en
opsummering og tre veje – 1 optimistisk og problemløsende, 2 reflekterende (hvad betyder det for resten af
opsætningen), 3 ulemperne – og "Valg: afventer", indtil brugeren har valgt en vej eller en kombination.
"""
import json
import sys
from datetime import date
from pathlib import Path

MAPPE = Path(__file__).resolve().parent.parent / "feedback"
STATUS = MAPPE / "_vurderet.json"
# Delte opskrifter, der venter på godkendelse (se godkend.py)
DELT_AFVENTER = MAPPE.parent / "opskrifter-delt" / "afventer"


def main():
    try:
        status = json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        status = {"vurderet": {}}
    nye = sorted(f for f in MAPPE.glob("*.txt") if f.name not in status["vurderet"])
    if "--marker" in sys.argv:
        for f in nye:
            status["vurderet"][f.name] = date.today().isoformat()
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(nye)} feedback markeret som vurderet.")
        return
    afventer = []
    for v in sorted((MAPPE / "vurderinger").glob("*.md")):
        n = v.read_text(encoding="utf-8").count("**Valg:** afventer")
        if n:
            afventer.append(f"{v.relative_to(MAPPE.parent).as_posix()} ({n})")
    if afventer:
        print("Vurderinger, der venter på et valg:", ", ".join(afventer))
    delte = sorted(DELT_AFVENTER.glob("*.json")) if DELT_AFVENTER.is_dir() else []
    if delte:
        titler = []
        for f in delte:
            try:
                titler.append(json.loads(f.read_text(encoding="utf-8")).get("t") or f.stem)
            except (OSError, ValueError):
                titler.append(f.stem)
        print(f"Delte opskrifter, der venter på godkendelse ({len(delte)}): {', '.join(titler)}. "
              "Vis dem med python feedback-modtager/godkend.py, og spørg brugeren, om de skal godkendes "
              "(--godkend <id>) eller afvises (--afvis <id>).")
    if not nye:
        print("Ingen ny feedback.")
        return
    print(f"{len(nye)} ny feedback:\n")
    for f in nye:
        print(f"===== {f.name} =====")
        print(f.read_text(encoding="utf-8").strip(), "\n")


if __name__ == "__main__":
    main()
