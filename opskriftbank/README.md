# Opskriftbank

Alle opskrifter samlet ét sted som data, uanset kilde: HelloFresh, kogebøger, nettet eller egne. Formålet er at give madappen (Opbrugt) noget, den kan filtrere, skalere og koble til køleskab og tilbud.

## Hvad ligger hvor

| Sti | Indhold |
|---|---|
| `opskriftbank.json` | **Den samlede fil, appen og AI læser.** Bygges automatisk og skal ikke rettes i hånden. |
| `opskrifter/<id>.json` | Én fil pr. opskrift. Det er her, man retter. |
| `ingredienser.json` | Kataloget over ingredienser. Alle opskrifter peger hertil. Køleskab og tilbud skal pege på de samme id'er. |
| `variabler.json` | Grupper af ingredienser, der kan bytte plads (se "Variabler" nedenfor). |
| `vaerktoej/tildel_variabler.py` | Foreslår variabler til ingredienslinjerne ud fra grupperne og fremgangsmåden. |
| `kategorier.json` | De faste ord til filtre: køkken (med region), måltid, rettype, hovedprotein, tags, allergener og butiksafdelinger. |
| `billeder/<id>.jpg` | Madbilledet til hver opskrift. |
| `kilder/scanninger/` | De originale scanninger (PDF). |
| `kilder/hellofresh-allergenkoder.json` | Nøglen til numrene efter ingredienserne på HelloFresh-kort. |
| `skema/opskrift.schema.json` | Den præcise definition af en opskrift. |
| `vaerktoej/byg.py` | Tjekker alle opskrifter og bygger `opskriftbank.json`. |
| `vaerktoej/klip_billede.py` | Klipper madbilledet ud af en scannet HelloFresh-forside. Tjek altid resultatet: den leder kun i venstre 84 % af siden. |
| `vaerktoej/udsnit.py` | Laver læsbare udsnit af et kort (ingredienser, næring/allergener, trin), og vender bagsider, der ligger på hovedet. |
| `_forslag/` (midlertidig) | Når flere arbejder samtidig, lægges nye ingredienser/kategorier/allergen-numre her i stedet for direkte i katalogerne. `byg.py --forslag` tjekker med forslagene uden at skrive noget; derefter flettes de ind, og mappen slettes. |

## Sådan er en opskrift bygget op

- **Portioner:** `maengde` gælder for `portioner.basis`. Hvis kilden selv angiver andre portionsstørrelser, som HelloFresh gør for 2, 3 og 4 personer, ligger de i `tabel`. Til n portioner bruges kildens `tabel[n]`, når den findes, og ellers `maengde × n / basis`. Kildens egne tal tæller altså før en lineær skalering. Det er vigtigt, fordi HelloFresh fx bruger 140 g tomatpuré til både 3 og 4 personer.
- **Ingredienser:** Hver linje har `ingrediens`, som er id'et i kataloget, og `navn`, som er teksten fra kilden. `basisvare: true` betyder noget, man normalt har i skabet, fx olie, salt og vand. `fra_fremgangsmaade: true` betyder, at ingrediensen bruges i trinene, selvom den ikke står på ingredienslisten.
- **Beregnet:** `byg.py` regner hver mængde om til ingrediensens basisenhed (gram, ml eller stk) for hvert portionsantal. Tsk, spsk og dl bliver til ml, og 1 tomat bliver til ca. 100 g. Køleskab og tilbud kan derfor sammenlignes direkte. Hver ingrediens i kataloget får også en liste `bruges_i` med de opskrifter, den indgår i.
- **Kategorier:** `koekken` er en liste, hvor den første er det primære køkken. Hvert køkken hører til en region, så man kan filtrere på både "Mexicansk" og "Latinamerika".

## Variabler: løse opskrifter

Den originale opskrift bevares altid, men mange ingredienser kan byttes. Det er typisk grøntsagerne, man har for mange af, der skal bestemme retten.

- **`variabler.json`** har grupper af ingredienser, der kan bytte plads. En gruppe er defineret ud fra **rollen i retten** og ikke ud fra selve grøntsagen. Det skyldes, at det, der kan erstatte agurk i en salat, ikke kan erstatte den i tzatziki. Eksempler:
  - "Råt, saftigt grønt": agurk, tomat, peberfrugt, radiser …
  - "Grønt på bagepladen": gulerod, pastinak, blomkål, zucchini …
  - "Grønt på panden, i wok eller gryde"
  - "Kål til slaw", "Salatblade", "Løg", "Friske krydderurter"
  - "Ris og korn", "Cremet dip", "Hakket kød", "Kylling" m.fl.
