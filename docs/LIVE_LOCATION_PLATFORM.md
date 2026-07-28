HABESHAGO Live Location Platform

Purpose
-------
The Live Location Platform provides fresh,
time-aware location data for drivers and
future platform entities.

Current Flow
------------

Driver goes online
        ↓
Driver shares Telegram GPS
        ↓
Database location updated
        ↓
Live Location Service records timestamp
        ↓
Live Location Engine evaluates freshness
        ↓
Location becomes LIVE or STALE
        ↓
Intelligent Dispatch uses only LIVE locations

Current MVP Policy
------------------
Driver locations are shared manually through
Telegram.

A location remains usable for 10 minutes.

This duration supports the current manual
Telegram workflow while still rejecting old
database coordinates.

Future clients with continuous background GPS
updates may use a shorter freshness window.

Responsibilities
----------------
- Record live coordinates
- Record update timestamps
- Classify LIVE and STALE locations
- Reject missing or stale dispatch data
- Provide trusted coordinates to Dispatch
- Expose location health for operations

Current Limitation
------------------
Live locations are stored in application memory.

They are erased when the bot process restarts.

Future production versions may use Redis or
another shared high-speed location store.

Engineering Principle
---------------------
Dispatch decisions are only as reliable as the
location data they receive.

HABESHAGO must distinguish coordinates that
exist from coordinates that are fresh enough
to trust.