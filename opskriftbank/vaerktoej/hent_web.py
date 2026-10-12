"""Hent opskrifter fra nettet: Valdemarsro, MENY og andre sider, der har opskriften som data (schema.org/Recipe).

Brug:
  python vaerktoej/hent_web.py <url> [<url> ...] [--antal N] [--igen]
      <url> kan være én opskrift eller en oversigt:
        https://www.valdemarsro.dk/aftensmad/   bladrer gennem siderne i kategorien
        https://meny.dk/opskrifter               tager tilfældige hovedretter fra MENY's liste over alle opskrifter
      --antal N  højst N nye opskrifter pr. oversigt (standard 20)
      --igen     hent også opskrifter, der allerede er hentet
  python vaerktoej/hent_web.py --status
      viser hentede opskrifter, der endnu ikke er blevet til en opskrift i opskrifter/,
      og de ingredienser, der ikke kunne findes i ingredienser.json. Forslagene i filerne
      opdateres samtidig, så nye ingredienser i kataloget kommer med.

For hver opskrift gemmes kilder/web/<side>/<slug>.json med kildens egne data og et forslag til hver
ingredienslinje: mængde, enhed og ingrediens-id fra ingredienser.json. Selve opskriften (opskrifter/<id>.json)
laves bagefter af Claude efter reglerne i README under "Tilføj opskrifter fra nettet".
kilder/web/ er udeladt fra git, fordi den indeholder kildens egen tekst.

Værktøjet siger ærligt, hvem det er (User-Agent), følger robots.txt og venter lidt mellem hvert opslag.
"""
import html
import json
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

BANK = Path(__file__).resolve().parent.parent
UD = BANK / "kilder" / "web"
UA = "Opbrugt-opskriftimport/1.0 (privat madapp; https://github.com/tobias539/opbrugt)"
PAUSE = 1.5
SIDENAVNE = {"valdemarsro.dk": "Valdemarsro", "meny.dk": "MENY"}

# ---------- Hent ----------

_robots, _sidst = {}, [0.0]


def hent(url):
    """Siden som tekst. Følger robots.txt og holder en pause mellem opslag."""
    p = urllib.parse.urlparse(url)
    vaert = f"{p.scheme}://{p.netloc}"
    if vaert not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(vaert + "/robots.txt", headers={"User-Agent": UA})
            rp.parse(urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace").splitlines())
        except (urllib.error.URLError, TimeoutError):
            rp.parse([])
        _robots[vaert] = rp
    if not _robots[vaert].can_fetch(UA, url):
        raise PermissionError(f"robots.txt tillader ikke {url}")
    vent = PAUSE - (time.time() - _sidst[0])
    if vent > 0:
        time.sleep(vent)
    _sidst[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "da"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def side_af(url):
    netloc = urllib.parse.urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


# ---------- Læs opskriften på siden ----------

def iso_min(v):
    """'PT1H20M' -> 80. Ugyldig eller tom -> None."""
    m = re.fullmatch(r"P(?:T)?(?:(\d+)H)?(?:(\d+)M)?(?:\d+S)?", str(v or "").strip())
    if not m or not any(m.groups()):
        return None
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def tekst(v):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(v or "")))).strip()


def find_ld_recipe(s):
    for blok in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', s, re.S | re.I):
        try:
            data = json.loads(blok)
        except json.JSONDecodeError:
            continue
        stak = [data]
        while stak:
            x = stak.pop()
            if isinstance(x, list):
                stak.extend(x)
            elif isinstance(x, dict):
                t = x.get("@type")
                if t == "Recipe" or (isinstance(t, list) and "Recipe" in t):
                    return x
                stak.extend(v for k, v in x.items() if k in ("@graph", "mainEntity", "itemListElement"))
    return None


