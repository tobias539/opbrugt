"""Hent hyldepriser fra kæderne og lav små prisfiler til Opbrugt-appen.

Brug:  python priser/hent_priser.py              (hent det, der er over 4 uger gammelt, og byg prisfilerne)
       python priser/hent_priser.py --tving      (hent alt nu)
       python priser/hent_priser.py --kun-byg    (byg prisfilerne ud fra det, der allerede er hentet)

Kæder:
  REMA 1000  webshoppens API (api.digital.rema1000.dk): hele sortimentet (ca. 4.000 varer) med hyldepriser.
             Ikke officielt åbent, så det hentes højst én gang om måneden.
  Netto,     Salling Groups udvikler-API (kræver nøgle i salling-noegle.txt, ikke i git; kun til
  føtex      uddannelse og ikke-kommerciel brug). Listen over de ca. 1.000 mest købte varer i kædens
             webshop giver varer og stregkoder; prisen slås op pr. stregkode i én bestemt butik.
             Kun matchede varer slås op (ca. 100 opslag pr. kæde om måneden).
  Lidl, 365discount: har ingen offentlige hyldepriser. Appen bruger REMA 1000's priser for dem.

Filer pr. kæde (<k> = rema-1000, netto, foetex):
  raa/<k>.json.gz            kædens varer, kompakt (ikke i git)
  raa/<k>-priser.json        senest hentede pris pr. stregkode (kun Salling, ikke i git)
  match-<k>.json             hvilken vare hver ingrediens i opskriftbanken svarer til (i git, rettes i hånden)
  til_opbrugt/<k>.json       hyldepris pr. ingrediens, som appen henter (i git)
"""
import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAPPE = Path(__file__).resolve().parent
NOEGLE = MAPPE / "salling-noegle.txt"
AKTUELLE_TILBUD = MAPPE.parent / "tilbud" / "aktuelle.json"
MAANED = 28 * 86400
# Salling Group blokerer IP-adressen ved for mange opslag. Derfor højst 15 prisopslag pr. kørsel med god
# pause imellem; den daglige opgave tager resten de følgende dage. Ved 429 stoppes, og der ventes.
SALLING_MAKS, SALLING_PAUSE = 15, 8
SALLING_STATUS = MAPPE / "raa" / "salling-status.json"
ENHED = {"kg": "kg", "ltr": "l", "l": "l", "stk": "stk", "g": "kg", "ml": "l"}

KAEDER = {
    "rema-1000": {"navn": "REMA 1000", "type": "rema"},
    # Butikken bruges kun til prisopslag; Netto og føtex har (næsten) samme priser i hele landet.
    "netto": {"navn": "Netto", "type": "salling", "feed": "nettoplus", "butik": "0b52d54b-66e1-4d8c-a4a4-e243b5120946"},
    "foetex": {"navn": "føtex", "type": "salling", "feed": "foetexplus", "butik": "d6abf195-312b-4818-8933-bda8ecdd9fbd"},  # føtex Aalborg
}


