import asyncio
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class LightController:

    def __init__(self, hass: HomeAssistant, light_entities: list[str]):
        self._hass = hass
        self._lights = light_entities
        self._active = False

    def update_config(self, light_entities: list[str]):
        self._lights = light_entities

    async def flash_color(self, rgb: list[int], duration: int = 10):
        if not self._lights or not rgb or len(rgb) != 3:
            return

        if self._active:
            _LOGGER.debug("Flash already active, skipping")
            return

        self._active = True
        try:
            await self._hass.services.async_call("scene", "create", {
                "scene_id": "ddc_darts_restore",
                "snapshot_entities": self._lights,
            })
            await asyncio.sleep(0.3)

            for entity_id in self._lights:
                await self._hass.services.async_call("light", "turn_on", {
                    "entity_id": entity_id,
                    "rgb_color": rgb,
                    "brightness": 255,
                })

            await asyncio.sleep(duration)

            await self._hass.services.async_call("scene", "turn_on", {
                "entity_id": "scene.ddc_darts_restore",
            })

        except Exception as err:
            _LOGGER.error("DDC Darts flash error: %s", err)
        finally:
            self._active = False
