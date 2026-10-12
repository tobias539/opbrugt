# Feedback og fælles opskrifter fra Mad app

Et Google Apps Script (`feedback.gs`) tager imod fire ting fra appen:

- **Feedback**: det, der sendes fra Feedback under Snak, og ændringer af holdbarhed i skabet. Det sendes
  anonymt, og hver besked gemmes som en tekstfil i Google Drive › Privat › mad › feedback.
- **Fælles opskrifter**: egne opskrifter, man vælger at dele. Hver gemmes som en JSON-fil i
  Google Drive › Privat › mad › opskrifter-delt, og alle, der bruger appen, kan se dem i kogebogen.
- **Emojis**: når nogen vælger en anden emoji til en vare i skabet, sendes varens navn og emojien anonymt.
  Valgene tælles sammen i Google Drive › Privat › mad › emojis › emojis.json, og appen viser dem som
  "Andre har valgt". Kun emojis tages imod.
- **Kvitteringer**: når en kvittering scannes og lægges i skabet, sendes billedet (formindsket) og varelinjerne
  uden navn. De gemmes i Google Drive › Privat › mad › kvitteringer som en `.jpg` og en `.json` med samme navn.
  Normalpriserne (ikke tilbud) samles i `kvitteringer/priser.json` – de sidste 5 pr. vare og butik – og appen
  henter midterværdien, så alles priser bliver bedre. Kan slås fra i appen under Præferencer › Del kvitteringer.

Mapperne synkroniseres til `My Drive\Privat\mad\` på computeren. `feedback/`, `emojis/` og `kvitteringer/`
er udeladt fra git, så de ikke kommer med i det offentlige repo.

## Opsætning (én gang)

1. Gå til https://script.google.com og vælg **Nyt projekt**. Kald det fx "Mad app feedback".
2. Slet det, der står i editoren, og indsæt indholdet af `feedback.gs`. Gem.
3. Vælg **Udrul › Ny udrulning**. Tryk på tandhjulet ved "Vælg type", og vælg **Webapp**.
   - Udfør som: **Mig**
   - Hvem har adgang: **Alle**
4. Tryk **Udrul** og godkend adgangen til din Google Drive. Google advarer om en "ikke-bekræftet app",
   fordi det er dit eget script: vælg **Avanceret › Gå til Mad app feedback**.
5. Kopiér **webapp-adressen** (slutter på `/exec`). Den skal sættes ind i `FEEDBACK_URL` i `opbrugt/index.html`.

## Når scriptet ændres

Indsæt den nye kode, gem, og vælg **Udrul › Administrer udrulninger** › blyanten › **Version: Ny version** ›
**Udrul**. Så beholder webappen den samme adresse, og appen behøver ikke opdateres.

Adressen ligger i det offentlige repo. Alle, der finder den, kan altså sende tekst og opskrifter,
og de delte opskrifter og de samlede priser kan læses af alle. Feedbacken og kvitteringerne kan ikke læses udefra. Hver besked er højst 4.000 tegn.

## Opsamling

Åbn en Claude-session i mappen `mad`, og skriv fx:
"Lav en opsamling på feedbacken i mappen feedback – hvad går igen, og hvad bør vi lave først?"
