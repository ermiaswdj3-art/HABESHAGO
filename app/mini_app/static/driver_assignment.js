"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO live driver tracking initialized.");

    const arrivalText = document.querySelector(
        "[data-driver-arrival-text]"
    );

    const tripStatus = document.querySelector(
        "[data-driver-trip-status]"
    );

    const progressTitle = document.querySelector(
        "[data-driver-progress-title]"
    );

    const progressMessage = document.querySelector(
        "[data-driver-progress-message]"
    );

    const feedback = document.querySelector(
        "[data-driver-tracking-feedback]"
    );

    let trackingStopped = false;

    function formatStatus(value) {
        return String(value || "")
            .replaceAll("_", " ")
            .replace(/\b\w/g, function (character) {
                return character.toUpperCase();
            });
    }

    function updateTrackingInterface(tracking) {
        if (tripStatus) {
            tripStatus.textContent = formatStatus(
                tracking.booking_status
            );
        }

        if (tracking.has_arrived) {
            if (arrivalText) {
                arrivalText.textContent =
                    "Driver has arrived";
            }

            if (progressTitle) {
                progressTitle.textContent =
                    "Your driver has arrived at the pickup.";
            }

            if (progressMessage) {
                progressMessage.textContent =
                    "Please confirm the vehicle and plate number before boarding.";
            }

            if (feedback) {
                feedback.textContent =
                    "Live tracking completed.";
            }

            trackingStopped = true;
            return;
        }

        const eta = Number(tracking.eta_minutes);

        if (arrivalText) {
            arrivalText.textContent =
                `Arriving in ${eta} ` +
                `minute${eta === 1 ? "" : "s"}`;
        }

        if (progressTitle) {
            progressTitle.textContent =
                "Your driver is heading to the pickup.";
        }

        if (progressMessage) {
            progressMessage.textContent =
                `${tracking.remaining_distance_km} km remaining.`;
        }

        if (feedback) {
            feedback.textContent =
                "Live location updated.";
        }
    }

    async function requestTrackingUpdate() {
        if (trackingStopped) {
            return;
        }

        try {
            const response = await fetch(
                "/api/trip/tracking/update",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({}),
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "Tracking could not be updated."
                );
            }

            updateTrackingInterface(result.tracking);

            console.log(
                "Live tracking update:",
                result.tracking
            );
        } catch (error) {
            console.error(
                "Live tracking failed:",
                error
            );

            if (feedback) {
                feedback.textContent =
                    error.message ||
                    "Live tracking is temporarily unavailable.";
            }

            trackingStopped = true;
        }
    }

    requestTrackingUpdate();

    const trackingInterval = window.setInterval(
        function () {
            if (trackingStopped) {
                window.clearInterval(trackingInterval);
                return;
            }

            requestTrackingUpdate();
        },
        3000
    );
});