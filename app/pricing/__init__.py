"""
HABESHAGO Pricing Platform

Canonical package boundary for HABESHAGO's
versioned and auditable transportation pricing.

Pricing implementation modules are intentionally
not imported eagerly here.

Consumers should import the specific pricing
submodule they require. This keeps package
initialization lightweight and prevents circular
dependencies between pricing services and
persistence repositories.
"""
