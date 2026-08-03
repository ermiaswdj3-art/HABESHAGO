"use strict";

document.addEventListener("DOMContentLoaded", function () {
    console.log("HABESHAGO Payment Platform initialized.");

    const methodButtons = Array.from(
        document.querySelectorAll(
            "[data-payment-method]"
        )
    );

    const processButton = document.querySelector(
        "[data-process-payment]"
    );

    const statusElement = document.querySelector(
        "[data-payment-status]"
    );

    const finalFareElement = document.querySelector(
        "[data-final-fare]"
    );

    const breakdownList = document.querySelector(
        "[data-fare-breakdown-list]"
    );

    const successCard = document.querySelector(
        "[data-payment-success]"
    );

    const transactionId = document.querySelector(
        "[data-transaction-id]"
    );

    const receiptId = document.querySelector(
        "[data-receipt-id]"
    );

    const feedback = document.querySelector(
        "[data-payment-feedback]"
    );

    let selectedMethod = null;

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

    function renderFareBreakdown(fare) {
        const breakdown = fare.breakdown;

        const rows = [
            ["Base fare", breakdown.base_fare],
            ["Distance fare", breakdown.distance_fare],
            ["Time fare", breakdown.time_fare],
            ["Waiting charge", breakdown.waiting_charge],
            ["Airport fee", breakdown.airport_fee],
            ["Toll fee", breakdown.toll_fee],
            ["Discount", -breakdown.discount],
        ];

        if (breakdownList) {
            breakdownList.innerHTML = "";

            rows.forEach(function (row) {
                const item = document.createElement("div");
                item.className = "fare-breakdown-row";

                const label = document.createElement("span");
                label.textContent = row[0];

                const value = document.createElement("strong");
                value.textContent =
                    `${Number(row[1]).toFixed(2)} ETB`;

                item.append(label, value);
                breakdownList.appendChild(item);
            });
        }

        if (finalFareElement) {
            finalFareElement.textContent =
                `${Number(
                    breakdown.final_fare
                ).toFixed(2)} ${fare.currency}`;
        }
    }

    async function initializeFare() {
        try {
            const result = await sendPostRequest(
                "/api/trip/fare/finalize",
                {
                    distance_km: 4,
                    duration_minutes: 12,
                    waiting_minutes: 0,
                    airport_fee: 0,
                    toll_fee: 0,
                    discount: 0,
                }
            );

            renderFareBreakdown(result.fare);

            if (statusElement) {
                statusElement.textContent =
                    formatStatus(
                        result.payment_status
                    );
            }

            if (feedback) {
                feedback.textContent =
                    "Final fare calculated.";
            }
        } catch (error) {
            if (feedback) {
                feedback.textContent =
                    error.message;
            }
        }
    }

    async function selectMethod(button) {
        const method =
            button.dataset.paymentMethod;
        const title =
            button.dataset.paymentTitle;

        try {
            const result = await sendPostRequest(
                "/api/trip/payment/method",
                {
                    payment_method: method,
                }
            );

            selectedMethod = method;

            methodButtons.forEach(function (
                methodButton
            ) {
                methodButton.classList.remove(
                    "is-selected"
                );
            });

            button.classList.add("is-selected");

            if (processButton) {
                processButton.disabled = false;
                processButton.textContent =
                    `Pay with ${title}`;
            }

            if (statusElement) {
                statusElement.textContent =
                    formatStatus(
                        result.payment.payment_status
                    );
            }

            if (feedback) {
                feedback.textContent =
                    `${title} selected.`;
            }
        } catch (error) {
            if (feedback) {
                feedback.textContent =
                    error.message;
            }
        }
    }

    async function completePayment() {
        if (!selectedMethod || !processButton) {
            return;
        }

        processButton.disabled = true;
        processButton.textContent =
            "Processing Payment...";

        try {
            const result = await sendPostRequest(
                "/api/trip/payment/process",
                {}
            );

            const payment = result.payment;

            if (statusElement) {
                statusElement.textContent =
                    formatStatus(
                        payment.payment_status
                    );
            }

            if (transactionId) {
                transactionId.textContent =
                    payment.payment_transaction_id;
            }

            if (receiptId) {
                receiptId.textContent =
                    payment.receipt_id;
            }

            processButton.textContent =
                "Payment Completed";

            showElement(successCard);

            if (feedback) {
                feedback.textContent =
                    "Payment completed successfully.";
            }
        } catch (error) {
            processButton.disabled = false;
            processButton.textContent =
                "Complete Payment";

            if (feedback) {
                feedback.textContent =
                    error.message;
            }
        }
    }

    methodButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                selectMethod(button);
            }
        );
    });

    if (processButton) {
        processButton.addEventListener(
            "click",
            completePayment
        );
    }

    initializeFare();
});