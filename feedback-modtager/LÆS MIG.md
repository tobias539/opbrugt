# Feedback fra Mad app

Feedback fra appen (feedback-feltet under Snak og kritik skrevet i snakken) sendes anonymt til et
Google Apps Script. Scriptet gemmer hver besked som en tekstfil i Google Drive › Privat › mad › feedback.
Mappen synkroniseres til `My Drive\Privat\mad\feedback` på computeren. Den er udeladt fra git,
så feedbacken ikke kommer med i det offentlige repo.

## Opsætning (én gang)

1. Gå til https://script.google.com og vælg **Nyt projekt**. Kald det fx "Mad app feedback".
2. Slet det, der står i editoren, og indsæt indholdet af `feedback.gs`. Gem.
3. Vælg **Udrul › Ny udrulning**. Tryk på tandhjulet ved "Vælg type", og vælg **Webapp**.
   - Udfør som: **Mig**
   - Hvem har adgang: **Alle**
4. Tryk **Udrul** og godkend adgangen til din Google Drive. Google advarer om en "ikke-bekræftet app",
   fordi det er dit eget script: vælg **Avanceret › Gå til Mad app feedback**.
5. Kopiér **webapp-adressen** (slutter på `/exec`). Den skal sættes ind i `FEEDBACK_URL` i `opbrugt/index.html`.

Adressen ligger i det offentlige repo. Alle, der finder den, kan altså sende tekst til mappen, men ikke læse noget.
Hver besked er højst 4.000 tegn.

## Opsamling

Åbn en Claude-session i mappen `mad`, og skriv fx:
"Lav en opsamling på feedbacken i mappen feedback – hvad går igen, og hvad bør vi lave først?"
