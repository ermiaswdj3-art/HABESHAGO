"use strict";

document.addEventListener(
    "DOMContentLoaded",
    function () {
        console.log(
            "HABESHAGO Driver Dashboard initialized."
        );

        const statusElement = document.querySelector(
            "[data-driver-offer-status]"
        );

        const offerCard = document.querySelector(
            "[data-driver-offer-card]"
        );

        const acceptButton = document.querySelector(
            "[data-accept-driver-offer]"
        );

        const rejectButton = document.querySelector(
            "[data-reject-driver-offer]"
        );

        const feedback = document.querySelector(
            "[data-driver-offer-feedback]"
        );

        const driverStatusLabel =
            document.querySelector(
                "[data-driver-status-label]"
            );

        const driverStatusBadge =
            document.querySelector(
                "[data-driver-status-badge]"
            );

        const driverOnline =
            document.querySelector(
                "[data-driver-online]"
            );

        const driverAvailable =
            document.querySelector(
                "[data-driver-available]"
            );

        const driverStatusAction =
            document.querySelector(
                "[data-driver-status-action]"
            );

        const driverStatusFeedback =
            document.querySelector(
                "[data-driver-status-feedback]"
            );

        let currentOffer = null;
        let currentDriverStatus = null;

        function getTelegramInitData() {
            if (
                !window.Telegram ||
                !window.Telegram.WebApp
            ) {
                return "";
            }

            return (
                window.Telegram.WebApp.initData ||
                ""
            );
        }

        function setText(selector, value) {
            const element = document.querySelector(
                selector
            );

            if (!element) {
                return;
            }

            element.textContent =
                value === null ||
                value === undefined ||
                value === ""
                    ? "—"
                    : String(value);
        }

        function formatNumber(value, suffix) {
            const number = Number(value);

            if (!Number.isFinite(number)) {
                return "—";
            }

            return (
                number.toFixed(2) +
                (suffix ? ` ${suffix}` : "")
            );
        }

        function setStatus(message) {
            if (statusElement) {
                statusElement.textContent = message;
            }
        }

        function setFeedback(message) {
            if (feedback) {
                feedback.textContent = message;
            }
        }

        function setDriverStatusFeedback(message) {
            if (driverStatusFeedback) {
                driverStatusFeedback.textContent =
                    message;
            }
        }

        function getDriverStatusPresentation(
            status
        ) {
            const presentations = {
                offline: {
                    label:
                        "You are currently offline",
                    action:
                        "Go Online",
                },
                available: {
                    label:
                        "You are online and available",
                    action:
                        "Go Offline",
                },
                unavailable: {
                    label:
                        "You are online but unavailable",
                    action:
                        "Go Available",
                },
            };

            return (
                presentations[status] ||
                presentations.offline
            );
        }

        function renderDriverAvailability(
            availability
        ) {
            if (!availability) {
                currentDriverStatus = null;

                setDriverStatusFeedback(
                    "Driver availability is unavailable."
                );

                if (driverStatusAction) {
                    driverStatusAction.disabled = true;
                }

                return;
            }

            const status =
                availability.status ||
                "offline";

            currentDriverStatus = status;

            const presentation =
                getDriverStatusPresentation(
                    status
                );

            if (driverStatusLabel) {
                driverStatusLabel.textContent =
                    presentation.label;
            }

            if (driverStatusBadge) {
                driverStatusBadge.textContent =
                    status
                        .replaceAll("_", " ")
                        .replace(
                            /\b\w/g,
                            function (character) {
                                return character.toUpperCase();
                            }
                        );

                driverStatusBadge.className =
                    (
                        "driver-status-badge " +
                        "driver-status-" +
                        status
                    );
            }

            if (driverOnline) {
                driverOnline.textContent =
                    availability.is_online
                        ? "Yes"
                        : "No";
            }

            if (driverAvailable) {
                driverAvailable.textContent =
                    availability.is_available
                        ? "Yes"
                        : "No";
            }

            if (driverStatusAction) {
                driverStatusAction.textContent =
                    presentation.action;

                driverStatusAction.disabled = false;
            }

            setDriverStatusFeedback(
                availability.can_receive_ride_offers
                    ? (
                        "You are eligible to receive " +
                        "canonical HABESHAGO ride offers."
                    )
                    : (
                        "Your driver status is synchronized " +
                        "with the authoritative HABESHAGO " +
                        "platform."
                    )
            );
        }

        async function fetchDriverContext() {
            const initData =
                getTelegramInitData();

            if (!initData) {
                setDriverStatusFeedback(
                    "Open the Driver Dashboard from " +
                    "Telegram to load your canonical " +
                    "driver context."
                );

                if (driverStatusAction) {
                    driverStatusAction.disabled = true;
                }

                return;
            }

            try {
                const response = await fetch(
                    "/api/driver/context",
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
                    !result.success
                ) {
                    throw new Error(
                        result.error ||
                        "Unable to load driver context."
                    );
                }

                renderDriverAvailability(
                    result.availability
                );

            } catch (error) {
                console.error(
                    "Driver context failed:",
                    error
                );

                setDriverStatusFeedback(
                    error.message ||
                    "Unable to load driver context."
                );

                if (driverStatusAction) {
                    driverStatusAction.disabled = true;
                }
            }
        }

        async function transitionDriverStatus() {
            const initData =
                getTelegramInitData();

            if (!initData) {
                setDriverStatusFeedback(
                    "Telegram authentication is required."
                );
                return;
            }

            if (!currentDriverStatus) {
                setDriverStatusFeedback(
                    "Driver status is not available."
                );
                return;
            }

            let targetStatus;

            if (
                currentDriverStatus ===
                "offline"
            ) {
                targetStatus = "available";
            } else if (
                currentDriverStatus ===
                "available"
            ) {
                targetStatus = "offline";
            } else {
                targetStatus = "available";
            }

            if (driverStatusAction) {
                driverStatusAction.disabled = true;
                driverStatusAction.textContent =
                    "Updating...";
            }

            setDriverStatusFeedback(
                "Synchronizing driver status..."
            );

            try {
                const response = await fetch(
                    "/api/driver/status",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json",
                            "X-Telegram-Init-Data":
                                initData,
                        },
                        body: JSON.stringify(
                            {
                                status:
                                    targetStatus,
                            }
                        ),
                    }
                );

                const result =
                    await response.json();

                if (
                    !response.ok ||
                    !result.success
                ) {
                    throw new Error(
                        result.error ||
                        "Unable to update driver status."
                    );
                }

                renderDriverAvailability(
                    result.availability
                );

            } catch (error) {
                console.error(
                    "Driver status transition failed:",
                    error
                );

                setDriverStatusFeedback(
                    error.message ||
                    "Unable to update driver status."
                );

                if (driverStatusAction) {
                    const presentation =
                        getDriverStatusPresentation(
                            currentDriverStatus
                        );

                    driverStatusAction.disabled = false;
                    driverStatusAction.textContent =
                        presentation.action;
                }
            }
        }

        function renderOffer(offer) {
            currentOffer = offer;

            if (!offerCard) {
                return;
            }

            offerCard.hidden = false;

            setStatus(
                "A new HABESHAGO ride offer is waiting " +
                "for your response."
            );

            setText(
                "[data-offer-reference]",
                offer.offer_reference
            );

            const pickup =
                offer.pickup || {};

            const destination =
                offer.destination || {};

            setText(
                "[data-offer-pickup]",
                (
                    pickup.latitude !==
                        undefined &&
                    pickup.longitude !==
                        undefined
                )
                    ? (
                        Number(
                            pickup.latitude
                        ).toFixed(5) +
                        ", " +
                        Number(
                            pickup.longitude
                        ).toFixed(5)
                    )
                    : "—"
            );

            setText(
                "[data-offer-destination]",
                (
                    destination.latitude !==
                        undefined &&
                    destination.longitude !==
                        undefined
                )
                    ? (
                        Number(
                            destination.latitude
                        ).toFixed(5) +
                        ", " +
                        Number(
                            destination.longitude
                        ).toFixed(5)
                    )
                    : "—"
            );

            setText(
                "[data-offer-distance]",
                formatNumber(
                    offer.distance,
                    "km"
                )
            );

            setText(
                "[data-offer-trip-eta]",
                offer.trip_eta === null ||
                offer.trip_eta === undefined
                    ? "—"
                    : `${offer.trip_eta} min`
            );

            setText(
                "[data-offer-pickup-eta]",
                offer.pickup_eta === null ||
                offer.pickup_eta === undefined
                    ? "—"
                    : `${offer.pickup_eta} min`
            );

            setText(
                "[data-offer-fare]",
                formatNumber(
                    offer.fare,
                    "ETB"
                )
            );

            setText(
                "[data-offer-payment]",
                offer.payment_method
            );

            setText(
                "[data-offer-service]",
                offer.service_type
            );

            setFeedback("");

            if (acceptButton) {
                acceptButton.disabled = false;
                acceptButton.textContent =
                    "Accept Ride";
            }

            if (rejectButton) {
                rejectButton.disabled = false;
                rejectButton.textContent =
                    "Reject Ride";
            }
        }

        function renderNoOffer() {
            currentOffer = null;

            setStatus(
                "No pending ride offer right now."
            );

            if (offerCard) {
                offerCard.hidden = true;
            }

            setFeedback("");
        }

        async function fetchPendingOffer() {
            const initData =
                getTelegramInitData();

            if (!initData) {
                setStatus(
                    "Open the Driver Dashboard from " +
                    "Telegram to receive live ride offers."
                );

                if (offerCard) {
                    offerCard.hidden = true;
                }

                return;
            }

            try {
                const response = await fetch(
                    "/api/driver/offers/pending",
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
                    !result.success
                ) {
                    throw new Error(
                        result.error ||
                        "Unable to load ride offer."
                    );
                }

                if (!result.offer) {
                    renderNoOffer();
                    return;
                }

                renderOffer(
                    result.offer
                );

            } catch (error) {
                console.error(
                    "Pending ride offer failed:",
                    error
                );

                setStatus(
                    error.message ||
                    "Unable to load ride offer."
                );
            }
        }

        async function acceptCurrentOffer() {
            if (
                !currentOffer ||
                !currentOffer.offer_id
            ) {
                setFeedback(
                    "No pending ride offer is available."
                );
                return;
            }

            const initData =
                getTelegramInitData();

            if (!initData) {
                setFeedback(
                    "Telegram authentication is required."
                );
                return;
            }

            if (acceptButton) {
                acceptButton.disabled = true;
                acceptButton.textContent =
                    "Accepting Ride...";
            }

            if (rejectButton) {
                rejectButton.disabled = true;
            }

            setFeedback("");

            try {
                const response = await fetch(
                    (
                        "/api/driver/offers/" +
                        currentOffer.offer_id +
                        "/accept"
                    ),
                    {
                        method: "POST",
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
                    !result.success
                ) {
                    throw new Error(
                        result.error ||
                        "Unable to accept ride."
                    );
                }

                setFeedback(
                    "Ride accepted successfully."
                );

                setStatus(
                    "Ride assigned. Canonical Ride #" +
                    result.ride_id +
                    " is now active."
                );

                currentOffer = null;

                if (acceptButton) {
                    acceptButton.textContent =
                        "Ride Accepted";
                }

                if (rejectButton) {
                    rejectButton.disabled = true;
                }

            } catch (error) {
                console.error(
                    "Ride acceptance failed:",
                    error
                );

                setFeedback(
                    error.message ||
                    "Unable to accept ride."
                );

                if (acceptButton) {
                    acceptButton.disabled = false;
                    acceptButton.textContent =
                        "Accept Ride";
                }

                if (rejectButton) {
                    rejectButton.disabled = false;
                }
            }
        }

        async function rejectCurrentOffer() {
            if (
                !currentOffer ||
                !currentOffer.offer_id
            ) {
                setFeedback(
                    "No pending ride offer is available."
                );
                return;
            }

            const initData =
                getTelegramInitData();

            if (!initData) {
                setFeedback(
                    "Telegram authentication is required."
                );
                return;
            }

            if (acceptButton) {
                acceptButton.disabled = true;
            }

            if (rejectButton) {
                rejectButton.disabled = true;
                rejectButton.textContent =
                    "Rejecting Ride...";
            }

            setFeedback("");

            try {
                const response = await fetch(
                    (
                        "/api/driver/offers/" +
                        currentOffer.offer_id +
                        "/reject"
                    ),
                    {
                        method: "POST",
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
                    !result.success
                ) {
                    throw new Error(
                        result.error ||
                        "Unable to reject ride."
                    );
                }

                setFeedback(
                    "Ride offer rejected."
                );

                setStatus(
                    "No pending ride offer right now."
                );

                currentOffer = null;

                if (offerCard) {
                    offerCard.hidden = true;
                }

                if (acceptButton) {
                    acceptButton.disabled = true;
                }

                if (rejectButton) {
                    rejectButton.disabled = true;
                    rejectButton.textContent =
                        "Reject Ride";
                }

            } catch (error) {
                console.error(
                    "Ride rejection failed:",
                    error
                );

                setFeedback(
                    error.message ||
                    "Unable to reject ride."
                );

                if (acceptButton) {
                    acceptButton.disabled = false;
                }

                if (rejectButton) {
                    rejectButton.disabled = false;
                    rejectButton.textContent =
                        "Reject Ride";
                }
            }
        }

        if (driverStatusAction) {
            driverStatusAction.addEventListener(
                "click",
                transitionDriverStatus
            );
        }

        if (acceptButton) {
            acceptButton.addEventListener(
                "click",
                acceptCurrentOffer
            );
        }

        if (rejectButton) {
            rejectButton.addEventListener(
                "click",
                rejectCurrentOffer
            );
        }

        fetchDriverContext();
        fetchPendingOffer();
    }
);
