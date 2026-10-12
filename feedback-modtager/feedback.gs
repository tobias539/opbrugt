/* Mad app – modtager feedback og fælles opskrifter.
   Feedback: appen sender {tekst, kilde, tid, version}. Hver besked gemmes som en tekstfil i
   Google Drive › Privat › mad › feedback. Der gemmes ikke noget om, hvem der har skrevet.
   Opskrifter: appen sender {type:"opskrift", opskrift:{...}}. Hver opskrift gemmes som en JSON-fil i
   Google Drive › Privat › mad › opskrifter-delt, og ?type=opskrifter henter dem alle.
   Emojis: appen sender {type:"emoji", vare, emoji}, når nogen vælger en anden emoji til en vare i skabet.
   Valgene tælles sammen i Google Drive › Privat › mad › emojis › emojis.json ({vare: {emoji: antal}}),
   og ?type=emojis henter dem, så appen kan vise, hvad andre har valgt.
   Mapperne oprettes, hvis de mangler. Opsætning: se LÆS MIG.md. */

const FEEDBACK_STI = ["Privat", "mad", "feedback"];
const OPSKRIFT_STI = ["Privat", "mad", "opskrifter-delt"];
const EMOJI_STI = ["Privat", "mad", "emojis"];
const EMOJI_FIL = "emojis.json";
const MAKS = 4000;
const KILDER = { snak: "skrevet i snakken", holdbarhed: "holdbarhed ændret i skabet", feedback: "feedback-feltet" };

function mappe(sti) {
  let f = DriveApp.getRootFolder();
  for (const navn of sti) {
    const fundet = f.getFoldersByName(navn);
    f = fundet.hasNext() ? fundet.next() : f.createFolder(navn);
  }
  return f;
}

function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    if (d.type === "opskrift") return gemOpskrift(d.opskrift);
    if (d.type === "emoji") return gemEmoji(d);
    const tekst = String(d.tekst || "").trim().slice(0, MAKS);
    if (!tekst) return svar({ ok: false, fejl: "tom besked" });
    const kilde = KILDER[d.kilde] ? d.kilde : "feedback";
    const nu = new Date();
    const filnavn = Utilities.formatDate(nu, "Europe/Copenhagen", "yyyy-MM-dd HH.mm.ss") + " " + kilde + ".txt";
    const indhold =
      "Tidspunkt: " + Utilities.formatDate(nu, "Europe/Copenhagen", "yyyy-MM-dd HH:mm") + "\n" +
      "Kilde: " + KILDER[kilde] + "\n" +
      "App-version: " + String(d.version || "").slice(0, 10) + "\n\n" +
      tekst + "\n";
    mappe(FEEDBACK_STI).createFile(filnavn, indhold, MimeType.PLAIN_TEXT);
    return svar({ ok: true });
  } catch (err) {
    return svar({ ok: false, fejl: String(err) });
  }
}

/* Én fil pr. opskrift; sendes den samme opskrift igen, bliver filen opdateret */
function gemOpskrift(o) {
  if (!o || typeof o.id !== "string" || !o.t || !Array.isArray(o.ing) || !Array.isArray(o.trin)) return svar({ ok: false, fejl: "ikke en opskrift" });
  const json = JSON.stringify(o);
  if (json.length > 100000) return svar({ ok: false, fejl: "for stor" });
  const navn = String(o.id).replace(/[^a-z0-9-]/gi, "").slice(0, 100) + ".json";
  const m = mappe(OPSKRIFT_STI), fundet = m.getFilesByName(navn);
  if (fundet.hasNext()) fundet.next().setContent(json);
  else m.createFile(navn, json, MimeType.PLAIN_TEXT);
  return svar({ ok: true });
}

/* Emoji-valg tælles sammen i én fil. Kun emojis (højst 3 tegn-klynger) og korte varenavne tages imod.
   Skriver to telefoner på samme tid, venter den ene på den anden. */
function emojiFil() {
  const m = mappe(EMOJI_STI), fundet = m.getFilesByName(EMOJI_FIL);
  return fundet.hasNext() ? fundet.next() : m.createFile(EMOJI_FIL, "{}", MimeType.PLAIN_TEXT);
}
function erEmoji(s) {
  return typeof s === "string" && s.length <= 16 && /^(\p{Extended_Pictographic}|\p{Emoji_Component}|\u200d|\ufe0f)+$/u.test(s) &&
    /\p{Extended_Pictographic}|\p{Regional_Indicator}/u.test(s);
}
function gemEmoji(d) {
  const vare = String(d.vare || "").toLowerCase().trim().slice(0, 60), emoji = String(d.emoji || "");
  if (!vare || !erEmoji(emoji)) return svar({ ok: false, fejl: "ikke en emoji" });
  const laas = LockService.getScriptLock();
  laas.waitLock(10000);
  try {
    const fil = emojiFil();
    let alle = {};
    try { alle = JSON.parse(fil.getBlob().getDataAsString()) || {}; } catch (x) {}
    const v = alle[vare] = alle[vare] || {};
    v[emoji] = (v[emoji] || 0) + 1;
    fil.setContent(JSON.stringify(alle));
  } finally {
    laas.releaseLock();
  }
  return svar({ ok: true });
}

function doGet(e) {
  if (e && e.parameter && e.parameter.type === "emojis") {
    try { return svar({ ok: true, emojis: JSON.parse(emojiFil().getBlob().getDataAsString()) || {} }); }
    catch (x) { return svar({ ok: true, emojis: {} }); }
  }
  if (e && e.parameter && e.parameter.type === "opskrifter") {
    const ud = [], filer = mappe(OPSKRIFT_STI).getFiles();
    while (filer.hasNext()) {
      try { ud.push(JSON.parse(filer.next().getBlob().getDataAsString())); } catch (x) {}
    }
    return svar({ ok: true, opskrifter: ud });
  }
  /* Åbner man adressen i en browser, kan man se, at den virker */
  return svar({ ok: true, besked: "Mad app modtager kører" });
}

function svar(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
