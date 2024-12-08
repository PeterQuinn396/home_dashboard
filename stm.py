import logging
import os
import requests
from dataclasses import dataclass
import json
from nicegui import ui


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STM_API_ROUTE = "https://api.stm.info/pub/od/i3/v2/messages"

ICON_SIZE = "md"

REFRESH_TIME_SEC = 60


@dataclass
class LineStatus:
    ok: bool = True
    desc: str = ""


@dataclass
class STMStatus:
    """Struct to hold the relevant info we want from the API call.
    This will get rendered to UI elements.
    """

    green_line: LineStatus = LineStatus()
    orange_line: LineStatus = LineStatus()
    bus_61_est: LineStatus = LineStatus()


def _parse_status_json(json_info: dict) -> STMStatus:
    status = STMStatus()
    for alert in json_info["alerts"]:
        route_name = alert["informed_entities"][0]["route_short_name"]
        try:
            direction = alert["informed_entities"][0]["direction_id"]
        except KeyError:
            direction = ""
        desc = alert["description_texts"][1]["text"]
        # check green line
        match route_name:
            case "1":
                status.green_line.ok = desc == "Normal métro service"
                status.green_line.desc = desc
            case "2":
                status.orange_line.desc = desc == "Normal métro service"
                status.orange_line.desc = desc
            case "61":
                if direction == "E":
                    status.bus_61_est.desc = desc

    return status


def _get_current_stm_status(api_key) -> STMStatus | None:
    response = requests.get(
        f"{STM_API_ROUTE}/etatservice",
        headers={"accept": "application/json", "apiKey": api_key},
    )

    logger.info(f"Got response {response.status_code}")

    # logger.info(f"{response.json()}")

    if response.ok:
        status = _parse_status_json(response.json())
        logger.info(f"Got status: {status}")
        return status
    else:
        logger.error("Got bad response")
        return None


def _status_icon(status: bool):
    if status:
        ui.icon(name="check_circle", color="green", size=ICON_SIZE)
    else:
        ui.icon(name="info", color="yellow", size=ICON_SIZE)


def stm_widget(api_key: str):
    @ui.refreshable
    def render_info_panel():
        logger.info("Rendering stm data")
        status = _get_current_stm_status(api_key)
        with ui.column():
            with ui.row():
                ui.icon(name="subway", color="green", size=ICON_SIZE)
                ui.label(f"{status.green_line.desc} ")
                _status_icon(status.green_line.ok)

            with ui.row():
                ui.icon(name="subway", color="orange", size=ICON_SIZE)
                ui.label(f"{status.orange_line.desc} ")
                _status_icon(status.orange_line.ok)

            with ui.row():
                ui.icon(name="directions_bus", color="white", size=ICON_SIZE)
                ui.label(f"61 Est (Costco) {status.bus_61_est.desc}")
                _status_icon(status.bus_61_est.ok)

    render_info_panel()
    ui.timer(REFRESH_TIME_SEC, callback=render_info_panel.refresh)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)
    logger.info("Running debug")

    api_key = os.getenv("STM_API_KEY")
    if api_key is None:
        raise ValueError("API key was none")

    status = _get_current_stm_status(api_key)

    print(status)