def ld_trin(instr):
    """recipeInstructions fra JSON-LD -> [{afsnit, tekst}]"""
    ud = []

    def gaa(x, afsnit=None):
        if isinstance(x, str):
            for del_ in re.split(r"\n+", x):
                if tekst(del_):
                    ud.append({"afsnit": afsnit, "tekst": tekst(del_)})
        elif isinstance(x, list):
            for y in x:
                gaa(y, afsnit)
        elif isinstance(x, dict):
            if x.get("@type") == "HowToSection":
                gaa(x.get("itemListElement", []), tekst(x.get("name")) or afsnit)
            else:
                gaa(x.get("text") or x.get("name") or "", afsnit)

    gaa(instr)
    return ud


class Mikrodata(HTMLParser):
    """Læser opskrifter, der er mærket op med itemprop (fx Valdemarsro)."""
    TOMME = {"br", "img", "input", "meta", "link", "hr", "source", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.aabne, self.felter, self.ingredienser, self.trin = [], {}, [], []
        self.afsnit = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.TOMME:
            if tag == "br":
                self._ny_blok()
            if tag == "meta" and a.get("itemprop") and a.get("content"):
                self.felter.setdefault(a["itemprop"], tekst(a["content"]))
            return
        prop = a.get("itemprop")
        if "ingredient-header" in (a.get("class") or ""):
            prop = "_afsnit"
        if tag in ("p", "li", "div") and self.aabne and self.aabne[-1][0] == "recipeInstructions":
            self._ny_blok()
        self.aabne.append((prop, tag, [""]) if prop else (None, tag, None))

    def _ny_blok(self):
        for prop, _, buf in self.aabne:
            if prop == "recipeInstructions" and buf[-1].strip():
                buf.append("")

    def handle_endtag(self, tag):
        for i in range(len(self.aabne) - 1, -1, -1):
            if self.aabne[i][1] == tag:
                for prop, _, buf in self.aabne[i:][::-1]:
                    if prop:
                        self._luk(prop, buf)
                del self.aabne[i:]
                return

    def handle_data(self, data):
        for prop, _, buf in self.aabne:
            if prop:
                buf[-1] += data

    def _luk(self, prop, buf):
        if prop == "recipeIngredient":
            if tekst(buf[0]):  # siderne har somme tider tomme linjer
                self.ingredienser.append({"afsnit": self.afsnit, "tekst": tekst(buf[0])})
        elif prop == "_afsnit":
            self.afsnit = tekst(buf[0]) or None
        elif prop == "recipeInstructions":
            self.trin += [{"afsnit": None, "tekst": tekst(b)} for b in buf if tekst(b)]
        else:
            self.felter.setdefault(prop, tekst(" ".join(buf)))


def laes_opskrift(s, url):
    """Opskriften på siden som dict, eller None hvis siden ikke har en."""
    ld = find_ld_recipe(s)
    if ld:
        ing = [{"afsnit": None, "tekst": tekst(x)} for x in ld.get("recipeIngredient", []) if tekst(x)]
        trin = ld_trin(ld.get("recipeInstructions", []))
        felter = {
            "name": tekst(ld.get("name")), "description": tekst(ld.get("description")),
            "recipeYield": ld.get("recipeYield"), "totalTime": ld.get("totalTime"),
            "cookTime": ld.get("cookTime"), "prepTime": ld.get("prepTime"),
            "recipeCategory": ld.get("recipeCategory"), "recipeCuisine": ld.get("recipeCuisine"),
            "keywords": ld.get("keywords"), "nutrition": ld.get("nutrition"),
        }
    else:
        p = Mikrodata()
        p.feed(s)
        if not p.ingredienser:
            return None
        ing, trin, felter = p.ingredienser, p.trin, p.felter
        # itemprop="name" bruges også om forfatter og udgiver, så overskriften tæller først
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        if h1 and tekst(h1.group(1)):
            felter["name"] = tekst(h1.group(1))
    stats = {tekst(k).lower(): tekst(v) for k, v in
             re.findall(r'recipe-stat-label">(.*?)</span>\s*<strong[^>]*>(.*?)</strong>', s, re.S)}

    def liste(v):
        if not v:
            return []
        v = v if isinstance(v, list) else re.split(r"\s*,\s*", str(v))
        return [tekst(x) for x in v if tekst(x)]

    yield_ = felter.get("recipeYield")
    yield_ = yield_[0] if isinstance(yield_, list) and yield_ else yield_
    m = re.search(r"\d+", str(yield_ or ""))
    tider = [t for t in (iso_min(felter.get(k)) for k in ("totalTime", "cookTime", "prepTime")) if t]
    side = side_af(url)
    o = {
        "url": url,
        "side": side,
        "navn": SIDENAVNE.get(side, side),
        "hentet": date.today().isoformat(),
        "titel": felter.get("name") or tekst((re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S) or [None, ""])[1]),
        "beskrivelse": felter.get("description") or "",
        "portioner": int(m.group()) if m else None,
        "portioner_tekst": tekst(yield_) or None,
        # Kilderne bytter tit om på felterne, så den længste tid er den samlede
        "tid_i_alt_min": max(tider) if tider else None,
        "kategori": liste(felter.get("recipeCategory")) + liste(felter.get("recipeCuisine")),
        "noegleord": liste(felter.get("keywords")),
        "kan_fryses": {"ja": True, "nej": False}.get(stats.get("kan fryses", "").lower()),
        "holdbarhed": stats.get("holdbarhed"),
        "ingredienser": [dict(x, **tolk_linje(x["tekst"])) for x in ing],
        "trin": trin,
    }
    if felter.get("nutrition"):
        o["naering_kilde"] = felter["nutrition"]
    return o