- **Kvalitet:** Hvert medlem er "god" eller "ok". Et bytte er kun "god", hvis både originalen og erstatningen er "god".
- **Byttes efter vægt.** Grøntsager, der tælles i stk, har en skønnet `gram_pr_stk` i ingredienser.json (1 agurk ≈ 350 g, 1 peberfrugt ≈ 150 g). Grupper med `"bytte": "efter smag"` (syre, chili) regnes ikke om.
- **I opskriften** har en ingredienslinje feltet `"variabel": "<gruppe>"`. `"variabel": null` betyder, at linjen bevidst er låst fast, fx rå broccoli i en broccolisalat.
- **`vaerktoej/tildel_variabler.py`** foreslår variabler til nye opskrifter. Når en ingrediens findes i flere grupper, læser værktøjet fremgangsmåden: "bageplade" peger på ovngruppen, og "salat/salsa" peger på rå. Uafklarede linjer skal afgøres i hånden. Kør først uden `--skriv` og se forslagene igennem.
- **`byg.py`** beregner tre ting i opskriftbank.json:
  - **For hver variabel linje:** alternativerne med mængde (`beregnet.alternativer`).
  - **For hver ret:** den løse skabelon (`beregnet.skabelon`), med faste ingredienser og pladser, der kan fyldes fra en gruppe.
  - **For hver ingrediens:** listen `kan_bruges_i`, med alle retter den kan bruges i, også som erstatning. Den svarer på "jeg har 2 peberfrugter – hvad kan jeg lave?".

## Kobling til køleskab og tilbud

Kataloget i `ingredienser.json` er nøglen:
- `synonymer` bruges til at matche en tilbudslinje eller en kvitteringslinje, fx "Hakket oksekød 8-12 %", til en ingrediens.
- `afdeling` er den samme inddeling, som indkøbslisten i Opbrugt bruger.
- `opbrugt` er nøglen i Opbrugt-appens varekatalog, fx `okse`, `pure` og `loeg`, så de to systemer kan flettes.

## Opbrugt-appen

Opbrugt henter opskrifterne fra en eksport af banken. Når banken er ændret, gør du sådan:

1. `python vaerktoej/byg.py`
2. `python vaerktoej/eksporter_opbrugt.py ../opbrugt`. Det skriver `opskrifter.js` og billeder i 560 px bredde.
3. Commit og `git push`. Appen ligger på GitHub Pages og opdateres af sig selv et minut efter.

Appen kalder Claude direkte fra browseren med en API-nøgle, som hver bruger skriver ind under Præferencer. Skab, plan og indkøbsliste gemmes kun i browseren på den enkelte telefon. Tilbuddene henter appen fra `../tilbud/til_opbrugt/`, som en daglig routine opdaterer med `tilbud/hent_tilbud.py`.

`eksporter_opbrugt.py` indeholder en tabel (`P_TIL_BANK`), der oversætter appens egne varenøgler (fx `peber` og `okse`) til bankens ingredienser. Fritekst-varer i skabet, fx "2 røde peberfrugter", matches på navne og synonymer. Forarbejdede varer som "syltede agurker" og "chilisovs" matcher kun ved præcist navn.

## Tilføj nye scanninger

1. Scan kortene med forsiden først, i farve og 200 dpi. Det er fint at samle mange kort i én PDF.
2. Læg PDF'en i `kilder/scanninger/` med et navn som `ÅÅÅÅ-MM-DD hellofresh NN.pdf`.
3. Bed Claude om at tilføje opskrifterne. Claude gør så følgende for hvert kort:
   - læser bagsiden i fuld opløsning (ingredienser, trin, næringsindhold og allergener) og forsiden (titel, undertitel, tid, ugekode og menunummer),
   - oversætter allergen-numrene med `kilder/hellofresh-allergenkoder.json` og tilføjer nye numre dér,
   - tilføjer manglende ingredienser til `ingredienser.json` og manglende kategorier til `kategorier.json`. Et ukendt navn på et HelloFresh-kort er som regel deres egen krydderiblanding (fx "Panamad"). Den registreres med `"krydderiblanding": "hellofresh"`, `"basisvare": true` og `"erstatning": null`, så appen ikke sætter den på indkøbslisten. Indholdet kan ofte findes ved at søge efter `"<navn>, en blanding af"` på hellofresh.dk, fordi HelloFresh nogle gange beskriver blandingen i indledningen til en opskrift. Bedst er et billede af indholdslisten på posen, fordi ingredienserne efter EU-reglerne står i rækkefølge efter vægt, med det største først,
   - skriver `opskrifter/<id>.json` og kører `python vaerktoej/klip_billede.py <pdf> <forside> <id>`.
4. Kør `python vaerktoej/byg.py`. Banken bliver kun opdateret, hvis der er 0 fejl. Til sidst viser den, hvilke scanninger der endnu ikke er behandlet.

Opskrifter fra andre kilder følger samme format. Sæt `kilde.type` til `kogebog`, `web`, `egen` eller `familie`, og angiv bogens titel og side eller en URL.
