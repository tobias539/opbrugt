# Billedstil for trinene i Mad app

Version: 1

Appen læser denne fil, hver gang Claude tegner et billede til et trin i "Lav retten". Ret den her, så gælder det
alle nye billeder. Hæv versionsnummeret, hvis de gamle billeder skal tegnes om.

## Formål

Hvert billede viser præcis det, man gør i trinnet, så man kan se det på et øjeblik, mens man står ved komfuret med
beskidte fingre: hvad der ligger på brættet eller er i gryden, og hvordan det skal se ud, når trinnet er færdigt.
Billederne i én opskrift er en serie fra samme kogebog, og alle opskrifter i appen skal se ud, som om de kommer fra
samme bog.

## Fast stil (alle billeder)

- Flad, moderne illustration i vektor. Ikke fotorealisme. Ingen tekst, bogstaver eller tal i billedet.
- Format: SVG med `viewBox="0 0 800 500"`. Ingen `<script>`, `<image>`, `<foreignObject>`, links, eksterne
  ressourcer eller fonte. Højst ca. 12 KB.
- Perspektiv: let skråt ovenfra (ca. 45 grader) ned på en bordplade. Samme bordplade og samme vinkel i alle trin af
  en ret.
- Komposition: hovedhandlingen i midten fylder omkring 60 % af billedet. Højst 5-7 ting i billedet. Rolige, store
  flader og luft omkring tingene.
- Former: bløde, afrundede former. Ingen konturer, eller tynde ensartede konturer (2-3 px) i en mørk, varm farve
  (#2b2218) med lav opacitet.
- Lys: blødt lys fra venstre. Skygger som enkle, halvgennemsigtige ellipser under tingene.
- Hænder: kun når handlingen kræver det (fx hakke, røre, vende). Stiliserede, uden ansigt, samme hudtone og samme
  ærme i alle trin.
- Varme vises med få, stiliserede dampkruseduller. Tid vises aldrig med ure eller tal.
- Ingredienserne skal kunne genkendes på form og farve: gulerod orange med grøn top, pak choi med hvide stilke og
  grønne blade, hakket kød brunt og krummet, ris som små hvide korn osv.
- Maden har altid naturlige, appetitlige farver. Stemningen (nedenfor) ændrer kun omgivelser, palet og lys.

## Serien

- Samme bordplade, samme lys og samme grej (gryde, pande, skærebræt, kniv, skåle) i alle trin af én ret.
- Grejet har samme farve og form fra trin til trin, så billederne tydeligt hører sammen.
- Første trin viser opstarten. Sidste trin viser den færdige ret anrettet på en tallerken.

## Stemning pr. kategori

Alle retter skal se lækre og indbydende ud og appellere til deres kategori. En billig ret må aldrig se billig ud.

- **Hverdag** (standard): lyst køkken, lys træbordplade, hvidt service, grønne accenter (#23523F).
- **Romantisk**: dæmpet, varmt aftenlys, dybe farver (bordeaux, guld, mørkt træ), et stearinlys i baggrunden,
  elegant service og stofserviet.
- **Hyggemad**: varme, mættede farver, rustikt træbord, ternet viskestykke, generøse portioner.
- **Kulinarisk oplevelse**: mørk skifer eller marmor, præcis anretning, moderne grej i stål.
- **Hurtig**: lyst og friskt, få ting, effektivt – én pande, én kniv, ét bræt.
- **Billig**: lys, glad hverdag med friske farver og fokus på gode råvarer. Aldrig trist.
- **Sund** og **vegetar**: lyse grønne og hvide toner, friske krydderurter, meget lys.
- **Børnevenlig**: legende, runde former og glade farver.
- **Dansk klassiker**: hyggeligt dansk køkken, lyst træ, blåt og hvidt porcelæn.
- **Fisk**: kølige, klare blå og grå toner, frisk og rent.
- **Proteinrig**: kraftige, varme farver, mørkt træ, solid støbejernspande.
