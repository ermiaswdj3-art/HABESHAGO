# 🇪🇹🚖 HABESHAGO Platform

> **Engineering Ethiopia's AI-Powered Mobility Future**

HABESHAGO is an AI-powered mobility and logistics platform engineered in Ethiopia.

The platform combines modular software architecture with Artificial Intelligence to build the next generation of transportation and logistics services.

Rather than creating isolated applications, HABESHAGO is being engineered as one shared platform capable of supporting ride-hailing, public transportation, package delivery, logistics, and future smart mobility services through a unified engineering foundation.

---

# 🌍 Vision

Our vision is to build Ethiopia's intelligent mobility infrastructure.

HABESHAGO is designed as a long-term platform where multiple transportation and logistics services operate together while sharing the same scalable architecture.

Instead of rebuilding software for every new service, HABESHAGO grows by extending a common platform.

---

# 🤖 Artificial Intelligence Strategy

Artificial Intelligence is not an add-on feature within HABESHAGO.

It is a strategic layer of the platform architecture.

The platform is being engineered so AI systems can continuously improve mobility services by learning from platform data while remaining independent of the core business logic.

Future AI capabilities include:

- 🧠 Intelligent Driver Dispatch
- 📈 Demand Forecasting
- 🛣 Route Optimization
- ⏱ Predictive ETA
- 💰 Dynamic Pricing
- 🛡 Fraud Detection
- 🚦 Traffic Prediction
- 🚌 Intelligent Public Bus Tracking
- 📊 Smart Fleet Analytics
- 🤖 AI Customer Support
- 🎯 Personalized Mobility Recommendations

---

# 🚖 Current Platform Capabilities

## Passenger

- Request a ride
- Share pickup location
- Share destination
- Receive fare estimation
- Confirm or cancel rides
- View ride history

---

## Driver

- Register as a driver
- Go online
- Go offline
- Share live location
- Receive ride requests
- Accept rides
- Complete trips

---

# 🏛 Platform Architecture

HABESHAGO is organized around independent platform components.

Each component has a single responsibility while working together to form one intelligent platform.

---

## 🚖 Ride State Platform

Responsible for managing the complete lifecycle of every ride.

Examples include:

- Requested
- Accepted
- Driver Arrived
- Trip Started
- Completed
- Cancelled

---

## 📡 Event Platform

Publishes important platform events whenever meaningful actions occur.

Examples include:

- Ride Requested
- Ride Accepted
- Driver Online
- Driver Offline

---

## 🔄 Synchronization Platform

Keeps independent platform components synchronized through platform events.

---

## 🧠 Intelligent Dispatch Platform

Selects the most appropriate driver using multiple decision factors including:

- Driver availability
- Distance from pickup
- Driver rating
- Live location freshness

The platform is designed so AI can continuously improve dispatch decisions over time.

---

## 📍 Live Location Platform

Maintains real-time driver location information and determines whether a location is fresh enough for intelligent dispatch.

---

## 🌐 Public API Foundation

Provides stable public interfaces for future clients including:

- Android applications
- iOS applications
- Web dashboards
- Public Bus Tracker
- Third-party integrations
- Future AI services

---

# 📂 Repository Structure

```text
app/
├── api/
├── config/
├── constants/
├── database/
├── handlers/
├── models/
├── repositories/
├── services/
├── state/

docs/
```

---

# 🏗 Engineering Principles

The HABESHAGO Platform is built around several core engineering principles.

- Modular Architecture
- Single Responsibility
- Event-Driven Communication
- Explainable Platform Decisions
- Versioned Public APIs
- Separation of Concerns
- Extensible Platform Design
- AI-Ready Architecture

---

# 📚 Documentation

Technical documentation is located inside the `docs/` directory.

Current documents include:

- PLATFORM_ARCHITECTURE.md
- PUBLIC_API_FOUNDATION.md
- LIVE_LOCATION_PLATFORM.md

