# Intro til opstart – forslag

Status: forslag, ikke i appen. Reglerne, forslaget bygger på, står i `ux-regler.md` i samme mappe.

## Præmis

Introen er ikke en ny ting. Det er en kæde af de guider, appen allerede har, med tre nye skærme som lim:
en velkomst, en skærm til nøglen og en afslutning. Hver skærm bruger den ramme, der findes i dag
(`.wiz.skaerm.guide`): prik-stribe øverst, × i hjørnet, en overskrift, der er spørgsmålet, én grå linje,
valgene som felter, og Tilbage/Næste nederst. Ét spørgsmål eller én handling pr. skærm. Et enkelt valg går
selv videre; flere valg afsluttes med Næste. Swipe virker som i dag.

Introen kører i den fane, hvor tingen hører hjemme: præferencerne på Plan, skabet på Skab. Bundbjælken
bliver stående og lyser den fane op, man står i, så man lærer, hvor tingene bor, ved at gå vejen.
Tandhjulet og kurven er skjult, mens introen kører, som ved guiderne i dag.

## Det, der findes i dag

- Plan: kortet "Velkommen til Mad app" med knappen "Opret præferencer" og en guide på otte trin
  (personer → allergier → madlavninger → vigtigt for jer → butikker → indkøbsture → butikker pr. tur → oversigt).
  Planknapperne er skjult, indtil præferencerne er gemt.
- Plan: boksen "Mangler API-nøgle" øverst, når der ikke er en nøgle.
- Skab: kortet "Hvad vil I altid have på hylden?" med "Ikke nu" / "Kom i gang" og en guide på fire trin.
- Skab: "+ Tilføj" med billeder, video eller skriv selv.
- Snak: "?" med hjælp til den viste del.
- Ingenting forklarer fanerne, kurven, tandhjulet, swipe, langt tryk eller træk til kurv/spist/smidt ud.

## Kæden

Ti skærme. En typisk husstand er igennem med 11 tryk (plus billederne af skabet) på under to minutter.

| Nr | Skærm (overskriften) | Den grå linje | Valgene | Ét tryk → | Findes? |
|---|---|---|---|---|---|
| 0 | **Velkommen til Mad app** | Planlæg ugen ud fra det, I har, og ugens tilbud. Et par hurtige valg først – det tager under to minutter. | [Kom i gang] · lille ghost: "Jeg har en gemt kopi" | Kom i gang → 1. Gemt kopi → "Hent fra fil / Indsæt tekst" (findes under Præferencer › Dine data) og hele introen springes over. | Delvist (kortet på Plan) |
| 1 | **Hvor mange er I?** | Så passer mængderne i opskrifter og indkøb. | Tal 1–8 | Tallet går selv videre. | Ja (trin P) |
| 2 | **Er der allergier i husstanden?** | Retter med det – også spor af det – bliver aldrig foreslået. | Nyt felt **Ingen allergier** øverst + chips som i dag | "Ingen allergier" går selv videre. Vælger man chips: Næste. | Ja (trin allergier) – nyt: "Ingen" |
| 3 | **Hvor mange gange vil I lave mad om ugen?** | De andre dage bliver til rester eller noget nemt. | Tal 1–7 | Tallet går selv videre. | Ja (trin M) |
| 4 | **Hvor handler I?** | Vælg en eller flere. % = appen har deres tilbud. | Logo-felter som i dag (Rema 1000 og Netto er valgt på forhånd) | Næste. Med standardvalget er ét tryk nok. | Ja (trin butikker) |
| 5 | **Sådan ser det ud** | – | Oversigten som i dag | Gem præferencer → 6. | Ja (trin oversigt) |
| 6 | **Sæt nøglen ind** | Forslag til retter, Snak og billeder af skab og kvitteringer kræver en nøgle. Plan, skab og indkøbsliste virker uden. | Feltet fra boksen "Mangler API-nøgle" + [Gem] · ghost [Senere] | Gem → 7. Senere → 7, og boksen på Plan bliver som i dag. | Delvist (boksen) |
| 7 | **Hvad har I derhjemme?** (på Skab) | Tag billeder af køleskab, fryser og skab – eller skriv det selv. Så bruger den første plan det op. | [📷 Tag billeder] · [✏️ Skriv selv] · ghost [Skabet er tomt] | Billeder → det flow, der findes (bunke → send → "Genkendte 5/7 ting" → læg i skabet) → 8. Skriv selv → feltet med autoliste → Næste → 8. Uden nøgle er "Tag billeder" grå med linjen "kræver nøglen". | Delvist (+ Tilføj) – nyt: i guide-rammen |
| 8 | **Vil I have faste varer på hylden?** (på Skab) | Salt, olie, toiletpapir og jeres egne faste varer. Appen siger til, når de er på tilbud. | [Ja, vælg dem] · ghost [Ikke nu] | Ja → de fire skærme, der findes (basis → husholdning → primærvarer → oversigt → Gem) → 9. Ikke nu → 9, og kortet i Skab bliver som i dag. | Ja (guiden) – nyt: spørgsmålet som skærm |
| 9 | **I er klar** (på Plan) | Fire linjer med fanernes ikoner: **Plan** ugens retter · **Snak** sig det med ord · **Skab** det, I har · **Opskrifter** find, tilføj, fra Instagram. Én linje til: kurven nederst til højre er indkøbslisten, tandhjulet er præferencerne. | [Planlæg denne uge] (storknap) · ghost [Se mig omkring først] | Planlæg → "Planlæg denne uge" starter. Se mig omkring → Plan som i dag. | Nej |

