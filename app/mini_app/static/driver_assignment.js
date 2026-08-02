"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log(
        "HABESHAGO live tracking and pickup verification initialized."
    );

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

    const trackingFeedback = document.querySelector(
        "[data-driver-tracking-feedback]"
    );

    const verificationPanel = document.querySelector(
        "[data-pickup-verification-panel]"
    );

    const pinDisplay = document.querySelector(
        "[data-pickup-pin-display]"
    );

    const verificationForm = document.querySelector(
        "[data-pickup-verification-form]"
    );

    const pinInput = document.querySelector(
        "[data-pickup-pin-input]"
    );

    const verifyButton = document.querySelector(
        "[data-verify-pickup]"
    );

    const verificationFeedback = document.querySelector(
        "[data-pickup-verification-feedback]"
    );

    const verificationSuccess = document.querySelector(
        "[data-pickup-verification-success]"
    );

    let trackingStopped = false;
    let verificationStarted = false;
    let trackingInterval = null;

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

    function hideElement(element) {
        if (!element) {
            return;
        }

        element.hidden = true;
        element.classList.add("is-hidden");
    }

    function formatPickupPin(pin) {
        return String(pin || "")
            .split("")
            .join(" ");
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

    async function startPickupVerification() {
        if (verificationStarted) {
            return;
        }

        verificationStarted = true;

        try {
            const result = await sendPostRequest(
                "/api/trip/pickup-verification/start",
                {}
            );

            const verification = result.verification;

            if (pinDisplay) {
                pinDisplay.textContent = formatPickupPin(
                    verification.pickup_pin
                );
            }

            if (tripStatus) {
                tripStatus.textContent = formatStatus(
                    verification.booking_status
                );
            }

            if (verificationFeedback) {
                verificationFeedback.textContent =
                    "Pickup PIN generated successfully.";
            }

            showElement(verificationPanel);

            if (pinInput) {
                pinInput.focus();
            }

            console.log(
                "Pickup verification started:",
                verification
            );
        } catch (error) {
            console.error(
                "Pickup verification could not start:",
                error
            );

            verificationStarted = false;

            if (verificationFeedback) {
                verificationFeedback.textContent =
                    error.message ||
                    "Pickup verification is unavailable.";
            }

            showElement(verificationPanel);
        }
    }

    function handleDriverArrival() {
        trackingStopped = true;

        if (trackingInterval !== null) {
            window.clearInterval(trackingInterval);
        }

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
                "Confirm the driver, vehicle, and plate before sharing your PIN.";
        }

        if (trackingFeedback) {
            trackingFeedback.textContent =
                "Live tracking completed.";
        }

        startPickupVerification();
    }

    function updateTrackingInterface(tracking) {
        if (tripStatus) {
            tripStatus.textContent = formatStatus(
                tracking.booking_status
            );
        }

        if (tracking.has_arrived) {
            handleDriverArrival();
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

        if (trackingFeedback) {
            trackingFeedback.textContent =
                "Live location updated.";
        }
    }

    async function requestTrackingUpdate() {
        if (trackingStopped) {
            return;
        }

        try {
            const result = await sendPostRequest(
                "/api/trip/tracking/update",
                {}
            );

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

            if (trackingFeedback) {
                trackingFeedback.textContent =
                    error.message ||
                    "Live tracking is temporarily unavailable.";
            }

            trackingStopped = true;

            if (trackingInterval !== null) {
                window.clearInterval(trackingInterval);
            }
        }
    }

    async function verifyPassengerPickup(event) {
        event.preventDefault();

        const submittedPin = String(
            pinInput ? pinInput.value : ""
        ).trim();

        if (!/^\d{4}$/.test(submittedPin)) {
            if (verificationFeedback) {
                verificationFeedback.textContent =
                    "Enter the complete four-digit pickup PIN.";
            }

            if (pinInput) {
                pinInput.focus();
            }

            return;
        }

        if (verifyButton) {
            verifyButton.disabled = true;
            verifyButton.textContent =
                "Verifying...";
        }

        if (verificationFeedback) {
            verificationFeedback.textContent =
                "Checking pickup PIN...";
        }

        try {
            const result = await sendPostRequest(
                "/api/trip/pickup-verification/verify",
                {
                    pickup_pin: submittedPin,
                }
            );

            const verification = result.verification;

            if (tripStatus) {
                tripStatus.textContent = formatStatus(
                    verification.booking_status
                );
            }

            if (arrivalText) {
                arrivalText.textContent =
                    "Passenger verified";
            }

            if (progressTitle) {
                progressTitle.textContent =
                    "Secure pickup verification complete.";
            }

            if (progressMessage) {
                progressMessage.textContent =
                    "The driver and passenger are ready to start the trip.";
            }

            hideElement(verificationPanel);
            showElement(verificationSuccess);

            if (trackingFeedback) {
                trackingFeedback.textContent =
                    "Ready to start trip.";
            }

            console.log(
                "Passenger pickup verified:",
                verification
            );
        } catch (error) {
            console.error(
                "Pickup PIN verification failed:",
                error
            );

            if (verificationFeedback) {
                verificationFeedback.textContent =
                    error.message ||
                    "The pickup PIN could not be verified.";
            }

            if (verifyButton) {
                verifyButton.disabled = false;
                verifyButton.textContent =
                    "Verify Passenger";
            }

            if (pinInput) {
                pinInput.select();
                pinInput.focus();
            }
        }
    }

    if (verificationForm) {
        verificationForm.addEventListener(
            "submit",
            verifyPassengerPickup
        );
    }

    requestTrackingUpdate();

    trackingInterval = window.setInterval(
        function () {
            if (trackingStopped) {
                window.clearInterval(
                    trackingInterval
                );

                return;
            }

            requestTrackingUpdate();
        },
        3000
    );
});