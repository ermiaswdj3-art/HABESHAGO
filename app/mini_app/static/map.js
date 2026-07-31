"use strict";

document.addEventListener("DOMContentLoaded", () => {

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

        coordinateLabel.textContent =
            `${center.lat.toFixed(6)}, ${center.lng.toFixed(6)}`;

        pickupTitle.textContent =
            "Pickup location selected";

        confirmButton.disabled = false;
    }

    map.on("moveend", updateCenter);

    updateCenter();

    setTimeout(() => {
        map.invalidateSize();
    }, 100);

});