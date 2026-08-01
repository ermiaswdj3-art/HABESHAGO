"use strict";

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("habeshago-map");

    if (!mapElement) {
        return;
    }

    const latitude = Number(mapElement.dataset.latitude);
    const longitude = Number(mapElement.dataset.longitude);
    const zoom = Number(mapElement.dataset.zoom);

    const coordinateLabel = document.querySelector(
        "[data-pickup-coordinates]"
    );

    const pickupTitle = document.querySelector(
        "[data-pickup-location-name]"
    );

    const confirmButton = document.querySelector(
        "[data-confirm-pickup]"
    );

    let selectedLatitude = latitude;
    let selectedLongitude = longitude;

    const map = L.map("habeshago-map").setView(
        [latitude, longitude],
        zoom
    );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution:
                "&copy; OpenStreetMap contributors",
        }
    ).addTo(map);

    function updateCenter() {
        const center = map.getCenter();

        selectedLatitude = center.lat;
        selectedLongitude = center.lng;

        if (coordinateLabel) {
            coordinateLabel.textContent =
                `${selectedLatitude.toFixed(6)}, ` +
                `${selectedLongitude.toFixed(6)}`;
        }

        if (pickupTitle) {
            pickupTitle.textContent =
                "Pickup location selected";
        }

        if (confirmButton) {
            confirmButton.disabled = false;
        }
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
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        latitude: selectedLatitude,
                        longitude: selectedLongitude,
                        name: "Selected on Map",
                    }),
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "Pickup could not be saved."
                );
            }

            console.log(
                "Pickup saved successfully:",
                result.trip
            );

            window.location.href = "/trip-planner";
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

    map.on("moveend", updateCenter);

    if (confirmButton) {
        confirmButton.addEventListener(
            "click",
            savePickup
        );
    }

    updateCenter();

    setTimeout(function () {
        map.invalidateSize();
    }, 100);
});