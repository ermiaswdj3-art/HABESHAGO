"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO Booking Summary initialized.");

    const confirmButton = document.querySelector(
        "[data-confirm-booking]"
    );

    const feedback = document.querySelector(
        "[data-booking-confirmation-feedback]"
    );

    if (!confirmButton) {
        console.error(
            "Confirm Booking button was not found."
        );
        return;
    }

    function setFeedback(message, isSuccess) {
        if (!feedback) {
            return;
        }

        feedback.textContent = message;

        feedback.classList.toggle(
            "booking-confirmation-success",
            Boolean(isSuccess)
        );
    }

    async function confirmBooking() {
        confirmButton.disabled = true;
        confirmButton.textContent =
            "Confirming Booking...";

        setFeedback("", false);

        try {
            const response = await fetch(
                "/api/trip/confirm",
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
                    "The booking could not be confirmed."
                );
            }

            confirmButton.textContent =
                "Booking Confirmed";

            setFeedback(
                "Booking confirmed. HABESHAGO is ready " +
                "to begin driver dispatch.",
                true
            );

            console.log(
                "Booking confirmed:",
                result.trip
            );
        } catch (error) {
            console.error(
                "Booking confirmation failed:",
                error
            );

            setFeedback(
                error.message ||
                "We could not confirm your booking.",
                false
            );

            confirmButton.disabled = false;
            confirmButton.textContent =
                "Confirm Booking";
        }
    }

    confirmButton.addEventListener(
        "click",
        confirmBooking
    );
});