Skærm 8 er den, jeg ville tage ud først, hvis kæden føles lang. Kortet i Skab gør det samme job i dag, og
Apple-retningslinjen siger "udskyd opsætning, der ikke er nødvendig". Den står her, fordi "Ikke nu" kun
koster ét tryk, og fordi standardvalgene gør "Ja" til fire tryk på Næste.

Rækkefølgen er valgt sådan: præferencerne først, fordi de er hurtige og giver noget med det samme; nøglen før
skabet, fordi billederne af skabet kræver den; skabet før den første plan, fordi "Tøm skabet" er den første
prioritet i enhver plan, og en plan med tomt skab viser ikke, hvad appen kan.

## Det, der bevidst ikke er med – og hvor det bor i stedet

| Udeladt | Hvorfor | Hvor det spørges i stedet |
|---|---|---|
| Vigtigt for jer (Tøm skabet, Bedste tilbud, prioriteter) | Bliver allerede spurgt ved hver plan: "Hvad er vigtigt denne gang?" | Første plan. Svaret gemmes som udgangspunkt i præferencerne, så næste plan starter med det. Kan stadig rettes under Præferencer. |
| Indkøbsture om ugen og butikker pr. tur | Betyder først noget, når der skal købes ind. Standard (én tur, én butik) er et gyldigt svar. | Første gang kurven åbnes med en plan: de to skærme i samme ramme, eller lad standard gælde og vis "Skift butik" som i dag. |
| Økologi, frugt og grønt enkeltvis, del kvitteringer, instruktioner, favoritter, kan ikke lide, justeringer | Ændrer ikke den første uge. | Præferencer › Flere indstillinger som i dag. |
| Læg appen på hjemmeskærmen | Folk skal have haft glæde af appen, før man beder om noget. | Én hint-linje på Plan, når den første plan er gemt (iPhone: Del → Føj til hjemmeskærm). Vises én gang. |
| Fanerne, kurven, tandhjulet, swipe, langt tryk, træk | Bevægelser læres der, hvor de bruges, ikke på en skærm i forvejen. | Første-gangs-hints i fanen, se nedenfor. |

## Første-gangs-hints i fanerne

Én linje pr. fane, grå, dér hvor handlingen er. Forsvinder, når handlingen er gjort første gang.

| Hvor | Hint | Væk når | Findes? |
|---|---|---|---|
| Enhver guide, første skærm | Swipe til siden for at gå frem og tilbage | Første swipe | Nej |
| Plan, ugen | Tryk på en kokkehue for at åbne retten | Første tryk på en kokkehue | Nej |
| Skab, hylden | Træk en vare for at spise den, smide den ud eller købe mere. Hold på en for at ændre den | Første træk og første lange tryk (i dag står linjen altid) | Ja (`skabForkl`) |
| Opskrifter, kogebogen | Bladr for at se retterne › · swipe op for at lukke | Første bladring | Ja (omslaget) |
| Indkøb, listen | Swipe mellem afdelingerne · ✓ købt, ✕ ikke i dag | Første "Færdig" | Nej |
| Snak | "?" med det, man kan her | Bliver (det er et "?", ikke en hint) | Ja |

## Tilstand og genstart (kort)

- `st.opsat` (præferencer) og `st.hylde.opsat` (hylden) findes. Nyt: `st.intro = {trin, faerdig}`.
  Introen starter, når `nyBruger()` er sand, og genoptager ved `st.intro.trin`, hvis den blev lukket undervejs.
- × lukker hele introen. Det, der allerede er gemt (fx præferencerne), bliver. Introen vises ikke igen af sig
  selv, men kan åbnes under Præferencer: "Gå introen igennem igen".
- Hver del gemmer ved sin egen afslutning, som i dag (kladde indtil Gem). Kæden er kun det, der sker efter Gem.
- Hints: `st.hint = {guideSwipe:true, kokkehue:true, kurv:true, hjemmeskaerm:true}`; nøglen slettes, når
  handlingen er gjort.
- Den egentlige byggeomkostning er skærm 7: "+ Tilføj"-delen af Skab skal kunne vises inde i guide-rammen.
  Resten er eksisterende skærme med en anden knap til sidst.

## Reglerne, introen følger

Udledt af kilderne i `ux-regler.md` (afsnit C):

1. Valgfri og kort: kan lukkes fra første skærm, vises aldrig igen af sig selv, kan findes under Præferencer.
2. Ét spørgsmål pr. skærm. Overskriften er spørgsmålet. Én hjælpelinje, ingen links.
3. Kun det, der ændrer den første uge. Resten har standardværdier og spørges, hvor det bruges.
4. Lær ved at gøre: skabet fyldes med rigtige billeder i stedet for en skærm, der forklarer skabet.
5. Tilbage findes altid. Ét tryk fører videre; flere valg afsluttes med én knap.
6. Fremdrift som prik-striben, ikke som en liste over alle trin.
7. Nøglen bedes om med grunden, og kan udskydes. Så minder boksen på Plan om den, som i dag.
8. Ingen store hentninger i introen. Talegenkendelsen hentes først, når video bruges, som i dag.
9. Bevægelser forklares i fanen første gang, ikke i introen.
10. Standardværdierne er valgt, så Næste altid er et gyldigt svar.
