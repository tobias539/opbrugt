"""Hent hyldepriser fra REMA 1000's webshop og lav en lille prisfil til Opbrugt-appen.

Brug:  python priser/hent_priser.py              (hent kataloget, hvis det er over 4 uger gammelt, og byg prisfilen)
       python priser/hent_priser.py --tving      (hent kataloget nu)
       python priser/hent_priser.py --kun-byg    (byg prisfilen ud fra det hentede katalog)

REMA's webshop (shop.rema1000.dk) henter varer og priser fra api.digital.rema1000.dk. Hele sortimentet
(ca. 4.000 varer) hentes med ca. 40 forespørgsler og en pause imellem. API'et er ikke officielt åbent, så
det hentes højst én gang om måneden, og det rå katalog bliver på computeren (ikke i git).

Filer:
  raa/rema-1000.json.gz            hele kataloget, kompakt (ikke i git)
  match-rema-1000.json             hvilken REMA-vare hver ingrediens i opskriftbanken svarer til (i git, rettes i hånden)
  til_opbrugt/rema-1000.json       hyldepris pr. ingrediens, som appen henter (i git)
"""
import gzip
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAPPE = Path(__file__).resolve().parent
API = "https://api.digital.rema1000.dk/api/v3/products"
RAA = MAPPE / "raa" / "rema-1000.json.gz"
MATCH = MAPPE / "match-rema-1000.json"
UD = MAPPE / "til_opbrugt" / "rema-1000.json"
ENHED = {"kg": "kg", "ltr": "l", "l": "l", "stk": "stk"}


def hent(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "opbrugt-privat/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def kompakt(p):
    """Kun det, appen og matchningen skal bruge."""
    priser = p.get("prices") or []
    hylde = next((x for x in priser if not x.get("is_campaign")), None)
    kampagne = next((x for x in priser if x.get("is_campaign")), None)
    d = {"id": p["id"], "n": p.get("name") or "", "u": p.get("underline") or ""}
    if hylde:
        d["p"] = hylde["price"]
        if hylde.get("compare_unit_price") is not None:
            d["ep"], d["pr"] = hylde["compare_unit_price"], ENHED.get(hylde.get("compare_unit"), hylde.get("compare_unit"))
    if kampagne:
        d["kp"] = kampagne["price"]
        d["kt"] = (kampagne.get("ending_at") or "")[:10]
    if p.get("is_weight_item"):
        d["vaegt"] = 1
    return d


def hent_katalog():
    varer, side = [], 1
    while True:
        d = hent(f"{API}?per_page=100&page={side}")
        varer += [kompakt(p) for p in d.get("data", [])]
        sidste = d.get("meta", {}).get("pagination", {}).get("last_page", side)
        if side >= sidste:
            break
        side += 1
        time.sleep(0.7)
    RAA.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(RAA, "wt", encoding="utf-8") as f:
        json.dump({"hentet": datetime.now(timezone.utc).isoformat(), "varer": varer}, f, ensure_ascii=False)
    return len(varer), side


def byg():
    with gzip.open(RAA, "rt", encoding="utf-8") as f:
        katalog = json.load(f)
    pr_id = {v["id"]: v for v in katalog["varer"]}
    match = json.loads(MATCH.read_text(encoding="utf-8")) if MATCH.exists() else {}
    ud, mangler = {}, []
    for ingrediens, vid in match.items():
        if ingrediens.startswith("_") or vid is None:
            continue
        v = pr_id.get(vid)
        if not v or v.get("p") is None:
            mangler.append(ingrediens)
            continue
        ud[ingrediens] = {k: v[k] for k in ("id", "n", "u", "p", "ep", "pr", "kp", "kt") if k in v}
    UD.parent.mkdir(parents=True, exist_ok=True)
    UD.write_text(json.dumps({"kaede": "REMA 1000", "hentet": katalog["hentet"][:16], "varer": ud},
                             ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(ud), mangler


def main():
    log = []
    try:
        gammel = not RAA.exists() or (time.time() - RAA.stat().st_mtime) > 28 * 86400
        if "--kun-byg" not in sys.argv and ("--tving" in sys.argv or gammel):
            n, sider = hent_katalog()
            log.append(f"hentede {n} varer fra REMA 1000 ({sider} sider)")
        antal, mangler = byg()
        log.append(f"priser: {antal} ingredienser" + (f", {len(mangler)} REMA-varer findes ikke længere: {', '.join(mangler)}" if mangler else ""))
    except Exception as e:  # noqa: BLE001 – en planlagt kørsel skal skrive fejlen
        log.append(f"FEJL: {type(e).__name__}: {e}")
    print(datetime.now().strftime("%Y-%m-%d %H:%M") + "  " + " | ".join(log))
    if any(x.startswith("FEJL") for x in log):
        sys.exit(1)


if __name__ == "__main__":
    main()