Additional platform documentation will continue to evolve alongside the project.

---

# 💻 Technology Stack

Current technologies include:

- Python
- python-telegram-bot
- SQLite
- Git
- GitHub

Future technologies may include:

- FastAPI
- PostgreSQL
- Redis
- Docker
- Kubernetes
- Cloud Infrastructure
- Android
- iOS

---

# 🗺 Roadmap

## ✅ Platform Foundations

- Ride State Platform
- Event Platform
- Synchronization Platform
- Intelligent Dispatch Platform
- Live Location Platform
- Public API Foundation

---

## 🚧 Current Focus

- Public API Expansion
- Platform Documentation
- Developer Experience
- AI Foundation

---

## 🔮 Future Ecosystem

The long-term HABESHAGO ecosystem includes:

- 🚖 Ride Hailing
- 📦 Package Delivery
- 🚌 Public Bus Tracker
- 🚚 Logistics Services
- 📍 Fleet Management
- 🤖 AI Mobility Services
- 🌍 Smart City Integrations

---

# 📈 Project Status

HABESHAGO is currently under active development.

The primary focus is building a robust engineering platform before rapidly expanding user-facing products.

This approach allows every future service to reuse the same architecture instead of reinventing it.

---

# 🇪🇹 Built in Ethiopia

HABESHAGO is proudly engineered in Ethiopia with the ambition of contributing to the country's transportation and logistics future through thoughtful software architecture and responsible Artificial Intelligence.

---

# ❤️ A Journey Worth Building

HABESHAGO started with one simple objective:

> Build a ride-hailing service.

It has since grown into something much larger.

Today, HABESHAGO is being engineered as an AI-powered mobility platform where every milestone strengthens a shared foundation for future transportation services.

Every commit represents another step toward that vision.

---

## HABESHAGO Mini App

HABESHAGO now includes a browser-based Mini App built with Flask.

### Current Features

- Ecosystem Home Screen
- Passenger Dashboard
- Driver Dashboard
- Shared Design System
- Responsive Layout
- Navigation Between Pages

### Architecture

```
Python Page Models
        │
        ▼
Flask Routes
        │
        ▼
Jinja Templates
        │
        ▼
CSS Design System
        │
        ▼
Browser
```

### Roadmap

- Interactive Ride Request
- Live Map Integration
- Driver Tracking
- Public Bus Tracker
- Logistics Dashboard
- AI-powered Features

> **"Engineering Ethiopia's AI-Powered Mobility Future."**

🇪🇹 Built with dedication.

# 🚀 Mini App Deployment

HABESHAGO includes a production-ready deployment path
for the Telegram Mini App.

## Render Deployment

The repository includes `render.yaml`, which defines the
HABESHAGO Mini App as a Render web service.

Render uses:

```text
Build:
pip install -r requirements.txt

Start:
python -m app.mini_app.runtime

Health:
GET /health
```
The production runtime:

- binds to `0.0.0.0`;
- respects the deployment platform `PORT`;
- starts the Flask Mini App through Waitress;
- exposes `/health` for deployment health checks.

## Required Environment Variables

Configure these values securely in the Render dashboard:

```text
BOT_TOKEN
ADMIN_ID
HABESHAGO_MINI_APP_URL
HABESHAGO_MINI_APP_DRIVER_ID
```

Never commit real secret values to `.env`,
`.env.example`, or `render.yaml`.

## Public Mini App URL

After a successful deployment, Render provides a public
HTTPS URL for the HABESHAGO Mini App.

That URL becomes the production value of:

```text
HABESHAGO_MINI_APP_URL
```

The Telegram passenger menu can then expose:

```text
🌐 Open HABESHAGO
```

which launches the deployed HABESHAGO Mini App inside
Telegram.

## Deployment Boundary

The current deployment foundation prepares the web
application for a controlled MVP deployment.

The current SQLite database remains local application
storage and should not yet be treated as durable
production persistence.