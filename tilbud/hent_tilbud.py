"""Hent tilbudsaviser fra REMA 1000, Netto, føtex og Lidl via Tjek (eTilbudsavis).

Brug:  python hent_tilbud.py            (tjek for nye aviser, hent dem, byg til_opbrugt/ hvis noget er ændret)
       python hent_tilbud.py --kun-byg  (byg igen ud fra det, der allerede er hentet)

Køres hver dag af en routine, som committer til_opbrugt/ og hentet.json, så Opbrugt-appen på
GitHub Pages får de nye tilbud. Et tjek koster én lille forespørgsel pr. kæde (~5 KB). Der bygges
kun, når en avis er kommet til eller udløbet. De rå aviser ligger ikke i git; mangler en, når der
skal bygges (fx i routinens friske kopi af repoet), hentes den igen.

Filer (i samme mappe som scriptet):
  raa/<kæde>/<start>_<katalog-id>.json.gz   avisen præcis som Tjek leverer den (ikke i git)
  hentet.json                               hvilke aviser der er set (i git)
  aktuelle.json                             alle tilbud, der gælder nu eller senere, i kort form og
                                            matchet mod opskriftbankens ingredienser (ikke i git)
  til_opbrugt/<kæde>.json, meta.json        kompakte filer, som Opbrugt-appen henter (i git)
  til_opbrugt/aviser.txt                    hvilke aviser til_opbrugt/ sidst blev bygget af (i git)
  log.txt                                   én linje pr. kørsel (ikke i git)

Bemærk: Tjeks API er ikke officielt åbent (https://tjek.com/apis-and-sdks). Brug det privat og
sparsomt; scriptet henter kun madaviser og ingen billeder.
"""
import gzip
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    DK = ZoneInfo("Europe/Copenhagen")
except Exception:  # Windows uden tzdata-pakken: brug computerens egen tidszone
    DK = None

MAPPE = Path(__file__).resolve().parent
BANK = MAPPE.parent / "opskriftbank"
API = "https://squid-api.tjek.com/v2"
KAEDER = {"REMA 1000": "11deC", "Netto": "9ba51", "føtex": "bdf5A", "Lidl": "71c90"}
# Kun ugeaviser og weekendaviser: langtløbende kataloger (legetøj, "fast lav pris", magasiner) springes over
MAKS_DAGE = 10
IKKE_MAD = re.compile(r"nonfood|non-food|elektro|legetøj|prosonic|tøj|have|byg|ud af huset", re.I)


