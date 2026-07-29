# HABESHAGO Platform Architecture

## Overview

HABESHAGO is a modular mobility platform designed for Ethiopia.

The platform is built around independent components that each have a single
responsibility while working together through well-defined interfaces.

---

## Core Platform

### Ride State Platform

Responsible for managing the lifecycle of every ride.

Examples:

- Requested
- Accepted
- Driver Arrived
- Trip Started
- Completed
- Cancelled

---

### Event Platform

Publishes important events across the platform.

Examples:

- Ride Requested
- Ride Accepted
- Driver Online
- Driver Offline

---

### Synchronization Platform

Keeps platform components synchronized whenever important events occur.

---

### Intelligent Dispatch Platform

Selects the best available driver using platform rules rather than simple
first-come-first-served assignment.

Current factors include:

- Driver availability
- Distance to pickup
- Driver rating
- Live location freshness

---

### Live Location Platform

Maintains the latest known driver locations and determines whether a location
is still considered usable for dispatch.

---

### Public API Foundation

Provides a stable interface for future clients including:

- Mobile applications
- Web dashboards
- Public Bus Tracker
- External integrations

---

## Engineering Principles

- Modular architecture
- Single responsibility
- Clear separation of concerns
- Versioned public APIs
- Explainable platform decisions
- Extensible design

---

## Long-Term Vision

The HABESHAGO Platform is intended to support multiple services through one
shared engineering foundation, including:

- Ride Hailing
- Package Delivery
- Public Bus Tracking
- Future Mobility Services