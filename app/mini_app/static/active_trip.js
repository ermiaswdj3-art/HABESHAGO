"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO Active Trip initialized.");

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

    let tripFinished = false;
    let progressInterval = null;

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

    async function sendPostRequest(
        url,
        payload
    ) {
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload || {}),
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(
                result.message ||
                "The request could not be completed."
            );
        }

        return result;
    }

    function updateProgressInterface(trip) {
        const progress = Number(
            trip.trip_progress_percent || 0
        );

        if (statusElement) {
            statusElement.textContent = formatStatus(
                trip.booking_status
            );
        }

        if (progressFill) {
            progressFill.style.width =
                `${progress}%`;
        }

        if (progressText) {
            progressText.textContent =
                `${progress}%`;
        }

        if (
            trip.booking_status ===
            "arriving_destination"
        ) {
            if (messageTitle) {
                messageTitle.textContent =
                    "You have reached the destination.";
            }

            if (messageText) {
                messageText.textContent =
                    "Completing your HABESHAGO trip...";
            }

            if (feedback) {
                feedback.textContent =
                    "Destination reached.";
            }
        } else {
            if (messageTitle) {
                messageTitle.textContent =
                    "Your trip is underway.";
            }

            if (messageText) {
                messageText.textContent =
                    `${progress}% of the journey completed.`;
            }

            if (feedback) {
                feedback.textContent =
                    "Trip progress updated.";
            }
        }
    }

    function showTripCompletion(trip) {
        tripFinished = true;

        if (progressInterval !== null) {
            window.clearInterval(
                progressInterval
            );
        }

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
                "Trip completed successfully.";
        }

        showElement(completionCard);

        window.setTimeout(
            function () {
                window.location.href = "/payment";
            },
            2000
        );

        console.log(
            "Trip completed:",
            trip
        );
    }

    async function completeTrip() {
        try {
            const result = await sendPostRequest(
                "/api/trip/complete",
                {}
            );

            showTripCompletion(result.trip);
        } catch (error) {
            console.error(
                "Trip completion failed:",
                error
            );

            if (feedback) {
                feedback.textContent =
                    error.message ||
                    "The trip could not be completed.";
            }

            tripFinished = true;
        }
    }

    async function advanceTrip() {
        if (tripFinished) {
            return;
        }

        try {
            const result = await sendPostRequest(
                "/api/trip/progress",
                {
                    progress_increment: 20,
                }
            );

            const trip = result.trip;

            updateProgressInterface(trip);

            console.log(
                "Trip progress:",
                trip
            );

            if (
                trip.booking_status ===
                "arriving_destination"
                && trip.destination_reached
            ) {
                await completeTrip();
            }
        } catch (error) {
            console.error(
                "Trip progress failed:",
                error
            );

            if (feedback) {
                feedback.textContent =
                    error.message ||
                    "Trip progress is temporarily unavailable.";
            }

            tripFinished = true;

            if (progressInterval !== null) {
                window.clearInterval(
                    progressInterval
                );
            }
        }
    }

    progressInterval = window.setInterval(
        function () {
            advanceTrip();
        },
        3000
    );
});