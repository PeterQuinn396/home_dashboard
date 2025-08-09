import logging
from datetime import datetime, timedelta
from nicegui import ui, app
from uuid import uuid4
from jinja2 import Template


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _get_web_route_string_from_date(day: int, month: int, year: int, hour: int, minute_multiple_of_ten: int) -> str:
    s = f"https://skaping.s3.gra.io.cloud.ovh.net/montreal/grand-port/tour-d-observation/{year}/{month:02}/{day:02}/large/{hour + 6:02}-{minute_multiple_of_ten:02}.jpg"
    return s


def _get_current_time() -> tuple[int, int, int, int]:
    now = datetime.now()
    now -= timedelta(minutes=10)
    return now.day, now.month, now.year, now.hour, (now.minute // 10) * 10


def webcam_widget():
    with open("pan.html.jinja2", "r") as f:
        template_str = Template(f.read())

    @ui.refreshable
    def render_webcam():
        day, month, year, hour, minute = _get_current_time()
        url = _get_web_route_string_from_date(day, month, year, hour, minute)
        jinja_context = {"PANORAMA_URL": url}
        rendered_html = template_str.render(jinja_context)
        with open("pan.html", "w") as f:
            f.write(rendered_html)

        logger.info(f"Webcam URL: {url}")
        url_local = f"/pan.html?id={uuid4()}"
        access = app.add_static_file(local_file="pan.html", url_path=url_local)
        logger.info(f"Access URL: {access}")
        ui.html(
            f'<iframe src="{access}" width="800" height="450" scrolling="no" style="border:none; overflow:hidden; scrollbar-width: none;"  title="Panorama Viewer" ></iframe>'
        )

    render_webcam()
    # refresh every 10 minutes
    ui.timer(60 * 10, callback=render_webcam.refresh)
