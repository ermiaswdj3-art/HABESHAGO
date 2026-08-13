"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO Trip Planner initialized.");

    const optionButtons = Array.from(
        document.querySelectorAll(".choose-option-button")
    );

    const mobilityCards = Array.from(
        document.querySelectorAll("[data-mobility-card]")
    );

    const categorySelector = document.querySelector(
        "[data-ride-category-selector]"
    );

    const categoryButtons = Array.from(
        document.querySelectorAll("[data-ride-category]")
    );

    const categoryFeedback = document.querySelector(
        "[data-ride-category-feedback]"
    );

    function clearSelectedCards() {
        mobilityCards.forEach(function (card) {
            card.classList.remove("is-selected");
        });
    }

    function resetButtonLabels() {
        optionButtons.forEach(function (optionButton) {
            const title = optionButton.dataset.optionTitle;

            optionButton.textContent = `Choose ${title}`;
            optionButton.disabled = false;
        });
    }

    function hideCategorySelector() {
        if (!categorySelector) {
            return;
        }

        categorySelector.hidden = true;
        categorySelector.classList.add("is-hidden");
    }

    function showCategorySelector() {
        if (!categorySelector) {
            return;
        }

        categorySelector.hidden = false;
        categorySelector.classList.remove("is-hidden");

        categorySelector.scrollIntoView({
            behavior: "smooth",
            block: "nearest",
        });
    }

    function clearSelectedCategories() {
        categoryButtons.forEach(function (button) {
            button.classList.remove("is-selected");
            button.disabled = false;
        });
    }

    function setCategoryFeedback(message) {
        if (!categoryFeedback) {
            return;
        }

        categoryFeedback.textContent = message;
    }

    function showSelectedOption(button) {
        const optionId = button.dataset.option;
        const optionTitle = button.dataset.optionTitle;

        const selectedCard = document.querySelector(
            `[data-mobility-card="${optionId}"]`
        );

        clearSelectedCards();
        resetButtonLabels();

        if (selectedCard) {
            selectedCard.classList.add("is-selected");
        }

        button.textContent = `${optionTitle} Selected`;

        if (optionId === "ride") {
            showCategorySelector();
        } else {
            hideCategorySelector();
        }
    }

    async function saveMobilityOption(button) {
        const optionId = button.dataset.option;
        const optionTitle = button.dataset.optionTitle;
        const estimatedFare = Number(
            button.dataset.optionFare
        );
        const estimatedEta =
            button.dataset.optionEta || "";
        const recommendation =
            button.dataset.optionRecommendation || "";

        optionButtons.forEach(function (optionButton) {
            optionButton.disabled = true;
        });

        button.textContent = `Saving ${optionTitle}...`;

        try {
            const response = await fetch(
                "/api/trip/service",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        service: optionId,
                        estimated_fare: estimatedFare,
                        estimated_eta: estimatedEta,
                        recommendation: recommendation,
                    }),
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "The service could not be selected."
                );
            }

            showSelectedOption(button);

            console.log(
                "Mobility service saved:",
                result.trip
            );
        } catch (error) {
            console.error(
                "Mobility service save failed:",
                error
            );

            alert(
                error.message ||
                "We could not save your selection."
            );

            resetButtonLabels();
        }
    }

    async function saveRideCategory(button) {
        const category = button.dataset.rideCategory;
        const categoryTitle = button.dataset.categoryTitle;

        clearSelectedCategories();
        setCategoryFeedback(
            `Saving ${categoryTitle}...`
        );

        categoryButtons.forEach(function (categoryButton) {
            categoryButton.disabled = true;
        });

        try {
            const response = await fetch(
                "/api/trip/category",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Telegram-Init-Data": (
                            window.Telegram &&
                            window.Telegram.WebApp
                        )
                            ? window.Telegram.WebApp.initData
                            : "",
                    },
                    body: JSON.stringify({
                        category: category,
                    }),
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "The ride category could not be saved."
                );
            }

            button.classList.add("is-selected");
            button.disabled = false;

            setCategoryFeedback(
                `${categoryTitle} selected. Opening summary...`
            );

            console.log(
                "Ride category saved:",
                result.trip
            );

            window.location.href = "/booking-summary";
        } catch (error) {
            console.error(
                "Ride category save failed:",
                error
            );

            setCategoryFeedback(
                error.message ||
                "We could not save your ride category."
            );

            categoryButtons.forEach(function (
                categoryButton
            ) {
                categoryButton.disabled = false;
            });
        }
    }

    optionButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            saveMobilityOption(button);
        });
    });

    categoryButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            saveRideCategory(button);
        });
    });

    hideCategorySelector();
});