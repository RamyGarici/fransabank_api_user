document.addEventListener("DOMContentLoaded", function () {
    console.log("Script chargé et exécuté !");

    const clientField = document.querySelector("#id_client");
    const employeField = document.querySelector("#id_employe");
    const meetingUrlField = document.querySelector("#id_meeting_url_preview");

    console.log("Champs détectés :", clientField, employeField, meetingUrlField);

    function updateMeetingUrl() {
        if (clientField && employeField && meetingUrlField) {
            const client = clientField.value;
            const employe = employeField.value;
            console.log("Changement détecté :", client, employe);

            if (client && employe) {
                const meetingUrl = `https://meet.jit.si/${client}${employe}`;
                meetingUrlField.value = meetingUrl;
                console.log("URL mise à jour :", meetingUrl);
            } else {
                meetingUrlField.value = "";
            }
        }
    }

    // ✅ Utiliser l'événement `input` pour détecter les changements des Raw ID Fields
    if (clientField) clientField.addEventListener("input", updateMeetingUrl);
    if (employeField) employeField.addEventListener("input", updateMeetingUrl);

    // ✅ Ajouter un intervalle pour détecter les changements liés à la popup Django admin
    setInterval(updateMeetingUrl, 1000);
});
