document.addEventListener("DOMContentLoaded", function () {

    const villeSelect = document.getElementById("ville");
    const quartierSelect = document.getElementById("quartier");
    const fraisLivraison = document.getElementById("frais-livraison");
    const boutonConfirmer = document.getElementById("btn-confirmer");


    // Vérifier que les éléments existent
    if (!villeSelect || !quartierSelect) {
        console.error("Les champs ville ou quartier sont introuvables.");
        return;
    }


    // Quand la ville change
    villeSelect.addEventListener("change", function () {

        const villeChoisie = this.value;


        // Réinitialiser le quartier
        quartierSelect.innerHTML = "";

        const optionInitiale = document.createElement("option");

        optionInitiale.value = "";
        optionInitiale.textContent = "-- Choisir un quartier --";

        quartierSelect.appendChild(optionInitiale);


        // Réinitialiser les frais
        fraisLivraison.textContent = "0 FCFA";


        // Désactiver le bouton
        boutonConfirmer.disabled = true;


        // Aucune ville choisie
        if (!villeChoisie) {

            quartierSelect.disabled = true;

            return;
        }


        // Filtrer les quartiers de la ville
        const quartiers = lieux.filter(function (lieu) {

            return lieu.ville === villeChoisie;

        });


        // Ajouter les quartiers
        quartiers.forEach(function (lieu) {

            const option = document.createElement("option");

            option.value = lieu.id;

            option.textContent =
                lieu.quartier +
                " — " +
                lieu.frais +
                " FCFA";

            option.dataset.frais = lieu.frais;

            quartierSelect.appendChild(option);

        });


        // Activer le quartier
        quartierSelect.disabled = false;

    });


    // Quand le quartier change
    quartierSelect.addEventListener("change", function () {

        const lieuId = this.value;


        // Aucun quartier
        if (!lieuId) {

            fraisLivraison.textContent = "0 FCFA";

            boutonConfirmer.disabled = true;

            return;
        }


        // Trouver le lieu sélectionné
        const lieu = lieux.find(function (lieu) {

            return String(lieu.id) === String(lieuId);

        });


        if (lieu) {

            // Afficher automatiquement les frais
            fraisLivraison.textContent =
                lieu.frais + " FCFA";

            // Activer le bouton
            boutonConfirmer.disabled = false;

        }

    });

});