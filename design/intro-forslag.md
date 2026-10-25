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
- Præferencer: "Ret præferencer" og "Nulstil præferencer" øverst. Nulstil sletter kun præferencerne, og
  velkomstkortet kommer tilbage på Plan. Der er ingen måde at nulstille hele appen på.
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

## Hvornår introen kommer

Introen kommer af sig selv én gang, og den kan altid startes igen under Præferencer.

| Situation | Hvad sker der |
|---|---|
| **Første gang appen åbnes** | Introen starter af sig selv på Plan, fra skærm 0. |
| **Appen lukkes midt i introen** (telefonen låses, appen skiftes) | Introen fortsætter fra den skærm, man var på, næste gang appen åbnes. |
| **× midt i introen** | Introen lukker. Det, der allerede er gemt, bliver. Den kommer ikke igen af sig selv. Kortene "Velkommen til Mad app" på Plan og "Hvad vil I altid have på hylden?" på Skab står, som de gør i dag, for det, der mangler. |
| **Præferencer › Ny opsætning** | Velkomstkortet kommer igen, og introen går hele vejen igennem med de valg, man har. Intet slettes. |
| **Præferencer › Nulstil præferencer** | Præferencerne slettes, og velkomstkortet kommer tilbage på Plan. Skab, plan og indkøbsliste bliver. |
| **Præferencer › Nulstil hele appen** | Alt slettes, og appen starter forfra med velkomstkortet, som første gang. |

Velkomstkortet er skærm 0. Det kommer altså igen på tre måder: Ny opsætning, Nulstil præferencer og Nulstil
hele appen. "Jeg har en gemt kopi" står på det hver gang, så man altid kan hente en kopi ind i stedet.

**Når introen startes igen** med Ny opsætning, er det en gennemgang af det, man har, ikke en ny start:

- Alle valg står på det, man valgte sidst. Næste beholder det, og man retter kun det, der er ændret.
  Sådan virker præferenceguiden og hylde-guiden allerede i dag.
- Intet slettes. Hver del gemmer først ved sin egen Gem, og × undervejs lader alt stå, som det var.
- Skærm 6 (nøglen): har telefonen en nøgle, står der "Nøglen er sat ✓" med Næste. Feltet kommer kun frem,
  hvis man vil skifte den.
- Skærm 7 (skabet): billeder og "Skriv selv" tilføjer kun det nye, som i dag. Skabet tømmes ikke. Står der
  allerede varer i skabet, siger linjen "I har 23 ting i skabet. Tag billeder af det nye, eller gå videre", og
  "Skabet er tomt" hedder i stedet "Gå videre".
- Skærm 9: "Se mig omkring først" hedder i stedet "Færdig".

## Start forfra under Præferencer

De fire knapper deles i to grupper, så det, der sletter noget, ikke står ved siden af det, man bruger til hverdag.

| Hvor | Knap | Hvad den gør | Findes? |
|---|---|---|---|
| Øverst, under "Dine præferencer" | **Ret præferencer** | Åbner kun præferenceguiden | Ja |
| Øverst, under "Dine præferencer" | **Ny opsætning** | Hele introen fra velkomstkortet, med de valg, man har | Nej |
| Nederst, Flere indstillinger › Dine data › Start forfra | **Nulstil præferencer** | Sletter præferencerne. Velkomstkortet kommer på Plan | Ja, flyttes hertil fra toppen |
| Nederst, Flere indstillinger › Dine data › Start forfra | **Nulstil hele appen** | Sletter alt og starter forfra | Nej |

"Start forfra" står lige under "Gem kopi", så kopien er det sidste, man ser, før man nulstiller.

### Nulstil hele appen

Ét tryk åbner én skærm i guide-rammen. Det er ikke browserens `confirm`, fordi listen er for lang til den, og fordi
skærmen skal kunne tilbyde en kopi først.

