# HABESHAGO Public API Foundation

## Purpose

The HABESHAGO Public API provides a stable interface through which external
applications communicate with the HABESHAGO Platform.

Instead of accessing internal services directly, clients interact with
well-defined public endpoints.

---

## Design Principles

- Versioned APIs
- Consistent response format
- Central route registry
- Clear separation between internal services and public interfaces
- Backward compatibility where possible

---

## Current API Version

- v1

---

## Current Public Endpoints

| Endpoint | Purpose |
|----------|---------|
| /api/v1/health | Verify that the HABESHAGO Platform is running |

---

## Response Format

Every endpoint returns the same structure:

```json
{
    "success": true,
    "message": "...",
    "data": {}
}
```

---

## API Components

- api_versions.py
- api_routes.py
- api_response.py
- router.py
- health.py

---

## Future Endpoints

The Public API is designed to expand with additional endpoints, including:

- Rides
- Drivers
- Passengers
- Dispatch
- Live Locations
- Public Bus Tracking
- Package Delivery
- Payments

---

## Engineering Goal

The Public API serves as the official communication layer between HABESHAGO
and external applications while keeping the internal platform architecture
modular and maintainable.