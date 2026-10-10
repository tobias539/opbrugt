/* Mad app – modtager feedback.
   Appen sender {tekst, kilde, tid, version}. Hver besked gemmes som en tekstfil i
   Google Drive › Privat › mad › feedback (mappen oprettes, hvis den mangler).
   Der gemmes ikke noget om, hvem der har skrevet. Opsætning: se LÆS MIG.md. */

const STI = ["Privat", "mad", "feedback"];
const MAKS = 4000;

function mappe() {
  let f = DriveApp.getRootFolder();
  for (const navn of STI) {
    const fundet = f.getFoldersByName(navn);
    f = fundet.hasNext() ? fundet.next() : f.createFolder(navn);
  }
  return f;
}

function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    const tekst = String(d.tekst || "").trim().slice(0, MAKS);
    if (!tekst) return svar({ ok: false, fejl: "tom besked" });
    const kilde = d.kilde === "snak" ? "snak" : "feedback";
    const nu = new Date();
    const filnavn = Utilities.formatDate(nu, "Europe/Copenhagen", "yyyy-MM-dd HH.mm.ss") + " " + kilde + ".txt";
    const indhold =
      "Tidspunkt: " + Utilities.formatDate(nu, "Europe/Copenhagen", "yyyy-MM-dd HH:mm") + "\n" +
      "Kilde: " + (kilde === "snak" ? "skrevet i snakken" : "feedback-feltet") + "\n" +
      "App-version: " + String(d.version || "").slice(0, 10) + "\n\n" +
      tekst + "\n";
    mappe().createFile(filnavn, indhold, MimeType.PLAIN_TEXT);
    return svar({ ok: true });
  } catch (err) {
    return svar({ ok: false, fejl: String(err) });
  }
}

/* Åbner man adressen i en browser, kan man se, at den virker */
function doGet() {
  return svar({ ok: true, besked: "Mad app feedback-modtager kører" });
}

function svar(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
