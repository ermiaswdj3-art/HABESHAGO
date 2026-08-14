"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log(
        "HABESHAGO canonical Active Trip synchronization initialized."
    );

    const statusElement = document.querySelector(
        "[data-active-trip-status]"
    );

    const progressFill = document.querySelector(
        "[data-active-trip-progress-fill]"
    );

    const progressText = document.querySelector(
        "[data-active-trip-progress-text]"
    );

    const messageTitle = document.querySelector(
        "[data-active-trip-message-title]"
    );

    const messageText = document.querySelector(
        "[data-active-trip-message-text]"
    );

    const completionCard = document.querySelector(
        "[data-trip-completion-card]"
    );

    const feedback = document.querySelector(
        "[data-active-trip-feedback]"
    );

    const SYNCHRONIZATION_INTERVAL_MS = 3000;

    let synchronizationInterval = null;
    let synchronizationInFlight = false;
    let tripFinished = false;

    function getTelegramInitData() {
        if (
            window.Telegram
            && window.Telegram.WebApp
            && window.Telegram.WebApp.initData
        ) {
            return window.Telegram.WebApp.initData;
        }

        return "";
    }

    function formatStatus(value) {
        return String(value || "")
            .replaceAll("_", " ")
            .replace(/\b\w/g, function (character) {
                return character.toUpperCase();
            });
    }

    function showElement(element) {
        if (!element) {
            return;
        }

        element.hidden = false;
        element.classList.remove("is-hidden");
    }

    function stopSynchronization() {
        if (synchronizationInterval !== null) {
            window.clearInterval(
                synchronizationInterval
            );

            synchronizationInterval = null;
        }
    }

    async function synchronizeCanonicalTrip() {
        if (
            tripFinished
            || synchronizationInFlight
        ) {
            return;
        }

        synchronizationInFlight = true;

        try {
            const initData = getTelegramInitData();

            if (!initData) {
                throw new Error(
                    "Telegram Mini App authentication data is required."
                );
            }

            const response = await fetch(
                "/api/trip/synchronize",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Telegram-Init-Data": initData,
                    },
                    body: JSON.stringify({}),
                }
            );

            const result = await response.json();

            if (
                !response.ok
                || !result.success
            ) {
                throw new Error(
                    result.error
                    || result.message
                    || "Trip synchronization failed."
                );
            }

            updatePassengerPresentation(
                result.trip
            );

        } catch (error) {
            console.error(
                "Canonical trip synchronization failed:",
                error
            );

            if (feedback) {
                feedback.textContent =
                    error.message
                    || "Live trip status is temporarily unavailable.";
            }

        } finally {
            synchronizationInFlight = false;
        }
    }

    function updatePassengerPresentation(trip) {
        const canonicalState = String(
            trip.canonical_state || ""
        ).toUpperCase();

        const bookingStatus = String(
            trip.booking_status || ""
        ).toLowerCase();

        if (statusElement) {
            statusElement.textContent = formatStatus(
                bookingStatus
                || canonicalState
            );
        }

        if (
            canonicalState === "TRIP_COMPLETED"
            || bookingStatus === "trip_completed"
        ) {
            showTripCompletion(trip);
            return;
        }

        if (
            canonicalState === "TRIP_STARTED"
            || bookingStatus === "trip_started"
            || bookingStatus === "trip_in_progress"
        ) {
            showTripInProgress();
            return;
        }

        if (
            canonicalState === "DRIVER_ARRIVED"
            || bookingStatus === "driver_arrived"
        ) {
            showDriverArrived();
            return;
        }

        if (
            canonicalState === "DRIVER_ARRIVING"
            || bookingStatus === "driver_arriving"
        ) {
            showDriverEnRoute();
            return;
        }

        if (feedback) {
            feedback.textContent =
                "Waiting for the latest canonical Ride state.";
        }
    }

    function showDriverEnRoute() {
        if (messageTitle) {
            messageTitle.textContent =
                "Your driver is on the way.";
        }

        if (messageText) {
            messageText.textContent =
                "HABESHAGO is receiving the driver's live Ride state.";
        }

        if (feedback) {
            feedback.textContent =
                "Driver en route.";
        }
    }

    function showDriverArrived() {
        if (messageTitle) {
            messageTitle.textContent =
                "Your driver has arrived.";
        }

        if (messageText) {
            messageText.textContent =
                "Meet your driver at the pickup point.";
        }

        if (feedback) {
            feedback.textContent =
                "Driver arrived.";
        }
    }

    function showTripInProgress() {
        if (progressText) {
            progressText.textContent = "Live";
        }

        if (messageTitle) {
            messageTitle.textContent =
                "Your trip is underway.";
        }

        if (messageText) {
            messageText.textContent =
                "Your driver is taking you toward your destination.";
        }

        if (feedback) {
            feedback.textContent =
                "Canonical Ride is in progress.";
        }
    }

    function showTripCompletion(trip) {
        if (tripFinished) {
            return;
        }

        tripFinished = true;

        stopSynchronization();

        if (statusElement) {
            statusElement.textContent =
                "Trip Completed";
        }

        if (progressFill) {
            progressFill.style.width = "100%";
        }

        if (progressText) {
            progressText.textContent = "100%";
        }

        if (messageTitle) {
            messageTitle.textContent =
                "You have arrived safely.";
        }

        if (messageText) {
            messageText.textContent =
                "Thank you for riding with HABESHAGO.";
        }

        if (feedback) {
            feedback.textContent =
                "Canonical Ride completed successfully.";
        }

        showElement(completionCard);

        console.log(
            "Canonical Ride completed:",
            trip
        );

        window.setTimeout(
            function () {
                window.location.href = "/payment";
            },
            2000
        );
    }

    window.addEventListener(
        "pagehide",
        stopSynchronization
    );

    synchronizeCanonicalTrip();

    synchronizationInterval = window.setInterval(
        synchronizeCanonicalTrip,
        SYNCHRONIZATION_INTERVAL_MS
    );
});