class UdenNoegleVedViderestilling(urllib.request.HTTPRedirectHandler):
    """Salling sender listerne videre til en tidsbegrænset fil-adresse; nøglen må ikke sendes med dertil."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        ny = super().redirect_request(req, fp, code, msg, headers, newurl)
        if ny is not None:
            ny.remove_header("Authorization")
        return ny


AABNER = urllib.request.build_opener(UdenNoegleVedViderestilling)


def hent(url, noegle=None):
    h = {"Accept": "application/json", "User-Agent": "opbrugt-privat/1.0"}
    if noegle:
        h["Authorization"] = "Bearer " + noegle
    with AABNER.open(urllib.request.Request(url, headers=h), timeout=60) as r:
        return json.loads(r.read())


def gammel(sti):
    return not sti.exists() or (time.time() - sti.stat().st_mtime) > MAANED


def gem_katalog(k, varer):
    sti = MAPPE / "raa" / f"{k}.json.gz"
    sti.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(sti, "wt", encoding="utf-8") as f:
        json.dump({"hentet": datetime.now(timezone.utc).isoformat(), "varer": varer}, f, ensure_ascii=False)


def laes_katalog(k):
    with gzip.open(MAPPE / "raa" / f"{k}.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def laes_match(k):
    sti = MAPPE / f"match-{k}.json"
    m = json.loads(sti.read_text(encoding="utf-8")) if sti.exists() else {}
    return {i: v for i, v in m.items() if not i.startswith("_") and v is not None}


def skriv(k, hentet, varer):
    ud = MAPPE / "til_opbrugt" / f"{k}.json"
    ud.parent.mkdir(parents=True, exist_ok=True)
    ud.write_text(json.dumps({"kaede": KAEDER[k]["navn"], "hentet": hentet[:16], "varer": varer},
                             ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


# ---------- REMA 1000 ----------
def rema_kompakt(p):
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
    return d


def rema_hent():
    varer, side = [], 1
    while True:
        d = hent(f"https://api.digital.rema1000.dk/api/v3/products?per_page=100&page={side}")
        varer += [rema_kompakt(p) for p in d.get("data", [])]
        if side >= d.get("meta", {}).get("pagination", {}).get("last_page", side):
            break
        side += 1
        time.sleep(0.7)
    gem_katalog("rema-1000", varer)
    return f"hentede {len(varer)} varer fra REMA 1000"


def rema_byg():
    katalog = laes_katalog("rema-1000")
    pr_id = {v["id"]: v for v in katalog["varer"]}
    ud, mangler = {}, []
    for ingrediens, vid in laes_match("rema-1000").items():
        v = pr_id.get(vid)
        if not v or v.get("p") is None:
            mangler.append(ingrediens)
            continue
        ud[ingrediens] = {x: v[x] for x in ("id", "n", "u", "p", "ep", "pr", "kp", "kt") if x in v}
    skriv("rema-1000", katalog["hentet"], ud)
    return len(ud), mangler


# ---------- Salling Group (Netto, føtex) ----------
def salling_hent_liste(k, noegle):
    feed = hent(f"https://api.sallinggroup.com/v1/recommendations/most-bought/{KAEDER[k]['feed']}/feed", noegle)
    varer = []
    for p in feed:
        if not p.get("gtins"):
            continue
        enhed = (p.get("contentsUnit") or "").lower()
        varer.append({"id": p["gtins"][0], "n": p.get("name") or p.get("description") or "",
                      "u": f"{p.get('contents') or ''} {enhed}".strip() + (f" / {p['brand']}" if p.get("brand") else ""),
                      "pr": ENHED.get(enhed)})
    gem_katalog(k, varer)
    return f"hentede {len(varer)} varer fra {KAEDER[k]['navn']}s liste"


def ligner_tilbud(kaede_navn, ingrediens, ep, pr):
    """Er prisen nok en tilbudspris? (et aktuelt tilbud på samme ingrediens med næsten samme pris pr. enhed)"""
    if not AKTUELLE_TILBUD.exists():
        return False
    for t in json.loads(AKTUELLE_TILBUD.read_text(encoding="utf-8")).get("tilbud", []):
        if (t.get("kaede", "").lower() == kaede_navn.lower() and t.get("ingrediens") == ingrediens
                and t.get("pr") == pr and t.get("enhedspris") and abs(ep - t["enhedspris"]) <= 0.1 * t["enhedspris"]):
            return True
    return False


def salling_blokeret():
    s = json.loads(SALLING_STATUS.read_text(encoding="utf-8")) if SALLING_STATUS.exists() else {}
    return s.get("blokeret_til", 0) > time.time()


def salling_hent_priser(k, noegle, tving, kvote):
    """Slå prisen op for de matchede stregkoder, der mangler eller er over en måned gamle (ældste først).
    Returnerer (antal opslag, om Salling har blokeret)."""
    sti = MAPPE / "raa" / f"{k}-priser.json"
    gemt = json.loads(sti.read_text(encoding="utf-8")) if sti.exists() else {}
    butik, nu, n = KAEDER[k]["butik"], time.time(), 0
    koe = [(i, e) for i, e in laes_match(k).items()
           if tving or not gemt.get(e) or gemt[e].get("p") is None or nu - gemt[e].get("t", 0) >= MAANED]
    koe.sort(key=lambda x: gemt.get(x[1], {}).get("t", 0))
    blokeret = False
    for ingrediens, ean in koe[:kvote]:
        g = gemt.get(ean)
        if n:
            time.sleep(SALLING_PAUSE)
        try:
            d = hent(f"https://api.sallinggroup.com/v2/products/{ean}?storeId={butik}", noegle)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                vent = int(e.headers.get("Retry-After") or 3600)
                SALLING_STATUS.write_text(json.dumps({"blokeret_til": time.time() + vent}), encoding="utf-8")
                blokeret = True
                break
            gemt[ean] = {**(g or {}), "fejl": e.code, "t": nu}
            n += 1
            continue
        ins = d.get("instore") or {}
        if ins.get("price") is None:
            continue
        pr = ENHED.get((ins.get("unit") or "").lower())
        ny = {"n": ins.get("name") or "", "u": f"{ins.get('contents') or ''} {ins.get('contentsUnit') or ''}".strip(),
              "p": ins["price"], "ep": ins.get("unitPrice"), "pr": pr, "t": nu}
        if g and pr and ny["ep"] and ligner_tilbud(KAEDER[k]["navn"], ingrediens, ny["ep"], pr):
            gemt[ean] = {**g, "t": nu}  # behold den gamle normalpris
        else:
            gemt[ean] = ny
        n += 1
    sti.parent.mkdir(parents=True, exist_ok=True)
    sti.write_text(json.dumps(gemt, ensure_ascii=False, indent=0), encoding="utf-8")
    return n, blokeret, max(0, len(koe) - n)


def salling_byg(k):
    sti = MAPPE / "raa" / f"{k}-priser.json"
    gemt = json.loads(sti.read_text(encoding="utf-8")) if sti.exists() else {}
    ud, mangler = {}, []
    for ingrediens, ean in laes_match(k).items():
        g = gemt.get(ean)
        if not g or g.get("p") is None:
            mangler.append(ingrediens)
            continue
        ud[ingrediens] = {"id": ean, **{x: g[x] for x in ("n", "u", "p", "ep", "pr") if g.get(x) is not None}}
    skriv(k, datetime.now(timezone.utc).isoformat(), ud)
    return len(ud), mangler


def main():
    log = []
    tving, kun_byg = "--tving" in sys.argv, "--kun-byg" in sys.argv
    noegle = NOEGLE.read_text(encoding="utf-8").strip() if NOEGLE.exists() else None
    kvote = SALLING_MAKS
    for k, c in KAEDER.items():
        try:
            if c["type"] == "rema":
                if not kun_byg and (tving or gammel(MAPPE / "raa" / f"{k}.json.gz")):
                    log.append(rema_hent())
                antal, mangler = rema_byg()
            else:
                if not noegle or not c.get("butik"):
                    log.append(f"{c['navn']}: springes over ({'ingen nøgle' if not noegle else 'ingen butik valgt'})")
                    continue
                if salling_blokeret():
                    log.append(f"{c['navn']}: Salling har midlertidigt blokeret opslag, prøver igen senere")
                elif not kun_byg:
                    if tving or gammel(MAPPE / "raa" / f"{k}.json.gz"):
                        log.append(salling_hent_liste(k, noegle))
                    if kvote > 0:
                        n, blokeret, rest = salling_hent_priser(k, noegle, tving, kvote)
                        kvote -= n
                        if n or rest:
                            log.append(f"slog {n} priser op i {c['navn']}" + (f", {rest} venter til de næste dage" if rest else ""))
                        if blokeret:
                            log.append("Salling svarede 'for mange forespørgsler'; stopper og venter")
                antal, mangler = salling_byg(k)
            log.append(f"{c['navn']}: {antal} priser" + ((f" ({len(mangler)} mangler: {', '.join(mangler)})" if len(mangler) <= 8 else f" ({len(mangler)} mangler endnu)") if mangler else ""))
        except Exception as e:  # noqa: BLE001 – en planlagt kørsel skal skrive fejlen
            log.append(f"FEJL i {c['navn']}: {type(e).__name__}: {e}")
    print(datetime.now().strftime("%Y-%m-%d %H:%M") + "  " + " | ".join(log))
    if any(x.startswith("FEJL") for x in log):
        sys.exit(1)


if __name__ == "__main__":
    main()
