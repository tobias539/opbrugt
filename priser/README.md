# Hyldepriser

Almindelige priser (ikke tilbud) fra kæderne, så Opbrugt kan regne ud, hvad et tilbud faktisk sparer. Indtil videre kun REMA 1000.

| Fil | Indhold |
|---|---|
| `hent_priser.py` | Henter REMA 1000's sortiment fra webshoppens API (højst én gang om ugen) og bygger prisfilen. Køres af den daglige opgave. |
| `match-rema-1000.json` | Hvilken REMA-vare hver ingrediens i opskriftbanken svarer til. Rettes i hånden. `null` = REMA's webshop har ikke varen. |
| `foreslaa_match.py` | Foreslår matches til nye ingredienser. Gennemgå altid forslagene; de automatiske valg er ofte forkerte (fx "agurk" → agurkerelish). |
| `til_opbrugt/rema-1000.json` | Hyldepris pr. ingrediens, som appen henter. |
| `raa/` | Hele det rå katalog (ikke i git). |

## Sådan bruger appen priserne

- **Normalpris** for en ingrediens er REMA 1000's hyldepris pr. kg, liter eller stk. Findes den ikke, bruges appens gamle cirkapriser, og ellers skønnes det, at tilbuddet er 20 % under normalprisen.
- Et tilbud tæller kun, hvis det er mindst 2 % billigere pr. kg/l/stk end normalprisen. I uge 41 2026 var 84 af 129 sammenlignelige tilbud ikke billigere end REMA's billigste almindelige vare (typisk mærkevarer på tilbud).

## Når opskriftbanken får nye ingredienser

1. `python priser/foreslaa_match.py` viser forslag.
2. Ret og tilføj linjerne i `match-rema-1000.json` (eller kør med `--skriv` og ret bagefter).
3. `python priser/hent_priser.py --kun-byg`, commit og push.

REMA's API er ikke officielt åbent. Brug det privat og sparsomt; kun de matchede priser lægges i git.
