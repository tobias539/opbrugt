# UX-regler for Mad app

Status: udkast til de generelle regler, der skal gøre siderne og fanerne ens. Reglerne er en kendt guide lagt
ned over appen, som den ser ud i version 77. Introen i `intro-forslag.md` er det første, der er tegnet efter dem.

## Kilden

**Jakob Nielsens 10 heuristikker for brugergrænseflader** (Nielsen Norman Group, 1994, gennemset 30. januar 2024):
https://www.nngroup.com/articles/ten-usability-heuristics/

Valgt, fordi den er kort (ti regler), bruges af alle, der arbejder med apps, er gratis, og handler om
brugerens oplevelse, ikke om et bestemt udseende. Den passer derfor til en app, der allerede har sit eget
udtryk. To supplementer, kun til guider og introer:

- **Apple, Human Interface Guidelines › Onboarding** (opdateret 10. juni 2024):
  https://developer.apple.com/design/human-interface-guidelines/onboarding
- **GOV.UK Design System › Question pages** ("one thing per page"):
  https://design-system.service.gov.uk/patterns/question-pages/

Afsnit A beskriver appens faste byggesten, som reglerne henviser til. Afsnit B er de ti regler lagt ned over
appen. Afsnit C er reglerne for guider og introer. Afsnit D er tjeklisten. Afsnit E er ordlisten.

## A. Appens faste byggesten

Det her findes allerede i koden. Nye sider bygges af det samme.

**En fane**

1. `header.top`: h1 øverst til venstre med fanens navn, evt. status eller antal til højre (grå).
   Navnet er det samme som i bundbjælken. Ting i bestemt form (Skabet), handlinger uden (Plan, Snak,
   Opskrifter, Indkøb, Præferencer).
2. Én grå linje (`.sub`), hvis siden skal forklares. Ellers ingen.
3. Indholdet.
4. Den primære handling som fyldt grøn knap: `.storknap`/`.planknap`, når den starter noget, ellers `.btn`.
5. Under-sider inde i en fane har `‹ Navnet på siden`, man kommer tilbage til (`.back`), øverst til venstre.

**En guide-skærm** (`.wiz.skaerm.guide`)

1. Prik-striben (`.prik`): hvor langt man er.
2. × øverst til højre: lukker uden at gemme.
3. h2: spørgsmålet.
4. Én grå linje: hvorfor der spørges, eller hvad svaret bruges til.
5. Valgene.
6. `.nav` nederst, fast over bundbjælken: Tilbage (ghost) til venstre, Næste eller Gem (fyldt) til højre.
7. Skærmen fylder telefonen uden at rulle. Tandhjul og kurv er skjult. Swipe = Tilbage/Næste.

**Valg**

| Byggesten | Bruges til | Opførsel |
|---|---|---|
| `.tile` | Få valg med emoji og et ord | Ét valg: går selv videre. Flere valg: ✓ på de valgte, Næste går videre |
| `.tiles.tal` | Tal | Går selv videre |
| `.tiles.logo` | Butikker | Flere valg |
| `.chip` | Mange små til/fra | Bliver på skærmen |
| `.seg` | Skift mellem visninger inden for en fane (Snak/Feedback/Forbrug) | Swipe skifter også |
| `.toggle`, `.step` | Til/fra og +/− i en liste med indstillinger | Gemmer med det samme |
| `.storknap` | De 1–2 store valg, der starter noget (Planlæg, Tilføj retter) | Den fyldte er den, man oftest trykker på |

**Lister og beskeder**

| Byggesten | Bruges til |
|---|---|
| `.list` > `.item` | Alle lister. `.oversigt` giver to kolonner (navn, værdi) |
| `.toast` | Kvittering for noget, der er gjort. Én linje, 2 sekunder, nederst |
| `.sugg` (orange) | Noget mangler, eller noget gik galt, med en vej videre |
| `.tilbudsbesked` (gul) | Et tilbud |
| `.hjaelp` "?" + `.hjaelpboks` | Hvad kan man her. Én pr. fane eller visning |
| `.skabhint` / grå linje | Én hint om en bevægelse, dér hvor den bruges |
| Browserens `confirm` | Kun før noget slettes |

**Farver, skrift, tone, bevægelser**

- Grøn (`--leaf`) = handling og valgt. Orange (`--carrot`) = opmærksomhed og fokusring. Gul (`--tilbud`) =
  tilbud. Grå (`--muted`) = forklaring. Mørk tilstand følger telefonen.
