"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO Trip Planner initialized.");

    const optionButtons = Array.from(
        document.querySelectorAll(".choose-option-button")
    );

    const mobilityCards = Array.from(
        document.querySelectorAll("[data-mobility-card]")
    );

    function clearSelectedCards() {
        mobilityCards.forEach(function (card) {
            card.classList.remove("is-selected");
        });
    }

    function selectMobilityOption(button) {
        const optionId = button.dataset.option;
        const optionTitle = button.dataset.optionTitle;

        const selectedCard = document.querySelector(
            `[data-mobility-card="${optionId}"]`
        );

        clearSelectedCards();

        if (selectedCard) {
            selectedCard.classList.add("is-selected");
        }

        optionButtons.forEach(function (optionButton) {
            const title = optionButton.dataset.optionTitle;

            optionButton.textContent = `Choose ${title}`;
        });

        button.textContent = `${optionTitle} Selected`;

        console.log("Selected mobility option:", optionId);
    }

    optionButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            selectMobilityOption(button);
        });
    });
});