# ---------- Ingredienslinjer ----------

BROEK = {"½": ".5", "¼": ".25", "¾": ".75", "⅓": ".33", "⅔": ".67", "⅛": ".125"}
ENHEDER = {
    "g": "g", "gr": "g", "gram": "g", "kg": "kg", "kilo": "kg", "ml": "ml", "cl": "cl", "dl": "dl",
    "l": "l", "liter": "l", "tsk": "tsk", "tesk": "tsk", "teskefuld": "tsk", "spsk": "spsk", "skefuld": "spsk",
    "stk": "stk", "styk": "stk", "fed": "fed", "pose": "pose", "poser": "pose", "dåse": "daase",
    "dåser": "daase", "ds": "daase", "pakke": "pakke", "pakker": "pakke", "pk": "pakke", "nip": "nip",
    "knivspids": "nip", "knsp": "nip",
}
# Ord, der er en enhed, men ikke findes i skemaet. De står i 'enhed_tekst', og Claude vælger en enhed.
ANDRE_ENHEDER = {"bundt", "bdt", "håndfuld", "håndfulde", "skive", "skiver", "glas", "bakke", "bakker", "stilk",
                 "stilke", "stængel", "stængler", "blad", "blade", "kvist", "kviste", "potte", "potter", "net", "bøtte", "flaske", "spiseske"}


def tal(t):
    t = t.replace(",", ".")
    if "/" in t:
        a, b = t.split("/", 1)
        return float(a) / float(b) if float(b) else None
    return float(t)


def tolk_linje(linje):
    """'2 fed hvidløg, finthakket' -> mængde, enhed, navn, note, valgfri. Mængde er None ved 'efter smag'."""
    t = linje.strip()
    for k, v in BROEK.items():
        t = re.sub(rf"(\d)\s*{k}", lambda m: m.group(1) + v, t).replace(k, "0" + v)
    valgfri = bool(re.match(r"(?i)\(?evt\.?\)?\s", t)) or "(evt" in t.lower()
    t = re.sub(r"(?i)^\(?evt\.?\)?\s*|^ca\.?\s*|^cirka\s*", "", t).strip()
    maengde = interval = None
    m = re.match(r"(\d+(?:[.,/]\d+)?)(?:\s*[-–]\s*(\d+(?:[.,/]\d+)?))?\s*", t)
    if m:
        maengde = tal(m.group(1))
        if m.group(2):
            interval = f"{m.group(1)}-{m.group(2)}"
        t = t[m.end():]
    enhed = enhed_tekst = None
    m = re.match(r"([a-zæøåA-ZÆØÅ]+)\.?(?=\s|$)", t)
    if m and maengde is not None:
        w = m.group(1).lower()
        if w in ENHEDER:
            enhed = ENHEDER[w]
            t = t[m.end():].strip()
        elif w in ANDRE_ENHEDER:
            enhed_tekst = w
            t = t[m.end():].strip()
    if enhed == "cl":
        enhed, maengde = "ml", maengde * 10
    if maengde is not None and enhed is None and enhed_tekst is None:
        enhed = "stk"
    if maengde is None:
        enhed = "efter smag"
    navn, _, note = t.partition(",")
    ud = {"maengde": round(maengde, 3) if maengde is not None else None, "enhed": enhed,
          "navn": navn.strip(" .:"), "note": note.strip() or None}
    if enhed_tekst:
        ud["enhed_tekst"] = enhed_tekst
    if interval:
        ud["interval"] = interval
    if valgfri:
        ud["valgfri"] = True
    return ud


def normer(s):
    s = s.lower().replace("®", "").replace("™", "")
    # 'tørret' og 'stødt' bliver stående, så stødt koriander ikke bliver til frisk koriander
    s = re.sub(r"\b(økologisk[e]?|øko|frisk[e]?|friskkværnet|grofthakket|finthakket|evt)\b", " ", s)
    return re.sub(r"\s+", " ", re.sub(r"[^a-zæøå0-9 %-]", " ", s)).strip()


def katalog_indeks():
    varer = {k: v for k, v in json.load(open(BANK / "ingredienser.json", encoding="utf-8")).items()
             if not k.startswith("_")}
    navne = {}
    for vid, v in varer.items():
        for n in [v["navn"], *v.get("synonymer", [])]:
            navne.setdefault(normer(n), vid)
    return varer, navne


def match(navn, navne):
    """Ingrediens-id og hvordan det blev fundet. Claude tjekker alle forslag."""
    n = normer(navn)
    if not n:
        return None, None
    if n in navne:
        return navne[n], "navn"
    for ende in ("erne", "ene", "er", "e", "r"):
        if n.endswith(ende) and n[: -len(ende)] in navne:
            return navne[n[: -len(ende)]], "flertal"
    # Det længste katalognavn, der står som hele ord i linjen
    bedst = None
    for k, vid in navne.items():
        if len(k) >= 3 and re.search(rf"(?<![a-zæøå]){re.escape(k)}(?:e|er|r|ene|erne)?(?![a-zæøå])", n):
            if not bedst or len(k) > len(bedst[0]):
                bedst = (k, vid)
    return (bedst[1], "delvis") if bedst else (None, None)


# ---------- Oversigter ----------

def kendte_urls():
    urls = set()
    for f in (BANK / "opskrifter").glob("*.json"):
        u = json.load(open(f, encoding="utf-8"))["kilde"].get("url")
        if u:
            urls.add(u.rstrip("/"))
    return urls


def hentede():
    ud = {}
    for f in UD.glob("*/*.json"):
        ud[json.load(open(f, encoding="utf-8"))["url"].rstrip("/")] = f
    return ud


def valdemarsro_links(url):
    """Opskrifterne på en kategoriside, side for side."""
    base = re.sub(r"/page/\d+/?$", "/", url.rstrip("/") + "/")
    nr = 1
    while True:
        try:
            s = hent(base if nr == 1 else f"{base}page/{nr}/")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return
            raise
        links = re.findall(r'<a href="(https://www\.valdemarsro\.dk/[^"]+/)"[^>]*>\s*<img class="favorite"', s)
        if not links:
            return
        yield from dict.fromkeys(links)
        nr += 1


def meny_links(_url):
    """MENY's liste er alfabetisk (fx 12 andretter i træk), så den tages i tilfældig rækkefølge."""
    links = re.findall(r"<loc>(https://meny\.dk/opskrift/[^<]+)</loc>", hent("https://meny.dk/sitemap.recipes.xml"))
    random.shuffle(links)
    yield from links