| Del | Indhold |
|---|---|
| Overskrift | **Nulstil hele appen?** |
| Grå linje | Appen bliver som første gang, I åbnede den. Det kan ikke fortrydes. |
| Slettes | Plan, skab, indkøbsliste, præferencer, altid på hylden, jeres egne opskrifter, favoritter, snak og tallene under Forbrug. |
| Bliver | Det, I har delt med andre (opskrifter, kvitteringer), og det, appen har hentet: talegenkendelsen og billederne til Lav retten, så de ikke skal hentes igen. |
| Valg | Chip **Slet også nøglen**, slået fra som standard. Linjen under: "Fx hvis telefonen skal bruges af en anden." |
| Knapper | Ghost **Gem kopi først** til venstre. Fyldt orange **Nulstil alt** til højre. × lukker uden at gøre noget. |

Efter "Nulstil alt":

1. Feedback, der venter på net, prøves sendt én gang. Det, der ikke kommer afsted, slettes med resten.
2. Husstandens data og forbrugstallene slettes. Nøglen slettes kun, hvis chippen er valgt.
3. Appen genindlæser og starter med velkomstkortet, som første gang. Det er kvitteringen; der er ingen toast.

Hvad der ligger hvor på telefonen, til den, der bygger det:

| Gemt som | Indhold | Ved Nulstil hele appen |
|---|---|---|
| `localStorage` "opbrugt" | Alt om husstanden: plan, skab, indkøbsliste, præferencer, hylde, egne opskrifter, favoritter, snak, historik, feedback der venter | Slettes |
| `localStorage` "opbrugt_forbrug" | Forbruget af nøglen på denne telefon | Slettes |
| `localStorage` "opbrugt_api_noegle" | Nøglen | Slettes kun med "Slet også nøglen" |
| `localStorage` "opbrugt_tale…" | Om talegenkendelsen er hentet og godkendt | Bliver |
| IndexedDB "madapp" › trinbilleder | Billederne til Lav retten | Bliver |
| Cache Storage | Appens filer (service worker) og talegenkendelsen (ca. 250 MB) | Bliver |

## Tilstand (kort)

- `st.opsat` (præferencer) og `st.hylde.opsat` (hylden) findes. Nyt: `st.intro = {trin, faerdig, igen}`.
  Introen starter af sig selv, når `nyBruger()` er sand (funktionen findes, men bruges ikke i dag), eller når
  `st.intro.trin` er sat og `faerdig` ikke er. × og den sidste skærm sætter `faerdig`. "Ny opsætning" sætter
  `igen`, som styrer teksterne ovenfor.
- Hver del gemmer ved sin egen afslutning, som i dag (kladde indtil Gem). Kæden er kun det, der sker efter Gem.
- Hints: `st.hint = {guideSwipe:true, kokkehue:true, kurv:true, hjemmeskaerm:true}`; nøglen slettes, når
  handlingen er gjort.
- Den egentlige byggeomkostning er skærm 7: "+ Tilføj"-delen af Skab skal kunne vises inde i guide-rammen.
  Resten er eksisterende skærme med en anden knap til sidst.

## Reglerne, introen følger

Udledt af kilderne i `ux-regler.md` (afsnit C):

1. Valgfri og kort: kan lukkes fra første skærm, vises aldrig igen af sig selv, kan startes igen fra
   velkomstkortet under Præferencer › Ny opsætning med de valg, man har i forvejen.
2. Ét spørgsmål pr. skærm. Overskriften er spørgsmålet. Én hjælpelinje, ingen links.
3. Kun det, der ændrer den første uge. Resten har standardværdier og spørges, hvor det bruges.
4. Lær ved at gøre: skabet fyldes med rigtige billeder i stedet for en skærm, der forklarer skabet.
5. Tilbage findes altid. Ét tryk fører videre; flere valg afsluttes med én knap.
6. Fremdrift som prik-striben, ikke som en liste over alle trin.
7. Nøglen bedes om med grunden, og kan udskydes. Så minder boksen på Plan om den, som i dag.
8. Ingen store hentninger i introen. Talegenkendelsen hentes først, når video bruges, som i dag.
9. Bevægelser forklares i fanen første gang, ikke i introen.
10. Standardværdierne er valgt, så Næste altid er et gyldigt svar.
