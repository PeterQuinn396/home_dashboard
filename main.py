from nicegui import ui
import argparse
import os
import logging
from stm import stm_widget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def weather_widget():
    # https://weatherwidget.io/

    ui.add_body_html(
        r'<script async src="https://app3.weatherwidget.org/js/?id=ww_ff894e771c7c3"></script>'
    )
    with ui.column().classes("items-center"):
        ui.html(r"""
        <div id="ww_ff894e771c7c3" v='1.3' loc='id' a='{"t":"horizontal","lang":"en","sl_lpl":1,"ids":["wl2935"],"font":"Arial","sl_ics":"one_a","sl_sot":"celsius","cl_bkg":"image","cl_font":"#FFFFFF","cl_cloud":"#FFFFFF","cl_persp":"#81D4FA","cl_sun":"#FFC107","cl_moon":"#FFC107","cl_thund":"#FF5722"}'>More forecasts: <a href="https://oneweather.org/calgary/30_days/" id="ww_ff894e771c7c3_u" target="_blank">30 day weather forecast Calgary</a></div>
        """)

        ui.html(r"""
        <iframe width="650" height="450" src="https://embed.windy.com/embed.html?type=map&location=coordinates&metricRain=mm&metricTemp=°C&metricWind=km/h&zoom=8&overlay=radar&product=radar&level=surface&lat=45.449&lon=-73.586&message=true&play=1" frameborder="0"></iframe>
        """)


def _parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    default_key = os.getenv("STM_API_KEY")
    parser.add_argument(
        "--stm-api-key",
        default=default_key,
        required=default_key is None,
        help="Defaults to STM_API_KEY",
    )

    return parser.parse_args()


# @ui.page("/")
def main(api_key):
    # ui.markdown("# Home Dashboard")

    logger.info("rendering ")
    with ui.row().classes("justify-evenly items-center w-full"):
        with ui.column():
            weather_widget()
        with ui.column():
            stm_widget(api_key)


if __name__ == "__main__":
    args = _parse_args()
    main(api_key=args.stm_api_key)
    ui.run(dark=True, reload=False)
