"use strict";

document.addEventListener(
    "DOMContentLoaded",
    function () {
        console.log(
            "HABESHAGO Booking Summary initialized."
        );

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

        function setFeedback(
            message,
            isSuccess
        ) {
            if (!feedback) {
                return;
            }

            feedback.textContent = message;

            feedback.classList.toggle(
                "booking-confirmation-success",
                Boolean(isSuccess)
            );
        }

        function getTelegramInitData() {
            const telegram = window.Telegram;

            if (
                !telegram ||
                !telegram.WebApp
            ) {
                throw new Error(
                    "Telegram Mini App is unavailable. " +
                    "Please open HABESHAGO from Telegram."
                );
            }

            const initData =
                telegram.WebApp.initData;

            if (
                typeof initData !== "string" ||
                !initData.trim()
            ) {
                throw new Error(
                    "Telegram authentication data is " +
                    "unavailable. Please reopen HABESHAGO " +
                    "from Telegram."
                );
            }

            return initData;
        }

        async function sendPostRequest(
            url,
            options = {}
        ) {
            const headers = {
                "Content-Type": "application/json",
            };

            if (options.telegramInitData) {
                headers["X-Telegram-Init-Data"] =
                    options.telegramInitData;
            }

            const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({}),
                }
            );

            let result;

            try {
                result = await response.json();
            } catch (error) {
                throw new Error(
                    "The server returned an invalid response."
                );
            }

            if (
                !response.ok ||
                !result.success
            ) {
                throw new Error(
                    result.error ||
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

            setFeedback(
                "",
                false
            );

            try {
                /*
                 * Authentication is required before
                 * canonical dispatch.
                 *
                 * Reading Telegram initData here does
                 * not establish passenger identity.
                 * The HABESHAGO server validates the
                 * signed credential.
                 */
                const telegramInitData =
                    getTelegramInitData();

                const confirmationResult =
                    await sendPostRequest(
                        "/api/trip/confirm"
                    );

                console.log(
                    "Booking confirmed:",
                    confirmationResult.trip
                );

                confirmButton.textContent =
                    "Preparing Ride Offer...";

                setFeedback(
                    "Booking confirmed. Preparing your " +
                    "ride request...",
                    true
                );

                const dispatchResult =
                    await sendPostRequest(
                        "/api/trip/dispatch",
                        {
                            telegramInitData:
                                telegramInitData,
                        }
                    );

                console.log(
                    "Canonical Ride Offer created:",
                    dispatchResult
                );

                if (
                    dispatchResult.status !==
                    "offer_pending"
                ) {
                    throw new Error(
                        "The ride request entered an " +
                        "unexpected lifecycle state."
                    );
                }

                confirmButton.textContent =
                    "Ride Offer Sent";

                setFeedback(
                    "Your ride offer has been sent to " +
                    "the selected driver. Waiting for " +
                    "driver acceptance...",
                    true
                );

                /*
                 * Do NOT redirect to driver assignment.
                 *
                 * A pending Ride Offer is not yet an
                 * accepted canonical Ride.
                 *
                 * Driver assignment becomes valid only
                 * after canonical offer acceptance and
                 * Ride creation.
                 */
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
    }
);