def hent(sti):
    req = urllib.request.Request(API + sti, headers={"Accept-Encoding": "gzip", "User-Agent": "opbrugt-privat/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        over_nettet = len(data)  # komprimeret størrelse, dvs. det der faktisk blev hentet
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return json.loads(data), over_nettet


def dato(s):
    return datetime.fromisoformat(s.replace("+0000", "+00:00"))


def hent_avis(kid, ud, katalog, antal=None):
    """Hent alle tilbud i et katalog og gem dem i raa/. Returnerer (tilbud, bytes)."""
    tilbud, offset, n_bytes = [], 0, 0
    while antal is None or offset < antal:
        side, n = hent(f"/offers?catalog_ids={kid}&limit=100&offset={offset}")
        n_bytes += n
        if not side:
            break
        tilbud += side
        offset += 100
        time.sleep(0.5)
        if len(side) < 100:
            break
    ud.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(ud, "wt", encoding="utf-8") as f:
        json.dump({"katalog": katalog, "tilbud": tilbud, "hentet": datetime.now(timezone.utc).isoformat()}, f, ensure_ascii=False)
    return tilbud, n_bytes


def nye_aviser(hentet, log):
    """Returnerer (antal nye aviser, bytes)."""
    bytes_ialt, nye = 0, 0
    for kaede, did in KAEDER.items():
        kataloger, n = hent(f"/catalogs?dealer_ids={did}&limit=24")
        bytes_ialt += n
        for k in kataloger:
            dage = (dato(k["run_till"]) - dato(k["run_from"])).days
            if k["id"] in hentet or not k.get("offer_count") or dage > MAKS_DAGE or IKKE_MAD.search(k.get("label") or ""):
                continue
            ud = MAPPE / "raa" / kaede / f"{k['run_from'][:10]}_{k['id']}.json.gz"
            tilbud, n = hent_avis(k["id"], ud, k, k["offer_count"])
            bytes_ialt += n
            nye += 1
            hentet[k["id"]] = {"kaede": kaede, "label": k.get("label"), "fra": k["run_from"], "til": k["run_till"],
                               "antal": len(tilbud), "fil": ud.relative_to(MAPPE).as_posix()}
            log.append(f"ny avis: {kaede} '{k.get('label')}' {k['run_from'][:10]}–{k['run_till'][:10]}, {len(tilbud)} tilbud")
    return nye, bytes_ialt


def aktive_aviser(hentet):
    nu = datetime.now(timezone.utc)
    return sorted(kid for kid, h in hentet.items() if dato(h["til"]) >= nu)


# ---------- Match mod opskriftbanken ----------
# Tilbud, der aldrig er en råvare til madlavning (forarbejdet, drikkevarer, non-food)
FORARB = re.compile(r"sylte|syltet|juice|saft\b|sovs|syltetøj|marmelade|chips|pålæg|dressing|pickles|snack|slik|\bis\b|kage|chokolade"
                    r"|smoothie|drik|vin\b|øl\b|sodavand|cola|fanta|schweppes|tuborg|pepsi|faxe|kakao|postej|kroket|sushi"
                    r"|opvask|rengøring|klude|børste|dyremad|katte|hunde", re.I)
IKKE_RAAVARE = {"vand"}  # basisvarer, der ikke giver mening at følge på tilbud
# "laks med spinat", "tun i olie": ingrediensen er tilbehør til en anden vare
FORAN = re.compile(r"(?:\bi|\bmed)\s+$")


def ingredienskatalog():
    p = BANK / "ingredienser.json"
    if not p.exists():
        return []
    kat = {k: v for k, v in json.load(open(p, encoding="utf-8")).items() if not k.startswith("_")}
    termer = []
    for vid, v in kat.items():
        if v.get("krydderiblanding") or vid in IKKE_RAAVARE:
            continue  # HelloFresh' egne blandinger findes ikke i butikkerne
        for t in [v["navn"], *v.get("synonymer", [])]:
            t = t.lower().strip()
            if len(t) >= 3:
                termer.append((t, vid))
    termer.sort(key=lambda x: -len(x[0]))
    return [(re.compile(r"(?<![a-zæøå])" + re.escape(t) + r"(?:e|er|r|n|ne|s)?(?![a-zæøå])"), vid) for t, vid in termer]


def match(overskrift, termer):
    o = overskrift.lower()
    if FORARB.search(o):
        return None
    for rx, vid in termer:
        for m in rx.finditer(o):
            if not FORAN.search(o[:m.start()]):
                return vid
    return None


def enhedspris(t):
    """Pris pr. kg, l eller stk ud fra Tjeks mængdefelter."""
    q, pris = t.get("quantity") or {}, (t.get("pricing") or {}).get("price")
    if not pris or not q.get("unit") or not q.get("size"):
        return None, None
    si = q["unit"].get("si") or {}
    stk = (q.get("pieces") or {}).get("from") or 1
    stoerrelse = q["size"].get("from") or 0
    if q["unit"].get("symbol") == "pcs":
        return round(pris / max(stoerrelse * stk, 1), 2), "stk"
    if si.get("symbol") in ("kg", "l") and stoerrelse:
        maengde = stoerrelse * si.get("factor", 1) * stk
        return (round(pris / maengde, 2), si["symbol"]) if maengde else (None, None)
    return None, None


def byg(hentet, log):
    nu = datetime.now(timezone.utc)
    termer = ingredienskatalog()
    ud, matchet, set_ = [], 0, set()
    for kid, h in sorted(hentet.items(), key=lambda x: x[1]["fra"]):
        if dato(h["til"]) < nu:
            continue
        fil = MAPPE / h["fil"]
        if not fil.exists():
            _, n = hent_avis(kid, fil, {"id": kid, "label": h["label"], "run_from": h["fra"], "run_till": h["til"]})
            log.append(f"hentede {h['kaede']} '{h['label']}' igen ({n // 1024} KB)")
        with gzip.open(fil, "rt", encoding="utf-8") as f:
            raa = json.load(f)
        for t in raa["tilbud"]:
            # samme tilbud i to aviser (fx Lidls uge- og weekendavis) tæller kun én gang
            noegle = (h["kaede"], t["heading"], (t.get("pricing") or {}).get("price"))
            if noegle in set_:
                continue
            set_.add(noegle)
            ep, eh = enhedspris(t)
            q = t.get("quantity") or {}
            r = {
                # datoerne i dansk tid: Tjek angiver UTC, så et tilbud fra lørdag kl. 00 står som fredag kl. 22
                "kaede": h["kaede"], "avis": h["label"], "fra": lokal_dato(t["run_from"]), "til": lokal_dato(t["run_till"]),
                "overskrift": t["heading"], "beskrivelse": (t.get("description") or "").strip(),
                "pris": (t.get("pricing") or {}).get("price"), "foerpris": (t.get("pricing") or {}).get("pre_price"),
                "maengde": {"fra": (q.get("size") or {}).get("from"), "til": (q.get("size") or {}).get("to"),
                            "enhed": (q.get("unit") or {}).get("symbol"), "stk": (q.get("pieces") or {}).get("from")},
                "enhedspris": ep, "pr": eh, "side": t.get("catalog_page"), "id": t["id"],
            }
            vid = match(t["heading"], termer)
            if vid:
                r["ingrediens"] = vid
                matchet += 1
            ud.append(r)
    data = {"opdateret": nu.isoformat(timespec="minutes"), "kaeder": list(KAEDER), "antal": len(ud), "matchet": matchet,
            "aviser": [h for h in hentet.values() if dato(h["til"]) >= nu], "tilbud": ud}
    (MAPPE / "aktuelle.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    til_opbrugt(data)
    return len(ud), matchet


def lokal_dato(s):
    return dato(s).astimezone(DK).date().isoformat()


def maengde_tekst(m):
    if not m.get("fra") or not m.get("enhed"):
        return ""
    enhed = {"pcs": "stk"}.get(m["enhed"], m["enhed"])
    stoer = f"{m['fra']:g}" + (f"-{m['til']:g}" if m.get("til") and m["til"] != m["fra"] else "")
    return (f"{m['stk']}x" if m.get("stk") and m["stk"] > 1 else "") + f"{stoer} {enhed}"


OPBRUGT_ID = {"REMA 1000": "rema-1000", "Netto": "netto", "føtex": "foetex", "Lidl": "lidl"}


def til_opbrugt(data):
    """Kompakte filer til Opbrugt-appen: én pr. kæde + meta."""
    mappe = MAPPE / "til_opbrugt"
    mappe.mkdir(exist_ok=True)
    pr_kaede = {k: [] for k in KAEDER}
    for t in data["tilbud"]:
        x = {"o": t["overskrift"], "p": t["pris"], "f": t["fra"], "t": t["til"]}
        b = " · ".join(l.strip() for l in t["beskrivelse"].splitlines() if l.strip())[:110]
        if b: x["b"] = b
        if t.get("foerpris"): x["fp"] = t["foerpris"]
        if t.get("enhedspris"): x["ep"], x["pr"] = t["enhedspris"], t["pr"]
        m = maengde_tekst(t["maengde"])
        if m: x["m"] = m
        if t.get("ingrediens"): x["i"] = t["ingrediens"]
        pr_kaede[t["kaede"]].append(x)
    docs = {}
    for k, liste in pr_kaede.items():
        docs[OPBRUGT_ID[k]] = {"kaede": k, "opdateret": data["opdateret"], "tilbud": liste}
    docs["meta"] = {"opdateret": data["opdateret"], "kaeder": [{"id": OPBRUGT_ID[k], "navn": k} for k in KAEDER],
                    "aviser": [{"kaede": a["kaede"], "label": a["label"], "fra": lokal_dato(a["fra"]), "til": lokal_dato(a["til"])}
                               for a in sorted(data["aviser"], key=lambda a: (a["kaede"], a["fra"]))]}
    for doc_id, d in docs.items():
        tekst = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        (mappe / f"{doc_id}.json").write_text(tekst, encoding="utf-8")


def main():
    hentet_fil = MAPPE / "hentet.json"
    hentet = json.loads(hentet_fil.read_text(encoding="utf-8")) if hentet_fil.exists() else {}
    bygget_fil = MAPPE / "til_opbrugt" / "aviser.txt"
    log = []
    try:
        nye = 0
        if "--kun-byg" not in sys.argv:
            nye, n_bytes = nye_aviser(hentet, log)
            hentet_fil.write_text(json.dumps(hentet, ensure_ascii=False, indent=1), encoding="utf-8")
            log.append(f"hentet {n_bytes // 1024} KB")
        aktive = "\n".join(aktive_aviser(hentet))
        bygget = bygget_fil.read_text(encoding="utf-8").strip() if bygget_fil.exists() else None
        if "--kun-byg" in sys.argv or nye or aktive != bygget:
            antal, matchet = byg(hentet, log)
            bygget_fil.write_text(aktive, encoding="utf-8")
            log.append(f"til_opbrugt: {antal} tilbud, {matchet} matchet mod opskriftbanken")
        else:
            log.append("til_opbrugt: uændret")
    except Exception as e:  # noqa: BLE001 – en planlagt kørsel skal skrive fejlen i loggen
        log.append(f"FEJL: {type(e).__name__}: {e}")
    linje = datetime.now().strftime("%Y-%m-%d %H:%M") + "  " + " | ".join(log)
    with open(MAPPE / "log.txt", "a", encoding="utf-8") as f:
        f.write(linje + "\n")
    print(linje)
    if any(x.startswith("FEJL") for x in log):
        sys.exit(1)


if __name__ == "__main__":
    main()
