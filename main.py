from datetime import datetime
from nicegui import ui
import argparse
import os
import logging
from stm import stm_widget
from webcam import webcam_widget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def weather_widget():
    # https://weatherwidget.io/

    ui.add_body_html(r"""
    <a class="weatherwidget-io" href="https://forecast7.com/en/45d50n73d57/montreal/" data-label_1="MONTREAL" data-label_2="WEATHER" data-theme="weather_one" >MONTREAL WEATHER</a>
    <script>
    !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
    </script>
    """)

    ui.add_body_html(r'<script async src="https://app3.weatherwidget.org/js/?id=ww_ff894e771c7c3"></script>')
    with ui.column().classes("items-center"):
        ui.html(r"""
        <iframe width="650" height="450" src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=°C&metricWind=km/h&zoom=8&overlay=radar&product=radar&level=surface&lat=45.449&lon=-73.586&message=true&play=1" frameborder="0"></iframe>
        """)


def _parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    default_key = os.getenv("STM_API_KEY")
    parser.add_argument(
        "--stm-api-key",
        default=default_key,
        required=default_key is None,
        help="Defaults to STM_API_KEY",
    )

    return parser.parse_args()


def main(api_key):
    logger.info("rendering ")
    with ui.row().classes("justify-evenly items-center w-full"):
        with ui.row():
            stm_widget(api_key)
            weather_widget()
            webcam_widget()


if __name__ == "__main__":
    args = _parse_args()
    main(api_key=args.stm_api_key)
    ui.run(dark=True, reload=False)
