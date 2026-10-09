# Hyldepriser

Almindelige priser (ikke tilbud) fra kæderne, så Opbrugt kan regne ud, hvad et tilbud faktisk sparer. Indtil videre kun REMA 1000.

| Fil | Indhold |
|---|---|
| `hent_priser.py` | Henter REMA 1000's sortiment fra webshoppens API (højst én gang om måneden) og bygger prisfilen. Køres af den daglige opgave. |
| `match-rema-1000.json` | Hvilken REMA-vare hver ingrediens i opskriftbanken svarer til. Rettes i hånden. `null` = REMA's webshop har ikke varen. |
| `foreslaa_match.py` | Foreslår matches til nye ingredienser. Gennemgå altid forslagene; de automatiske valg er ofte forkerte (fx "agurk" → agurkerelish). |
| `til_opbrugt/rema-1000.json` | Hyldepris pr. ingrediens, som appen henter. |
| `raa/` | Hele det rå katalog (ikke i git). |

## Sådan bruger appen priserne

- **Normalpris** for en ingrediens i en butik findes i denne rækkefølge:
  1. Prisen fra brugerens egne kvitteringer fra den butik (appen lærer dem, når en kvittering scannes; linjer med rabat og priser, der ligner et tilbud, springes over).
  2. REMA 1000's hyldepris. Den bruges også for Netto, Lidl og 365discount, som ikke lægger deres priser ud.
  3. Appens gamle cirkapriser, og ellers et skøn: tilbuddet regnes som 20 % under normalprisen.
- Netto, Lidl og 365discount har ingen offentlige hyldepriser. føtex' dagligvarepriser findes kun via Salling Groups API (Bilka-priser) og kræver en nøgle i `priser/salling-noegle.txt` (ikke i git).
- Et tilbud tæller kun, hvis det er mindst 2 % billigere pr. kg/l/stk end normalprisen. I uge 41 2026 var 84 af 129 sammenlignelige tilbud ikke billigere end REMA's billigste almindelige vare (typisk mærkevarer på tilbud).

## Når opskriftbanken får nye ingredienser

1. `python priser/foreslaa_match.py` viser forslag.
2. Ret og tilføj linjerne i `match-rema-1000.json` (eller kør med `--skriv` og ret bagefter).
3. `python priser/hent_priser.py --kun-byg`, commit og push.

REMA's API er ikke officielt åbent. Brug det privat og sparsomt; kun de matchede priser lægges i git.
