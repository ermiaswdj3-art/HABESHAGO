"use strict";

/**
 * HABESHAGO Interactive Destination Search
 *
 * Features:
 * - Shows destination suggestions when search receives focus
 * - Filters destinations while typing
 * - Saves the selected destination to the Flask Trip Context
 * - Opens the pickup map after a successful save
 * - Clears the current visual selection
 * - Supports Recent Places
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO home.js loaded successfully.");

    const greetingText = document.querySelector(
    ".home-greeting-text"
);

async function loadAuthenticatedPassengerGreeting() {
    if (!greetingText) {
        return;
    }

    const telegramWebApp =
        window.Telegram &&
        window.Telegram.WebApp;

    if (!telegramWebApp) {
        console.log(
            "Telegram WebApp context unavailable; " +
            "using public greeting."
        );
        return;
    }

    const initData = String(
        telegramWebApp.initData || ""
    ).trim();

    if (!initData) {
        console.log(
            "Telegram init data unavailable; " +
            "using public greeting."
        );
        return;
    }

    try {
        const response = await fetch(
            "/api/passenger/context",
            {
                method: "GET",
                headers: {
                    "X-Telegram-Init-Data": initData,
                },
            }
        );

        const result = await response.json();

        if (
            !response.ok ||
            !result.success ||
            !result.greeting
        ) {
            throw new Error(
                result.error ||
                "Passenger context could not be loaded."
            );
        }

        greetingText.textContent = result.greeting;

        console.log(
            "Authenticated passenger greeting loaded."
        );
    } catch (error) {
        console.error(
            "Passenger greeting load failed:",
            error
        );
    }
}

loadAuthenticatedPassengerGreeting();

    const searchForm = document.querySelector(".destination-search");

    const searchInput = document.querySelector(
        "#destination-search-input"
    );

    const suggestionSection = document.querySelector(
        ".destination-suggestions"
    );

    const suggestionCards = Array.from(
        document.querySelectorAll(
            ".destination-suggestion-card"
        )
    );

    const emptyState = document.querySelector(
        "[data-destination-empty-state]"
    );

    const selectedPanel = document.querySelector(
        "[data-selected-destination]"
    );

    const selectedName = document.querySelector(
        "[data-selected-destination-name]"
    );

    const clearButton = document.querySelector(
        "[data-clear-destination]"
    );

    const recentPlaceCards = Array.from(
        document.querySelectorAll(
            "[data-recent-destination]"
        )
    );

    if (!searchForm) {
        console.error("Search form was not found.");
        return;
    }

    if (!searchInput) {
        console.error("Destination search input was not found.");
        return;
    }

    if (!suggestionSection) {
        console.error(
            "Destination suggestions section was not found."
        );
        return;
    }

    if (suggestionCards.length === 0) {
        console.error(
            "No destination suggestion cards were found."
        );
        return;
    }

    function normalizeText(value) {
        return String(value || "")
            .trim()
            .toLowerCase();
    }

    function showElement(element) {
        if (!element) {
            return;
        }

        element.hidden = false;
        element.classList.remove("is-hidden");
    }

    function hideElement(element) {
        if (!element) {
            return;
        }

        element.hidden = true;
        element.classList.add("is-hidden");
    }

    function showSuggestions() {
        showElement(suggestionSection);
    }

    function hideSuggestions() {
        hideElement(suggestionSection);
    }

    function filterDestinations() {
        const searchTerm = normalizeText(
            searchInput.value
        );

        let visibleCount = 0;

        suggestionCards.forEach(function (card) {
            const destinationName = normalizeText(
                card.dataset.destinationName
            );

            const destinationDescription = normalizeText(
                card.dataset.destinationDescription
            );

            const matchesSearch =
                searchTerm === "" ||
                destinationName.includes(searchTerm) ||
                destinationDescription.includes(searchTerm);

            if (matchesSearch) {
                showElement(card);
                visibleCount += 1;
            } else {
                hideElement(card);
            }
        });

        if (emptyState) {
            if (visibleCount === 0) {
                showElement(emptyState);
            } else {
                hideElement(emptyState);
            }
        }

        showSuggestions();
    }

    async function saveDestination(destinationName) {
        const response = await fetch(
            "/api/trip/destination",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    destination: destinationName,
                }),
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(
                result.message ||
                "Destination could not be saved."
            );
        }

        return result;
    }

    async function selectDestination(destinationName) {
        const cleanDestinationName =
            String(destinationName || "").trim();

        if (!cleanDestinationName) {
            return;
        }

        searchInput.value = cleanDestinationName;

        if (selectedName) {
            selectedName.textContent =
                cleanDestinationName;
        }

        showElement(selectedPanel);
        hideSuggestions();

        console.log(
            "Saving destination:",
            cleanDestinationName
        );

        try {
            await saveDestination(
                cleanDestinationName
            );

            console.log(
                "Destination saved successfully:",
                cleanDestinationName
            );

            window.location.href = "/map";
        } catch (error) {
            console.error(
                "Destination save failed:",
                error
            );

            alert(
                "We could not save your destination. " +
                "Please try again."
            );
        }
    }

    function clearDestination() {
        searchInput.value = "";

        hideElement(selectedPanel);

        suggestionCards.forEach(function (card) {
            showElement(card);
        });

        hideElement(emptyState);
        showSuggestions();

        searchInput.focus();

        console.log("Destination selection cleared.");
    }

    searchInput.addEventListener(
        "focus",
        function () {
            filterDestinations();
        }
    );

    searchInput.addEventListener(
        "input",
        function () {
            hideElement(selectedPanel);
            filterDestinations();
        }
    );

    searchForm.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            const enteredDestination =
                searchInput.value.trim();

            if (!enteredDestination) {
                searchInput.focus();
                showSuggestions();
                return;
            }

            const firstVisibleCard =
                suggestionCards.find(function (card) {
                    return !card.hidden;
                });

            if (firstVisibleCard) {
                selectDestination(
                    firstVisibleCard.dataset.destinationName
                );
                return;
            }

            selectDestination(enteredDestination);
        }
    );

    suggestionCards.forEach(function (card) {
        card.addEventListener(
            "click",
            function () {
                selectDestination(
                    card.dataset.destinationName
                );
            }
        );
    });

    if (clearButton) {
        clearButton.addEventListener(
            "click",
            function () {
                clearDestination();
            }
        );
    }

    recentPlaceCards.forEach(function (card) {
        card.addEventListener(
            "click",
            function () {
                selectDestination(
                    card.dataset.recentDestination
                );
            }
        );
    });

    hideSuggestions();
    hideElement(selectedPanel);
    hideElement(emptyState);

    console.log(
        "HABESHAGO destination interactions initialized."
    );
});