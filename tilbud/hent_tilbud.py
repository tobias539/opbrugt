"""Hent tilbudsaviser fra REMA 1000, Netto, føtex og Lidl via Tjek (eTilbudsavis).

Brug:  python hent_tilbud.py            (tjek for nye aviser, hent dem, byg aktuelle.json)
       python hent_tilbud.py --kun-byg  (byg aktuelle.json igen ud fra det, der allerede er hentet)
       python hent_tilbud.py --sendt    (marker til_opbrugt/ som lagt i Opbrugts database)

Køres gerne hver dag: et tjek koster én lille forespørgsel pr. kæde (~5 KB). En avis hentes kun
første gang, den dukker op, så I altid har næste uges tilbud, så snart de er udgivet.

Filer (i samme mappe som scriptet):
  raa/<kæde>/<start>_<katalog-id>.json.gz   avisen præcis som Tjek leverer den (katalog + alle tilbud)
  hentet.json                               hvilke aviser der allerede er hentet
  aktuelle.json                             alle tilbud, der gælder nu eller senere, i kort form og
                                            matchet mod opskriftbankens ingredienser
  til_opbrugt/<kæde>.json, meta.json        kompakte dokumenter til Opbrugt-appens database (samling "tilbud");
                                            linjen "OPBRUGT: skal opdateres" betyder, at de er ændret
  log.txt                                   én linje pr. kørsel

Bemærk: Tjeks API er ikke officielt åbent (https://tjek.com/apis-and-sdks). Brug det privat og
sparsomt; scriptet henter kun madaviser og ingen billeder.
"""
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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


def nye_aviser(hentet, log):
    bytes_ialt = 0
    for kaede, did in KAEDER.items():
        kataloger, n = hent(f"/catalogs?dealer_ids={did}&limit=24")
        bytes_ialt += n
        for k in kataloger:
            dage = (dato(k["run_till"]) - dato(k["run_from"])).days
            if k["id"] in hentet or not k.get("offer_count") or dage > MAKS_DAGE or IKKE_MAD.search(k.get("label") or ""):
                continue
            tilbud, offset = [], 0
            while offset < k["offer_count"]:
                side, n = hent(f"/offers?catalog_ids={k['id']}&limit=100&offset={offset}")
                bytes_ialt += n
                if not side:
                    break
                tilbud += side
                offset += 100
                time.sleep(0.5)
            ud = MAPPE / "raa" / kaede / f"{k['run_from'][:10]}_{k['id']}.json.gz"
            ud.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(ud, "wt", encoding="utf-8") as f:
                json.dump({"katalog": k, "tilbud": tilbud, "hentet": datetime.now(timezone.utc).isoformat()}, f, ensure_ascii=False)
            hentet[k["id"]] = {"kaede": kaede, "label": k.get("label"), "fra": k["run_from"], "til": k["run_till"],
                               "antal": len(tilbud), "fil": ud.relative_to(MAPPE).as_posix()}
            log.append(f"ny avis: {kaede} '{k.get('label')}' {k['run_from'][:10]}–{k['run_till'][:10]}, {len(tilbud)} tilbud")
    return bytes_ialt


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


def byg(hentet):
    nu = datetime.now(timezone.utc)
    termer = ingredienskatalog()
    ud, matchet, set_ = [], 0, set()
    for kid, h in sorted(hentet.items(), key=lambda x: x[1]["fra"]):
        if dato(h["til"]) < nu:
            continue
        with gzip.open(MAPPE / h["fil"], "rt", encoding="utf-8") as f:
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
    skal_sendes = til_opbrugt(data)
    return len(ud), matchet, skal_sendes


def lokal_dato(s):
    return dato(s).astimezone().date().isoformat()


def maengde_tekst(m):
    if not m.get("fra") or not m.get("enhed"):
        return ""
    enhed = {"pcs": "stk"}.get(m["enhed"], m["enhed"])
    stoer = f"{m['fra']:g}" + (f"-{m['til']:g}" if m.get("til") and m["til"] != m["fra"] else "")
    return (f"{m['stk']}x" if m.get("stk") and m["stk"] > 1 else "") + f"{stoer} {enhed}"


OPBRUGT_ID = {"REMA 1000": "rema-1000", "Netto": "netto", "føtex": "foetex", "Lidl": "lidl"}


def til_opbrugt(data):
    """Kompakte dokumenter til Opbrugt-appens database: ét pr. kæde (under 256 KB hver) + meta.
    Returnerer True, hvis indholdet er ændret siden sidste afsendelse (se --sendt)."""
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
    indhold = ""
    for doc_id, d in docs.items():
        tekst = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        assert len(tekst.encode()) < 250_000, f"{doc_id} er for stort til databasen"
        (mappe / f"{doc_id}.json").write_text(tekst, encoding="utf-8")
        if doc_id != "meta":
            indhold += json.dumps(d["tilbud"], ensure_ascii=False, sort_keys=True)
    fingeraftryk = hashlib.sha256(indhold.encode()).hexdigest()[:16]
    (mappe / "fingeraftryk.txt").write_text(fingeraftryk, encoding="utf-8")
    sendt = (mappe / "sendt.txt").read_text(encoding="utf-8").strip() if (mappe / "sendt.txt").exists() else ""
    return fingeraftryk != sendt


def main():
    hentet_fil = MAPPE / "hentet.json"
    hentet = json.loads(hentet_fil.read_text(encoding="utf-8")) if hentet_fil.exists() else {}
    if "--sendt" in sys.argv:
        # kaldes af den planlagte opgave, når dokumenterne er lagt i Opbrugts database
        mappe = MAPPE / "til_opbrugt"
        (mappe / "sendt.txt").write_text((mappe / "fingeraftryk.txt").read_text(encoding="utf-8"), encoding="utf-8")
        print("Opbrugt markeret som opdateret.")
        return
    log = []
    try:
        if "--kun-byg" not in sys.argv:
            n_bytes = nye_aviser(hentet, log)
            hentet_fil.write_text(json.dumps(hentet, ensure_ascii=False, indent=1), encoding="utf-8")
            log.append(f"hentet {n_bytes // 1024} KB")
        antal, matchet, skal_sendes = byg(hentet)
        log.append(f"aktuelle.json: {antal} tilbud, {matchet} matchet mod opskriftbanken")
        log.append("OPBRUGT: skal opdateres" if skal_sendes else "OPBRUGT: uændret")
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
