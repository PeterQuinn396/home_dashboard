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

    metro_line_green: LineStatus = LineStatus()
    metro_line_orange: LineStatus = LineStatus()
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
                status.metro_line_green.ok = desc == "Normal métro service"
                status.metro_line_green.desc = desc
            case "2":
                status.metro_line_orange.ok = desc == "Normal métro service"
                status.metro_line_orange.desc = desc
            case "61":
                if direction == "E":
                    status.bus_61_est.desc = desc

    return status


def _get_stm_json(api_key) -> dict:
    response = requests.get(
        f"{STM_API_ROUTE}/etatservice",
        headers={"accept": "application/json", "apiKey": api_key},
    )

    if response.ok:
        return response.json()
    else:
        logger.error("Failed to fetch STM data")
        return {}


def _status_icon(status: bool):
    if status:
        ui.icon(name="check_circle", color="green", size=ICON_SIZE)
    else:
        ui.icon(name="info", color="yellow", size=ICON_SIZE)


def stm_widget(api_key: str):
    @ui.refreshable
    def render_info_panel():
        logger.info("Rendering stm data")
        stm_json = _get_stm_json(api_key)
        if not stm_json:
            ui.label("Failed to fetch STM data").classes("text-red")
            return

        status: STMStatus = _parse_status_json(stm_json)
        with ui.column():
            with ui.row():
                ui.icon(name="subway", color="green", size=ICON_SIZE)
                ui.label(f"{status.metro_line_green.desc} ")
                _status_icon(status.metro_line_green.ok)

            with ui.row():
                ui.icon(name="subway", color="orange", size=ICON_SIZE)
                ui.label(f"{status.metro_line_orange.desc} ")
                _status_icon(status.metro_line_orange.ok)

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

    stm_json = _get_stm_json(api_key)

    # dump json to file for debugging
    with open("stm_debug.json", "w") as f:
        json.dump(stm_json, f, indent=4)

    status = _parse_status_json(stm_json)

    print(status)
