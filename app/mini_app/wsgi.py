"""
HABESHAGO Mini App WSGI Entry Point

Exposes the Flask application for production-style
WSGI servers.

Commit #114 purpose:

- provide a stable Mini App runtime entry point;
- keep Flask development startup separate from
  production serving;
- prepare HABESHAGO for HTTPS deployment.
"""

from app.mini_app.web import app


application = app