OVERSIGTER = [
    # (mønster, links, filter på den hentede opskrift)
    (r"^https://(www\.)?valdemarsro\.dk/[a-z0-9_-]+/(page/\d+/?)?$", valdemarsro_links, None),
    (r"^https://(www\.)?meny\.dk/opskrifter/?$", meny_links,
     # kun hovedretter, og ikke artikler med flere opskrifter i én ("5 ingredienser – 3 opskrifter")
     lambda o: any(k.lower() == "hovedret" for k in o["kategori"]) and not re.search(r"(?i)opskrifter|\d+ slags", o["titel"])),
]


def slug(s):
    s = s.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def gem(o, navne):
    for x in o["ingredienser"]:
        x["ingrediens"], x["match"] = match(x["navn"], navne)
    sti = UD / o["side"] / f"{slug(urllib.parse.urlparse(o['url']).path.strip('/').split('/')[-1])}.json"
    sti.parent.mkdir(parents=True, exist_ok=True)
    with open(sti, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)
    mangler = sum(1 for x in o["ingredienser"] if not x["ingrediens"])
    print(f"  {o['titel']} ({o['portioner']} pers., {len(o['ingredienser'])} ingredienser"
          f"{f', {mangler} ukendte' if mangler else ''}) -> {sti.relative_to(BANK).as_posix()}")


def hent_url(url, antal, igen, navne, kendte, allerede):
    # Er siden selv en opskrift? (Valdemarsros opskrifter og kategorier har samme slags adresse)
    o = laes_opskrift(hent(url), url)
    if o:
        gem(o, navne)
        return
    for moenster, links, filter_ in OVERSIGTER:
        if re.match(moenster, url):
            print(f"Oversigt: {url}")
            n = 0
            for link in links(url):
                if n >= antal:
                    break
                if link.rstrip("/") in kendte or (link.rstrip("/") in allerede and not igen):
                    continue
                try:
                    o = laes_opskrift(hent(link), link)
                except (urllib.error.URLError, PermissionError, TimeoutError) as e:
                    print(f"  SPRUNGET OVER {link}: {e}")
                    continue
                if not o or (filter_ and not filter_(o)):
                    continue
                gem(o, navne)
                allerede[link.rstrip("/")] = True
                n += 1
            print(f"{n} nye opskrifter fra {url}")
            return
    sys.exit(f"Fandt ingen opskrift på {url}, og siden er ikke en oversigt, værktøjet kender")


def status(navne):
    kendte = kendte_urls()
    ukendte = {}
    rest = []
    for url, f in sorted(hentede().items()):
        if url in kendte:
            continue
        o = json.load(open(f, encoding="utf-8"))
        if o.get("sprunget_over"):
            continue
        rest.append(f)
        # Kataloget kan have fået nye ingredienser siden, så forslagene opdateres
        for x in o["ingredienser"]:
            x["ingrediens"], x["match"] = match(x["navn"], navne)
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(o, fh, ensure_ascii=False, indent=1)
        for x in o["ingredienser"]:
            vid = x["ingrediens"]
            if not vid:
                retter = ukendte.setdefault(normer(x["navn"]), [])
                if o["titel"] not in retter:
                    retter.append(o["titel"])
    print(f"{len(rest)} hentede opskrifter mangler at blive lavet til en opskrift:")
    for f in rest:
        print("  " + f.relative_to(BANK).as_posix())
    if ukendte:
        print(f"\n{len(ukendte)} ingredienser findes ikke i ingredienser.json:")
        for n, retter in sorted(ukendte.items(), key=lambda x: (-len(x[1]), x[0])):
            print(f"  {n}  ({len(retter)}: {', '.join(retter[:3])}{' …' if len(retter) > 3 else ''})")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    _, navne = katalog_indeks()
    if args == ["--status"]:
        status(navne)
        return
    antal, igen, urls = 20, False, []
    i = 0
    while i < len(args):
        if args[i] == "--antal":
            antal = int(args[i + 1])
            i += 1
        elif args[i] == "--igen":
            igen = True
        else:
            urls.append(args[i])
        i += 1
    kendte, allerede = kendte_urls(), dict.fromkeys(hentede(), True)
    for url in urls:
        hent_url(url, antal, igen, navne, kendte, allerede)


if __name__ == "__main__":
    main()
