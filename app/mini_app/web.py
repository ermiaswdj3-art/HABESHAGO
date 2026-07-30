"""
HABESHAGO Mini App Web Server

Serves the HABESHAGO Mini App locally using Flask.
"""

from flask import Flask, render_template

from app.mini_app.pages.home import get_home_page
from app.mini_app.pages.passenger_dashboard import (
    get_passenger_dashboard,
)

from app.mini_app.pages.driver_dashboard import (
    get_driver_dashboard,
)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


@app.route("/")
def home():
    """
    Render the HABESHAGO ecosystem home page.
    """

    page = get_home_page()

    return render_template(
        "home.html",
        page=page,
        active_page="home",
    )


@app.route("/passenger")
def passenger_dashboard():
    """
    Render the HABESHAGO passenger dashboard.
    """

    page = get_passenger_dashboard()

    return render_template(
        "passenger_dashboard.html",
        page=page,
        active_page="passenger",
    )

@app.route("/driver")
def driver_dashboard():
    """
    Render the HABESHAGO driver dashboard.
    """

    page = get_driver_dashboard()

    return render_template(
        "driver_dashboard.html",
        page=page,
        active_page="driver",
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )