"use strict";

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById(
        "habeshago-map"
    );

    if (!mapElement) {
        return;
    }

    const fallbackLatitude = Number(
        mapElement.dataset.latitude
    );

    const fallbackLongitude = Number(
        mapElement.dataset.longitude
    );

    const defaultZoom = Number(
        mapElement.dataset.zoom
    );

    const coordinateLabel = document.querySelector(
        "[data-pickup-coordinates]"
    );

    const contextLabel = document.querySelector(
        "[data-pickup-location-context]"
    );

    const pickupTitle = document.querySelector(
        "[data-pickup-location-name]"
    );

    const confirmButton = document.querySelector(
        "[data-confirm-pickup]"
    );

    let selectedLatitude = fallbackLatitude;
    let selectedLongitude = fallbackLongitude;

    let locationResolved = false;
    let locationSource = "map";

    let suppressNextMove = false;
    let passengerDraggedMap = false;

    let geocodeRequestSequence = 0;

    const map = L.map(
        "habeshago-map"
    ).setView(
        [
            fallbackLatitude,
            fallbackLongitude,
        ],
        defaultZoom
    );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution:
                "&copy; OpenStreetMap contributors",
        }
    ).addTo(map);

    const pickupMarker = L.marker(
        [
            fallbackLatitude,
            fallbackLongitude,
        ]
    ).addTo(map);

    function updatePickupDisplay(
        latitude,
        longitude,
        source
    ) {
        selectedLatitude = latitude;
        selectedLongitude = longitude;
        locationSource = source;

        pickupMarker.setLatLng([
            selectedLatitude,
            selectedLongitude,
        ]);

        if (coordinateLabel) {
            coordinateLabel.textContent =
                `${selectedLatitude.toFixed(6)}, ` +
                `${selectedLongitude.toFixed(6)}`;
        }

        if (pickupTitle) {
            pickupTitle.textContent =
                source === "device"
                    ? "Your current location"
                    : "Adjusted pickup location";
        }

        if (confirmButton) {
            confirmButton.disabled = false;
        }
    }

    async function loadPickupContext(
        latitude,
        longitude
    ) {
        const requestSequence =
            ++geocodeRequestSequence;

        if (contextLabel) {
            contextLabel.textContent =
                "Finding nearby location details...";
        }

        const query =
            new URLSearchParams({
                latitude:
                    String(latitude),
                longitude:
                    String(longitude),
            });

        try {
            const response = await fetch(
                `/api/location/reverse?${query}`
            );

            const result =
                await response.json();

            if (
                requestSequence !==
                geocodeRequestSequence
            ) {
                return;
            }

            if (
                !response.ok ||
                !result.success
            ) {
                throw new Error(
                    result.message ||
                    "Location details unavailable."
                );
            }

            const location =
                result.location || {};

            const fullName =
                String(
                    location.full_name || ""
                ).trim();

            const shortName =
                String(
                    location.short_name || ""
                ).trim();

            if (contextLabel) {
                contextLabel.textContent =
                    fullName ||
                    shortName ||
                    "Pickup coordinates identified.";
            }
        } catch (error) {
            console.warn(
                "Pickup context unavailable:",
                error
            );

            if (
                requestSequence !==
                geocodeRequestSequence
            ) {
                return;
            }

            if (contextLabel) {
                contextLabel.textContent =
                    "Pickup coordinates identified.";
            }
        }
    }

    function useMapCenter() {
        if (suppressNextMove) {
            suppressNextMove = false;
            return;
        }

        if (!locationResolved) {
            return;
        }

        if (!passengerDraggedMap) {
            return;
        }

        passengerDraggedMap = false;

        const center = map.getCenter();

        updatePickupDisplay(
            center.lat,
            center.lng,
            "map"
        );

        loadPickupContext(
            center.lat,
            center.lng
        );
    }

    function handleLocationSuccess(position) {
        const latitude =
            position.coords.latitude;

        const longitude =
            position.coords.longitude;

        suppressNextMove = true;

        map.setView(
            [
                latitude,
                longitude,
            ],
            17
        );

        updatePickupDisplay(
            latitude,
            longitude,
            "device"
        );

        locationResolved = true;

        loadPickupContext(
            latitude,
            longitude
        );

        console.log(
            "Passenger location resolved:",
            {
                latitude,
                longitude,
                accuracy:
                    position.coords.accuracy,
            }
        );
    }

    function handleLocationFailure(error) {
        locationResolved = true;

        console.warn(
            "Passenger location unavailable:",
            error
        );

        updatePickupDisplay(
            fallbackLatitude,
            fallbackLongitude,
            "map"
        );

        if (pickupTitle) {
            pickupTitle.textContent =
                "Choose your pickup location";
        }

        if (contextLabel) {
            contextLabel.textContent =
                "Move the map to set your pickup.";
        }
    }

    function requestPassengerLocation() {
        if (!navigator.geolocation) {
            handleLocationFailure(
                new Error(
                    "Geolocation is not supported."
                )
            );

            return;
        }

        if (pickupTitle) {
            pickupTitle.textContent =
                "Finding your current location...";
        }

        if (contextLabel) {
            contextLabel.textContent =
                "Waiting for location permission...";
        }

        if (coordinateLabel) {
            coordinateLabel.textContent =
                "Please allow location access.";
        }

        navigator.geolocation.getCurrentPosition(
            handleLocationSuccess,
            handleLocationFailure,
            {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 30000,
            }
        );
    }

    async function savePickup() {
        if (!confirmButton) {
            return;
        }

        confirmButton.disabled = true;
        confirmButton.textContent =
            "Saving Pickup Location...";

        try {
            const response = await fetch(
                "/api/trip/pickup",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        latitude:
                            selectedLatitude,
                        longitude:
                            selectedLongitude,
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
                    "Pickup could not be saved."
                );
            }

            console.log(
                "Pickup saved successfully:",
                {
                    source: locationSource,
                    trip: result.trip,
                }
            );

            window.location.href =
                "/trip-planner";
        } catch (error) {
            console.error(
                "Pickup save failed:",
                error
            );

            alert(
                error.message ||
                "We could not save your pickup. " +
                "Please try again."
            );

            confirmButton.disabled = false;
            confirmButton.textContent =
                "Confirm Pickup Location";
        }
    }

    map.on(
        "dragstart",
        function () {
            if (!locationResolved) {
                return;
            }

            passengerDraggedMap = true;
        }
    );

    map.on(
        "moveend",
        useMapCenter
    );

    if (confirmButton) {
        confirmButton.addEventListener(
            "click",
            savePickup
        );
    }

    setTimeout(function () {
        map.invalidateSize();
    }, 100);

    requestPassengerLocation();
});
