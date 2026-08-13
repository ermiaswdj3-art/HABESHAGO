"use strict";

/**
 * HABESHAGO Passenger Home
 *
 * Responsibilities:
 * - Load the authenticated Telegram passenger greeting.
 * - Search destinations through the shared HABESHAGO
 *   destination-search platform.
 * - Require a resolved geographic destination before
 *   saving it to Trip Context.
 * - Preserve quick suggestions and recent places by
 *   resolving them through the same canonical search.
 */

document.addEventListener(
    "DOMContentLoaded",
    function () {
        console.log(
            "HABESHAGO home.js loaded successfully."
        );

        const greetingText =
            document.querySelector(
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
                            "X-Telegram-Init-Data":
                                initData,
                        },
                    }
                );

                const result =
                    await response.json();

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

                greetingText.textContent =
                    result.greeting;

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

        const searchForm =
            document.querySelector(
                ".destination-search"
            );

        const searchInput =
            document.querySelector(
                "#destination-search-input"
            );

        const suggestionSection =
            document.querySelector(
                ".destination-suggestions"
            );

        const searchResultsContainer =
            document.querySelector(
                "[data-destination-search-results]"
            );

        const staticSuggestionsContainer =
            document.querySelector(
                "[data-static-destination-suggestions]"
            );

        const staticSuggestionCards =
            Array.from(
                document.querySelectorAll(
                    ".destination-suggestion-card"
                )
            );

        const emptyState =
            document.querySelector(
                "[data-destination-empty-state]"
            );

        const selectedPanel =
            document.querySelector(
                "[data-selected-destination]"
            );

        const selectedName =
            document.querySelector(
                "[data-selected-destination-name]"
            );

        const clearButton =
            document.querySelector(
                "[data-clear-destination]"
            );

        const recentPlaceCards =
            Array.from(
                document.querySelectorAll(
                    "[data-recent-destination]"
                )
            );

        if (
            !searchForm ||
            !searchInput ||
            !suggestionSection ||
            !searchResultsContainer ||
            !staticSuggestionsContainer
        ) {
            console.error(
                "Destination search UI is incomplete."
            );
            return;
        }

        let searchTimer = null;
        let searchSequence = 0;
        let currentSearchResults = [];

        function showElement(element) {
            if (!element) {
                return;
            }

            element.hidden = false;
            element.classList.remove(
                "is-hidden"
            );
        }

        function hideElement(element) {
            if (!element) {
                return;
            }

            element.hidden = true;
            element.classList.add(
                "is-hidden"
            );
        }

        function clearDynamicResults() {
            currentSearchResults = [];
            searchResultsContainer.replaceChildren();
            hideElement(
                searchResultsContainer
            );
        }

        function showStaticSuggestions() {
            clearDynamicResults();

            showElement(
                staticSuggestionsContainer
            );

            hideElement(emptyState);
            showElement(suggestionSection);
        }

        function showEmptyState() {
            clearDynamicResults();

            hideElement(
                staticSuggestionsContainer
            );

            showElement(emptyState);
            showElement(suggestionSection);
        }

        function createDestinationResultCard(
            destination
        ) {
            const button =
                document.createElement(
                    "button"
                );

            button.type = "button";
            button.className =
                "destination-suggestion-card";

            const icon =
                document.createElement(
                    "div"
                );

            icon.className =
                "destination-suggestion-icon";
            icon.textContent = "📍";

            const content =
                document.createElement(
                    "div"
                );

            content.className =
                "destination-suggestion-content";

            const heading =
                document.createElement(
                    "h3"
                );

            heading.textContent =
                destination.short_name ||
                destination.name ||
                "Destination";

            const description =
                document.createElement(
                    "p"
                );

            description.textContent =
                destination.full_name ||
                destination.city ||
                "Addis Ababa";

            content.append(
                heading,
                description
            );

            const arrow =
                document.createElement(
                    "div"
                );

            arrow.className =
                "destination-suggestion-arrow";

            arrow.setAttribute(
                "aria-hidden",
                "true"
            );

            arrow.textContent = "→";

            button.append(
                icon,
                content,
                arrow
            );

            button.addEventListener(
                "click",
                function () {
                    selectResolvedDestination(
                        destination
                    );
                }
            );

            return button;
        }

        function renderSearchResults(
            destinations
        ) {
            currentSearchResults =
                destinations;

            searchResultsContainer.replaceChildren();

            hideElement(
                staticSuggestionsContainer
            );

            if (
                destinations.length === 0
            ) {
                showEmptyState();
                return;
            }

            destinations.forEach(
                function (destination) {
                    searchResultsContainer.appendChild(
                        createDestinationResultCard(
                            destination
                        )
                    );
                }
            );

            hideElement(emptyState);
            showElement(
                searchResultsContainer
            );
            showElement(
                suggestionSection
            );
        }

        async function searchDestinations(
            query
        ) {
            const cleanQuery =
                String(query || "").trim();

            if (
                cleanQuery.length < 2
            ) {
                showStaticSuggestions();
                return [];
            }

            const requestSequence =
                ++searchSequence;

            const parameters =
                new URLSearchParams({
                    q: cleanQuery,
                });

            try {
                const response = await fetch(
                    `/api/destinations/search?${parameters}`
                );

                const result =
                    await response.json();

                if (
                    requestSequence !==
                    searchSequence
                ) {
                    return [];
                }

                if (
                    !response.ok ||
                    !result.success
                ) {
                    throw new Error(
                        result.message ||
                        "Destination search failed."
                    );
                }

                const destinations =
                    Array.isArray(
                        result.destinations
                    )
                        ? result.destinations
                        : [];

                renderSearchResults(
                    destinations
                );

                return destinations;
            } catch (error) {
                console.error(
                    "Destination search failed:",
                    error
                );

                if (
                    requestSequence ===
                    searchSequence
                ) {
                    showEmptyState();
                }

                return [];
            }
        }

        async function saveDestination(
            destination
        ) {
            const latitude =
                Number(
                    destination.latitude
                );

            const longitude =
                Number(
                    destination.longitude
                );

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {
                throw new Error(
                    "Destination coordinates are required."
                );
            }

            const destinationName =
                String(
                    destination.short_name ||
                    destination.name ||
                    ""
                ).trim();

            if (!destinationName) {
                throw new Error(
                    "Destination name is required."
                );
            }

            const response = await fetch(
                "/api/trip/destination",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        destination:
                            destinationName,
                        latitude:
                            latitude,
                        longitude:
                            longitude,
                    }),
                }
            );

            const result =
                await response.json();

            if (
                !response.ok ||
                !result.success
            ) {
                throw new Error(
                    result.message ||
                    "Destination could not be saved."
                );
            }

            return result;
        }

        async function selectResolvedDestination(
            destination
        ) {
            const destinationName =
                String(
                    destination.short_name ||
                    destination.name ||
                    ""
                ).trim();

            if (!destinationName) {
                return;
            }

            searchInput.value =
                destinationName;

            if (selectedName) {
                selectedName.textContent =
                    destinationName;
            }

            showElement(selectedPanel);
            hideElement(
                suggestionSection
            );

            console.log(
                "Saving resolved destination:",
                {
                    name:
                        destinationName,
                    latitude:
                        destination.latitude,
                    longitude:
                        destination.longitude,
                }
            );

            try {
                await saveDestination(
                    destination
                );

                console.log(
                    "Resolved destination saved successfully:",
                    destinationName
                );

                window.location.href =
                    "/map";
            } catch (error) {
                console.error(
                    "Destination save failed:",
                    error
                );

                alert(
                    error.message ||
                    "We could not save your destination. " +
                    "Please try again."
                );

                hideElement(
                    selectedPanel
                );

                showElement(
                    suggestionSection
                );
            }
        }

        async function resolveAndSelectDestination(
            destinationName
        ) {
            const cleanName =
                String(
                    destinationName || ""
                ).trim();

            if (!cleanName) {
                return;
            }

            searchInput.value =
                cleanName;

            const destinations =
                await searchDestinations(
                    cleanName
                );

            if (
                destinations.length === 0
            ) {
                return;
            }

            await selectResolvedDestination(
                destinations[0]
            );
        }

        function scheduleDestinationSearch() {
            if (searchTimer) {
                window.clearTimeout(
                    searchTimer
                );
            }

            const query =
                searchInput.value.trim();

            hideElement(
                selectedPanel
            );

            if (
                query.length < 2
            ) {
                ++searchSequence;
                showStaticSuggestions();
                return;
            }

            hideElement(
                staticSuggestionsContainer
            );

            hideElement(emptyState);
            showElement(
                suggestionSection
            );

            searchTimer =
                window.setTimeout(
                    function () {
                        searchDestinations(
                            query
                        );
                    },
                    350
                );
        }

        function clearDestination() {
            if (searchTimer) {
                window.clearTimeout(
                    searchTimer
                );
            }

            ++searchSequence;

            searchInput.value = "";

            hideElement(
                selectedPanel
            );

            showStaticSuggestions();

            searchInput.focus();

            console.log(
                "Destination selection cleared."
            );
        }

        searchInput.addEventListener(
            "focus",
            function () {
                if (
                    searchInput.value
                        .trim()
                        .length < 2
                ) {
                    showStaticSuggestions();
                } else {
                    scheduleDestinationSearch();
                }
            }
        );

        searchInput.addEventListener(
            "input",
            scheduleDestinationSearch
        );

        searchForm.addEventListener(
            "submit",
            async function (event) {
                event.preventDefault();

                const enteredDestination =
                    searchInput.value.trim();

                if (
                    enteredDestination.length < 2
                ) {
                    searchInput.focus();
                    showStaticSuggestions();
                    return;
                }

                if (
                    currentSearchResults.length > 0
                ) {
                    await selectResolvedDestination(
                        currentSearchResults[0]
                    );
                    return;
                }

                await resolveAndSelectDestination(
                    enteredDestination
                );
            }
        );

        staticSuggestionCards.forEach(
            function (card) {
                card.addEventListener(
                    "click",
                    function () {
                        resolveAndSelectDestination(
                            card.dataset.destinationName
                        );
                    }
                );
            }
        );

        recentPlaceCards.forEach(
            function (card) {
                card.addEventListener(
                    "click",
                    function () {
                        resolveAndSelectDestination(
                            card.dataset.recentDestination
                        );
                    }
                );
            }
        );

        if (clearButton) {
            clearButton.addEventListener(
                "click",
                clearDestination
            );
        }

        hideElement(
            suggestionSection
        );

        hideElement(
            selectedPanel
        );

        hideElement(
            emptyState
        );

        clearDynamicResults();

        console.log(
            "HABESHAGO canonical destination search initialized."
        );
    }
);
