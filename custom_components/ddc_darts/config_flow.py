import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, DEFAULT_API_URL, CONF_TOKEN, CONF_LIGHTS


class DDCDartsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._token = None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            valid = await self._validate_token(token)
            if valid:
                self._token = token
                return await self.async_step_lights()
            errors["base"] = "invalid_token"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )

    async def async_step_lights(self, user_input=None):
        if user_input is not None:
            await self._register_connection(user_input.get(CONF_LIGHTS, []))
            return self.async_create_entry(
                title="DDC Darts",
                data={CONF_TOKEN: self._token},
                options={CONF_LIGHTS: user_input.get(CONF_LIGHTS, [])},
            )

        return self.async_show_form(
            step_id="lights",
            data_schema=vol.Schema({
                vol.Required(CONF_LIGHTS): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
            }),
        )

    async def _validate_token(self, token: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{DEFAULT_API_URL}?action=ha_events&token={token}&last_id=0",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 401:
                        return False
                    data = await resp.json()
                    return "events" in data
        except Exception:
            return False

    async def _register_connection(self, lights: list):
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{DEFAULT_API_URL}?action=ha_register&token={self._token}",
                    json={"lights": lights, "version": "1.0.0"},
                    timeout=aiohttp.ClientTimeout(total=10),
                )
        except Exception:
            pass

    @staticmethod
    def async_get_options_flow(config_entry):
        return DDCDartsOptionsFlow(config_entry)


class DDCDartsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self._config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_LIGHTS, default=current.get(CONF_LIGHTS, [])): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
            }),
        )