- Bricolage Grotesque til overskrifter, Atkinson Hyperlegible til brødtekst. 17 px som grundstørrelse.
- Appen siger "vi" og nævner aldrig Claude, AI eller en model. "I/jer" er husstanden ("Hvor mange er I?").
  "Du" er den, der holder telefonen ("Du har ikke valgt det endnu").
- Swipe til siden = frem/tilbage. Langt tryk = indstillinger for en vare. Træk = flyt til kurv, spist eller
  smidt ud. Swipe op lukker kogebogen. Hver bevægelse har også en knap.

## B. De ti regler lagt ned over appen

Hver regel: hvad den siger, hvordan appen allerede gør det, reglen for nye sider og faner, og de huller, der
er i dag.

### 1. Man kan altid se, hvad der sker

*Nielsen: Hold brugeren orienteret med rettidig tilbagemelding.*

- **Appen i dag:** toast ("3 varer lagt i skabet", "Gemt på telefonen"), fremdrift i procent med hvad der
  behandles, tænkeprikker, prik-striben i guider, tallet på kurven, "Forbindelse: tjekker …".
- **Regel:** Alt, der ændrer noget, kvitteres inden for et sekund med én linje. Alt, der tager over et sekund,
  viser fremdrift og hvad der sker. Alt med trin viser, hvor langt man er.
- **Huller:** Ingen kendte. Versionslinjen under Præferencer stod fast på "Version 52"; den følger nu `APP_VERSION`.

### 2. Appen taler husstandens sprog

*Nielsen: Brug ord og begreber, brugeren kender, i den rækkefølge, de kender fra virkeligheden.*

- **Appen i dag:** Skabet, hylden, kokkehuerne, "Tøm skabet", "Køb ind i Netto", "Holder 3 dage mere",
  "Fordi …". Rækkefølgen er køkkenets: planlæg → køb ind → lav retten → spist eller smidt ud.
- **Regel:** Ord fra køkkenet og butikken, aldrig fra koden: ikke "data", "synkroniser", "session", "fejl 429".
  Tal med enhed og i hele kroner. Spørgsmål om husstanden i "I", handlinger på telefonen i "du".
- **Huller:** "API-nøgle" og "sk-ant-…" er kodens ord. Overvej "nøglen" og én linje om, hvor man får den.

### 3. Man kan altid fortryde og komme ud

*Nielsen: En tydelig nødudgang fra enhver tilstand, og fortryd.*

- **Appen i dag:** × på alle guider, Tilbage, "‹ Skabet", swipe tilbage, kladde i guider (intet gemmes før
  Gem), Byt og fjern en ret, "Nulstil" bag et ekstra tryk og en bekræftelse.
- **Regel:** Hver skærm har én vej ud på samme sted hver gang: × øverst til højre i guider, `‹ Navn` øverst til
  venstre på under-sider. Intet gemmes, før man trykker Gem eller Færdig. Det, der gemmes med ét tryk eller
  ét træk, skal kunne fortrydes med ét tryk.
- **Huller:** Tjek, om træk til Spist og Smidt ud kan fortrydes. Hvis ikke: en "Fortryd" i toasten.

### 4. Ens ord, ens steder, ens knapper

*Nielsen: Brugeren skal ikke gætte, om forskellige ord og steder betyder det samme.*

- **Appen i dag:** Samme guide-ramme til præferencer, hylde, planlægning og opskriftfiltre. Fyldt grøn = det
  man oftest trykker, ghost = alternativet. × til højre, Tilbage til venstre, Næste/Gem til højre, ✓ på valgte.
- **Regel:** Byg af afsnit A. Opfind ikke en ny knaptype til en ny side. Ét ord pr. betydning (afsnit E).
  Samme ting samme sted på alle faner.
- **Huller:** Pile på navigationsknapper nogle steder: "‹ Tilbage" på planlægningens forslagsskærm og i
  opskriftvisningen, "‹ Forrige", "Næste ›" og "Start: trin 1 ›" i Lav retten, "‹ Tilbage til planen" i
  kogebogen. Opskriftfiltrene er rettet til "Tilbage" og "Næste". "Gem", "Gem præferencer" og "Færdig" om det samme. Browserens `confirm` otte steder mod appens egne bokse.
  Plan-fanens h1 er "Mad app", bundbjælken siger "Plan". Indkøb er både en side og en kurv-knap; tandhjulet
  er en femte "fane". De to sidste er valgt med vilje, og så skal det stå her som undtagelse.

