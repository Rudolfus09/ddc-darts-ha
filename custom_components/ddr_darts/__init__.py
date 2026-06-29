import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_TOKEN, CONF_LIGHTS, CONF_FLASH_DURATION, DEFAULT_FLASH_DURATION
from .coordinator import DDRDartsCoordinator
from .light_controller import LightController

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    token = entry.data[CONF_TOKEN]
    lights = entry.options.get(CONF_LIGHTS, [])
    duration = entry.options.get(CONF_FLASH_DURATION, DEFAULT_FLASH_DURATION)

    coordinator = DDRDartsCoordinator(hass, token)
    controller = LightController(hass, lights, duration)

    async def _on_update():
        events = coordinator.data.get("events", []) if coordinator.data else []
        for event in events:
            rgb = event.get("rgb")
            if rgb:
                _LOGGER.info("DDR Darts event: %s by %s → color %s", event.get("event_type"), event.get("player"), rgb)
                hass.async_create_task(controller.flash_color(rgb))

    coordinator.async_add_listener(_on_update)

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "controller": controller,
    }

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    lights = entry.options.get(CONF_LIGHTS, [])
    duration = entry.options.get(CONF_FLASH_DURATION, DEFAULT_FLASH_DURATION)
    data = hass.data[DOMAIN].get(entry.entry_id)
    if data and "controller" in data:
        data["controller"].update_config(lights, duration)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
