import logging
import aiohttp
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DEFAULT_API_URL, DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


class DDRDartsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, token: str):
        super().__init__(
            hass,
            _LOGGER,
            name="DDC Darts",
            update_interval=timedelta(seconds=DEFAULT_POLL_INTERVAL),
        )
        self._token = token
        self._last_id = 0

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{DEFAULT_API_URL}?action=ha_events&token={self._token}&last_id={self._last_id}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 401:
                        _LOGGER.error("DDC Darts: Ungültiger Token")
                        return {"events": [], "error": "invalid_token"}
                    data = await resp.json()
        except Exception as err:
            _LOGGER.warning("DDC Darts: API-Fehler: %s", err)
            return {"events": [], "error": str(err)}

        events = data.get("events", [])
        if events:
            self._last_id = max(e["id"] for e in events)

        return {"events": events, "error": None}
