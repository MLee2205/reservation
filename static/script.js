

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("reservation-form");
    const tooltip = document.getElementById("tooltip");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Empêche le rechargement de la page

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            // Cacher le tooltip si la réponse est ok
            tooltip.classList.remove("tooltip-visible");
            tooltip.classList.add("tooltip-hidden");

            if (!response.ok) {
                const errorData = await response.json();

                // Afficher le message d'erreur
                tooltip.textContent = errorData.error || "Erreur inconnue.";
                tooltip.classList.remove("tooltip-hidden");
                tooltip.classList.add("tooltip-visible");

                // Afficher les places disponibles si l'erreur concerne les places
                if (errorData.places_disponibles !== undefined) {
                    tooltip.innerHTML += `<br>Places disponibles : ${errorData.places_disponibles}`;
                }
            } else {
                // Si la réservation réussit, vous pouvez gérer la réponse ici (par exemple, téléchargement du ticket)
                const ticketLink = document.createElement("a");
                ticketLink.href = URL.createObjectURL(await response.blob());
                ticketLink.download = "ticket.pdf";
                ticketLink.click();
            }
        } catch (error) {
            console.error("Erreur lors de l'envoi de la réservation:", error);
        }
    });
});