### 5. Forebyg fejl

*Nielsen: Fjern det, der kan gå galt, eller bed om bekræftelse, før det sker.*

- **Appen i dag:** Allergier filtrerer, før der foreslås noget. Knapper er grå med en grund ("Resten af ugen
  er planlagt", "Tilbudsaviserne er ikke kommet endnu"). Filtervalg viser "3 retter", så man ikke vælger en
  tom kombination. Bekræftelse før nulstil. Kladde i guider.
- **Regel:** Vis kun valg, der kan lade sig gøre. Grå dem ud med grunden i stedet for at fejle bagefter.
  Bekræftelse kun ved det, der sletter eller sender. Standardværdi på alt, så Næste altid er gyldigt.

### 6. Vis det, i stedet for at kræve, at man husker det

*Nielsen: Genkendelse frem for hukommelse.*

- **Appen i dag:** Felter med emoji og ord, logoer for butikker, "Sådan ser det ud" før Gem, resuméet af
  præferencerne, skabet som hylde, autoliste når man skriver, "Fordi …" ved forslag.
- **Regel:** Under ca. 12 muligheder vises som valg, ikke som et tomt felt. Den valgte værdi står, hvor den
  bruges ("Køb ind i Netto og Rema 1000"). Et tomt felt har et eksempel i placeholder ("Fx paprika").

### 7. Hurtige veje for de vante

*Nielsen: Genveje, som nye brugere ikke behøver se.*

- **Appen i dag:** Swipe overalt, langt tryk, "Vælg" flere, søgefeltet i Opskrifter, "Én ret ad gangen",
  korte kommandoer i Snak ("jeg mangler toiletpapir"), tryk på prikkerne i filtrene hopper direkte.
- **Regel:** Alt med trin kan swipes. Hver guide kan springes over, og det samme kan gøres uden guide (på
  fanen eller i Snak). Hints forsvinder, når de er brugt.

### 8. Enkelt, og kun det nødvendige

*Nielsen: Hvert ekstra element konkurrerer med det, der betyder noget.*

- **Appen i dag:** Én skærm pr. trin. "Flere indstillinger" foldet sammen. "Se mere" i stedet for en lang boks.
  h2 + én grå linje. "Genkendte 5/7 ting".
- **Regel:** Én overskrift, én linje, ét spørgsmål pr. skærm. Højst én fyldt knap pr. skærm. Alt, der ikke
  bruges hver uge, bag en fold eller under Præferencer. Ingen forklaring over tre linjer; lav et "?" i stedet.

### 9. Fejl i klart sprog med en vej videre

*Nielsen: Sig hvad der skete, og hvad man kan gøre. Ingen koder.*

- **Appen i dag:** "Næste uges tilbudsaviser er ikke klar endnu", "Det kan vi ikke hjælpe med. Prøv med andre
  ønsker.", "Mangler API-nøgle … Planen, skabet og indkøbslisten virker også uden", genforsøg op til tre gange,
  "Gemt på telefonen og bliver sendt automatisk" uden net.
- **Regel:** En fejl siger, hvad der skete, og hvad man kan gøre nu. Orange boks (`.sugg`), aldrig rød alarm.
  Det, der kan gøres uden net, gøres og sendes senere.

### 10. Hjælp dér, hvor man er

*Nielsen: Helst ingen manual. Når der skal hjælp til, så kort, i kontekst og om opgaven.*

- **Appen i dag:** "?" i Snak, hint-linjen under hylden, omslagets "Bladr for at se retterne", kortet
  "Ikke nu / Kom i gang" i Skab, den grå linje under hvert spørgsmål.
- **Regel:** Ét "?" eller én hint-linje pr. fane eller visning, om det, man kan gøre lige her. Introen forklarer
  ikke fanerne i detaljer; de forklarer sig selv, første gang man står i dem.

## C. Guider og introer

Fra Apple og GOV.UK, kogt ned til det, der passer til appens ramme.

1. **Valgfri og kort.** Kan lukkes fra første skærm. Vises aldrig igen af sig selv. Kan findes igen under
   Præferencer. (Apple)
2. **Ét spørgsmål pr. skærm.** Overskriften er spørgsmålet. Én hjælpelinje uden links. (GOV.UK)
3. **Spørg kun om det, du har brug for nu.** Vid hvorfor du spørger. Det, der ikke ændrer den første uge, har
   en standardværdi og spørges, hvor det bruges. (GOV.UK, Apple: "udskyd opsætning, der ikke er nødvendig")
4. **Lær ved at gøre.** Folk husker det, de har gjort, ikke det, de har læst. En guide, der fylder skabet med
   rigtige billeder, slår en skærm, der forklarer skabet. (Apple)
5. **Hints i kontekst frem for ét langt forløb.** Forklaringer om en del af skærmen står ved den del. (Apple)
6. **Tilbage findes altid.** Ét tryk fører videre. Flere valg afsluttes med én knap. (GOV.UK)
7. **Fremdrift enkelt.** Prik-striben, ikke en liste over alle trin. (GOV.UK)
8. **Adgang bedes om med grunden.** Enten i introen med én linje om hvorfor, eller første gang den skal
   bruges. (Apple)
9. **Ingen store hentninger og ingen vilkår i introen.** (Apple)
10. **Standardværdierne er valgt, så Næste altid er et gyldigt svar.** (GOV.UK, Nielsen 5)

GOV.UK anbefaler ordet "Fortsæt" frem for "Næste". Appen bruger "Næste" overalt, og regel 4 (ens ord) vejer
tungere end den anbefaling. Behold "Næste".

## D. Tjekliste før en ny side, fane eller guide sendes ud

- [ ] h1 øverst til venstre hedder det samme som i bundbjælken (fane), eller h2 er spørgsmålet (guide).
- [ ] Højst én grå forklaringslinje under overskriften.
- [ ] Ét spørgsmål eller én handling pr. skærm. Ét valg går selv videre; flere valg har én Næste.
- [ ] Højst én fyldt grøn knap. Alternativet er ghost.
- [ ] Tilbage/× på det faste sted. Intet gemmes før Gem/Færdig.
- [ ] Standardværdi på alt. Knapper, der ikke kan bruges, er grå med en grund.
- [ ] Alle ord står i ordlisten (afsnit E). Ingen ord fra koden.
- [ ] "Vi" om appen, "I" om husstanden, "du" til den, der holder telefonen. Aldrig Claude, AI eller model.
- [ ] Hver handling kvitteres med en toast på én linje. Alt over et sekund viser fremdrift.
- [ ] Fejl siger, hvad der skete, og hvad man kan gøre. Orange boks.
- [ ] Swipe gør det samme som Tilbage/Næste. Hver bevægelse har en knap.
- [ ] Højst én hint eller ét "?" pr. visning. Hints forsvinder, når de er brugt.
- [ ] Byggestenene fra afsnit A er brugt. Ingen ny knaptype.
- [ ] Set i mørk tilstand og på en kort skærm (iPhone SE). Knapperne nederst står fast.
- [ ] `aria-label` på knapper uden tekst, `aria-pressed` på valg, fokusring synlig.

## E. Ordliste

| Betydning | Ord | Knap | Sted |
|---|---|---|---|
| Et trin frem | Næste | fyldt grøn | nederst til højre |
| Et trin tilbage | Tilbage | ghost | nederst til venstre |
| Gem og afslut en guide | Gem (evt. "Gem præferencer") | fyldt grøn | nederst til højre |
| Afslut noget, der løbende er gemt (indkøb, rækkefølge) | Færdig | fyldt grøn | nederst, fuld bredde |
| Luk uden at gemme | × (`aria-label="Luk"`) | `.x` | øverst til højre |
| Tilbage til siden over | ‹ Navnet på siden ("‹ Skabet") | `.back` | øverst til venstre |
| Begynd en guide | Kom i gang · Opret … · Vælg | fyldt grøn | i kortet |
| Udskyd et tilbud om en guide | Ikke nu | ghost | i kortet, til venstre |
| Ret noget gemt | Ret | ghost | under oversigten |
| Nulstil | Nulstil (med bekræftelse) | ghost | under Præferencer |
| Tilføj | + Tilføj (knap) · Tilføj (ved et felt) | ghost | øverst i fanen / ved feltet |
| Åbn en ret | Lav retten · Ændr retten | fyldt / ghost | ved kokkehuen |
| Fravalgt i en liste | ✕ | – | på varen |
| Gjort | ✓ | – | på varen |

Varianter, der stadig skal tages stilling til: "‹ Tilbage" (planlægningens forslag og opskriftvisningen),
"‹ Forrige", "Næste ›" og "Start: trin 1 ›" (Lav retten) og "‹ Tilbage til planen" (kogebogen).
Opskriftfiltrene er rettet.
