# Ikke-kommercielt

Her er alt i projektet, der ikke må bruges kommercielt, eller hvor der ikke er en tilladelse. Bliver appen
kommerciel, er det de ting, der skal ændres. Tabellen siger hvordan.

Data, der kun må bruges ikke-kommercielt, ligger i denne mappe, når det kan lade sig gøre. Prisdataene fra
Salling Group ligger stadig i `priser/` og `tilbud/`. Hvis de flyttes, holder den daglige opgave op med at virke,
og appens adresser ændrer sig. De står derfor i tabellen nedenfor i stedet.

## I denne mappe

| Mappe | Hvad | Licens | Bruges til |
|---|---|---|---|
| `recipe1msubs/` | Recipe1MSubs: 70.000 gange, hvor folk i kommentarer til opskrifter har skrevet, at de brugte én ingrediens i stedet for en anden. `byt.json` er udtrækket for opskriftbankens egne ingredienser. | CC BY-NC 4.0, kun ikke-kommerciel brug. Fatemi, Kassam, Darabi, Pierre, Wendt & Romero-Soriano (2023): *Learning to Substitute Ingredients in Recipes*, Meta AI. | Lighedstabellen: "ofte brugt i stedet" |
| `flavorgraph/` | FlavorGraph: hvilke ingredienser der bruges sammen i opskrifter. `kontekst.json` siger, hvor ens to ingredienser bruges. | Koden er Apache 2.0, men grafen er bygget på Recipe1M, som kun må bruges til ikke-kommerciel forskning. Park m.fl. (2021): *FlavorGraph*, Sony AI. | Lighedstabellen: "bruges i samme slags retter" |

Rådataene ligger i `*/raa/` og er udeladt fra git. Her hentes de:

- Recipe1MSubs: `https://dl.fbaipublicfiles.com/gismo/{train,val,test}_comments_subs.pkl`. Repoet er https://github.com/facebookresearch/gismo.
- FlavorGraph: `https://raw.githubusercontent.com/lamypark/FlavorGraph/master/input/{nodes,edges}_191120.csv`

Bagefter køres `python ikke-kommercielt/udtraek.py` og så `python opskriftbank/vaerktoej/lighed.py`.
Recipe1MSubs ligger som Python-pickles. `udtraek.py` læser dem med en låst indlæser, der ikke kan køre kode.

## Hvis appen bliver kommerciel

| Hvad | Hvor | Vilkår | Det skal gøres |
|---|---|---|---|
| **Lighedstabellen** ("Findes den ikke? Tag … i stedet") | `opskriftbank/lighed.json` → `opbrugt/opskrifter.js` | Er afledt af Recipe1MSubs og FlavorGraph og må derfor kun bruges ikke-kommercielt. | Kør `python opskriftbank/vaerktoej/lighed.py --kommerciel` og eksportér igen. Så bruges kun Frida og opskriftbankens egne byttegrupper. Slet denne mappe. |
| **Salling Groups API** (hyldepriser fra Netto og føtex) | `priser/hent_priser.py` (`netto` og `foetex` i `KAEDER`), `priser/til_opbrugt/netto.json` og `foetex.json`, `priser/match-netto.json` og `match-foetex.json` | Salling Groups udviklervilkår: kun uddannelse og ikke-kommerciel brug. | Få en kommerciel aftale med Salling Group, eller fjern `netto` og `foetex` fra `KAEDER` og slet de to prisfiler. Appen bruger så REMA 1000's priser med et prisniveau for Netto og føtex, ligesom for Lidl. |
| **REMA 1000's webshop-API** (hyldepriser) | `priser/hent_priser.py`, `priser/til_opbrugt/rema-1000.json` | Ikke officielt åbent, og der er ingen tilladelse. | Få en aftale med REMA 1000, eller find en anden priskilde. |
| **Tjek / eTilbudsavis** (tilbudsaviser) | `tilbud/hent_tilbud.py`, `tilbud/til_opbrugt/` | Ikke officielt åbent (https://tjek.com/apis-and-sdks). | Tjek sælger API-adgang. Få en aftale. |
| **HelloFresh-opskrifter** (50 stk.) og deres billeder | `opskriftbank/opskrifter/` (`kilde.type` = `hellofresh`), `opskriftbank/billeder/`, `opbrugt/billeder/` | Billeder og tekster er HelloFresh' ophavsret. | Fjern dem, eller skriv opskrifterne om med egne ord og egne billeder. |
| **Opskrifter fra Valdemarsro (20) og MENY (19)** | `opskriftbank/opskrifter/` (`kilde.type` = `web`) | Siderne har ophavsret til deres tekster. | Få tilladelse, eller fjern dem. |
| **Butikkernes logoer** | `opbrugt/logoer/` | Varemærker. | Få tilladelse, eller vis butikkens navn i stedet. |

## Må bruges kommercielt

- **Frida 5.5** (DTU Fødevareinstituttet): CC BY 4.0. Kilden skal angives: "© Fødevaredata (frida.fooddata.dk), version 5.5, november 2025". Frida ligger i `opskriftbank/kilder/frida/` og er udeladt fra git. Hent den fra https://doi.org/10.11583/DTU.29500682.
- **Whisper** (talegenkendelse i videoer) via transformers.js: MIT og Apache 2.0.
- **Claude API**: Anthropics kommercielle vilkår. Hver telefon bruger sin egen nøgle.
