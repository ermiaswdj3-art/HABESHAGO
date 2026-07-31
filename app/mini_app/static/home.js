"use strict";

/**
 * HABESHAGO Interactive Destination Search
 *
 * Features:
 * - Shows destination suggestions when search receives focus
 * - Filters destinations while typing
 * - Selects a suggestion
 * - Displays a selected-destination panel
 * - Clears the current selection
 * - Supports Recent Places
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO home.js loaded successfully.");

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
        console.error("Destination suggestions section was not found.");
        return;
    }

    if (suggestionCards.length === 0) {
        console.error("No destination suggestion cards were found.");
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

    function selectDestination(destinationName) {
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
            "Destination selected:",
            cleanDestinationName
        );
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