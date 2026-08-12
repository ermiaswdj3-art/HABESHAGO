"use strict";

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("habeshago-map");

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
            if (source === "device") {
                pickupTitle.textContent =
                    "Your current location";
            } else {
                pickupTitle.textContent =
                    "Adjusted pickup location";
            }
        }

        if (confirmButton) {
            confirmButton.disabled = false;
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

        const center = map.getCenter();

        updatePickupDisplay(
            center.lat,
            center.lng,
            "map"
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
                        name:
                            locationSource ===
                            "device"
                                ? "Current Location"
                                : "Selected on Map",
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
                result.trip
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
