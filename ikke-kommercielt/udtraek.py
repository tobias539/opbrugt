"""Træk det ud af Recipe1MSubs og FlavorGraph, som lighedstabellen bruger – kun for opskriftbankens egne ingredienser.

Brug:  python ikke-kommercielt/udtraek.py

Læser rådata i recipe1msubs/raa/ og flavorgraph/raa/ (ikke i git, se README om hvor de hentes) og
opskriftbank/lighed/koblinger.json (hvilke engelske navne hver ingrediens har). Skriver:
  recipe1msubs/byt.json      {a: {b: n}}  n = antal gange, folk har skrevet, at de brugte b i stedet for a
  flavorgraph/kontekst.json  {a: {b: s}}  s = hvor ens a og b bruges (cosinus mellem deres naboer i FlavorGraph),
                                          de 25 mest ens pr. ingrediens

Begge må kun bruges ikke-kommercielt (se README.md i denne mappe).
Recipe1MSubs ligger som Python-pickles. De læses med en låst indlæser, der ikke tillader nogen klasser,
så filerne ikke kan køre kode.
"""
import csv
import io
import json
import math
import pickle
from collections import Counter, defaultdict
from pathlib import Path

MAPPE = Path(__file__).resolve().parent
KOBLINGER = MAPPE.parent / "opskriftbank" / "lighed" / "koblinger.json"


class Laast(pickle.Unpickler):
    def find_class(self, module, name):
        raise pickle.UnpicklingError(f"klasse afvist: {module}.{name}")


def skriv(sti, data):
    sti.write_text("{\n" + ",\n".join(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False, sort_keys=True)}"
                                       for k, v in sorted(data.items())) + "\n}\n", encoding="utf-8")


def main():
    kob = {k: v for k, v in json.loads(KOBLINGER.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    navn_til = defaultdict(set)
    for k, v in kob.items():
        for n in v["en"]:
            navn_til[n].add(k)

    # Recipe1MSubs: tæl par mellem vores ingredienser
    par = Counter()
    for fil in sorted((MAPPE / "recipe1msubs" / "raa").glob("*_comments_subs.pkl")):
        for x in Laast(io.BytesIO(fil.read_bytes())).load():
            s = x.get("subs") if isinstance(x, dict) else None
            if not s or len(s) != 2:
                continue
            a, b = (y[0] if isinstance(y, (list, tuple)) else y for y in s)
            for ka in navn_til.get(str(a), ()):
                for kb in navn_til.get(str(b), ()):
                    if ka != kb:
                        par[(ka, kb)] += 1
    byt = defaultdict(dict)
    for (a, b), n in par.items():
        byt[a][b] = n
    skriv(MAPPE / "recipe1msubs" / "byt.json", byt)
    print(f"Recipe1MSubs: {len(par)} par mellem {len(byt)} ingredienser")

    # FlavorGraph: hver ingrediens' naboer (ingrediens-ingrediens-kanter med vægt); cosinus mellem naboskaberne
    raa = MAPPE / "flavorgraph" / "raa"
    navn = {r["node_id"]: r["name"] for r in csv.DictReader(open(raa / "nodes_191120.csv", encoding="utf-8")) if r["node_type"] == "ingredient"}
    nabo = defaultdict(Counter)
    for r in csv.DictReader(open(raa / "edges_191120.csv", encoding="utf-8")):
        if r["edge_type"] != "ingr-ingr" or r["id_1"] not in navn or r["id_2"] not in navn:
            continue
        a, b, s = navn[r["id_1"]], navn[r["id_2"]], float(r["score"])
        nabo[a][b] += s
        nabo[b][a] += s
    vek = {}
    for k, v in kob.items():
        c = Counter()
        for n in v["en"]:
            c.update(nabo.get(n, {}))
        for n in v["en"]:  # ens egne navne tæller ikke som nabo
            c.pop(n, None)
        if c:
            vek[k] = (c, math.sqrt(sum(x * x for x in c.values())))
    kontekst = {}
    for a, (va, la) in vek.items():
        s = []
        for b, (vb, lb) in vek.items():
            if a == b:
                continue
            d = sum(x * vb.get(n, 0) for n, x in va.items())
            if d > 0:
                s.append((round(d / (la * lb), 3), b))
        s.sort(reverse=True)
        kontekst[a] = {b: x for x, b in s[:25]}
    skriv(MAPPE / "flavorgraph" / "kontekst.json", kontekst)
    print(f"FlavorGraph: {len(vek)} af {len(kob)} ingredienser fundet")


if __name__ == "__main__":
    main()
