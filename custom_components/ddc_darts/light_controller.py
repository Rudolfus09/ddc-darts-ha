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

    async def execute_effect(self, rgb: list[int] | None, effect: dict):
        if not self._lights:
            return

        if self._active:
            _LOGGER.debug("Effect already active, skipping")
            return

        effect_type = effect.get("effect_type", "solid")
        duration = effect.get("duration", 10)
        brightness = int(effect.get("brightness", 100) * 255 / 100)
        color_mode = effect.get("color_mode", "player")

        if color_mode == "fixed" and effect.get("fixed_color"):
            rgb = self._hex_to_rgb(effect["fixed_color"])

        colors = None
        if effect.get("color_sequence"):
            colors = effect["color_sequence"]

        if effect_type != "off" and not rgb and not colors:
            _LOGGER.warning("No color available for effect")
            return

        self._active = True
        try:
            await self._save_scene()

            if effect_type == "solid":
                await self._effect_solid(rgb, duration, brightness)
            elif effect_type == "blink":
                speed = effect.get("blink_speed_ms", 500) / 1000
                await self._effect_blink(rgb, duration, brightness, speed)
            elif effect_type == "pulse":
                await self._effect_pulse(rgb, duration, brightness)
            elif effect_type == "color_cycle":
                await self._effect_color_cycle(colors or [rgb], duration, brightness)
            elif effect_type == "off":
                await self._effect_off(duration)
            else:
                await self._effect_solid(rgb, duration, brightness)

            await self._restore_scene()

        except Exception as err:
            _LOGGER.error("DDC Darts effect error: %s", err)
        finally:
            self._active = False

    async def _effect_solid(self, rgb, duration, brightness):
        await self._set_lights(rgb, brightness)
        await asyncio.sleep(duration)

    async def _effect_blink(self, rgb, duration, brightness, speed):
        end_time = asyncio.get_event_loop().time() + duration
        on = True
        while asyncio.get_event_loop().time() < end_time:
            if on:
                await self._set_lights(rgb, brightness)
            else:
                await self._turn_off_lights()
            on = not on
            await asyncio.sleep(speed)

    async def _effect_pulse(self, rgb, duration, brightness):
        cycle_time = 2.0
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            await self._set_lights(rgb, brightness, transition=cycle_time / 2)
            await asyncio.sleep(cycle_time / 2)
            if asyncio.get_event_loop().time() >= end_time:
                break
            await self._set_lights(rgb, 1, transition=cycle_time / 2)
            await asyncio.sleep(cycle_time / 2)

    async def _effect_color_cycle(self, colors, duration, brightness):
        if not colors:
            return
        time_per_color = max(1.0, duration / len(colors))
        end_time = asyncio.get_event_loop().time() + duration
        idx = 0
        while asyncio.get_event_loop().time() < end_time:
            color = colors[idx % len(colors)]
            await self._set_lights(color, brightness, transition=0.5)
            await asyncio.sleep(time_per_color)
            idx += 1

    async def _effect_off(self, duration):
        await self._turn_off_lights()
        await asyncio.sleep(duration)

    async def _save_scene(self):
        await self._hass.services.async_call("scene", "create", {
            "scene_id": "ddc_darts_restore",
            "snapshot_entities": self._lights,
        })
        await asyncio.sleep(0.3)

    async def _restore_scene(self):
        await self._hass.services.async_call("scene", "turn_on", {
            "entity_id": "scene.ddc_darts_restore",
        })

    async def _set_lights(self, rgb, brightness, transition=0):
        data = {"brightness": brightness}
        if rgb:
            data["rgb_color"] = rgb
        if transition > 0:
            data["transition"] = transition
        for entity_id in self._lights:
            await self._hass.services.async_call("light", "turn_on", {
                "entity_id": entity_id, **data,
            })

    async def _turn_off_lights(self, transition=0):
        data = {}
        if transition > 0:
            data["transition"] = transition
        for entity_id in self._lights:
            await self._hass.services.async_call("light", "turn_off", {
                "entity_id": entity_id, **data,
            })

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> list[int]:
        h = hex_str.lstrip("#")
        return [int(h[i:i+2], 16) for i in (0, 2, 4)]
