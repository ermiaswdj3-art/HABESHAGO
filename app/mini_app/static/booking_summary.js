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

    async function sendPostRequest(url) {
        const response = await fetch(
            url,
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
                "The request could not be completed."
            );
        }

        return result;
    }

    async function confirmAndDispatchBooking() {
        confirmButton.disabled = true;
        confirmButton.textContent =
            "Confirming Booking...";

        setFeedback("", false);

        try {
            const confirmationResult =
                await sendPostRequest(
                    "/api/trip/confirm"
                );

            console.log(
                "Booking confirmed:",
                confirmationResult.trip
            );

            confirmButton.textContent =
                "Searching for Driver...";

            setFeedback(
                "Booking confirmed. Searching for " +
                "the best available driver...",
                true
            );

            const dispatchResult =
                await sendPostRequest(
                    "/api/trip/dispatch"
                );

            console.log(
                "Driver assigned:",
                dispatchResult.trip
            );

            confirmButton.textContent =
                "Driver Found";

            setFeedback(
                "Driver assigned successfully. " +
                "Opening driver details...",
                true
            );

            window.location.href =
                "/driver-assignment";
        } catch (error) {
            console.error(
                "Booking or dispatch failed:",
                error
            );

            setFeedback(
                error.message ||
                "We could not complete the booking.",
                false
            );

            confirmButton.disabled = false;
            confirmButton.textContent =
                "Confirm Booking";
        }
    }

    confirmButton.addEventListener(
        "click",
        confirmAndDispatchBooking
    );
});