"""Config flow for Cozi component."""
from __future__ import annotations

import asyncio

from cozi import Cozi
from cozi.exceptions import InvalidLoginException

from aiohttp import ClientError
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN, LOGGER

class CoziConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            try:
                async with timeout(10):
                    cozi = Cozi(
                        user_input[CONF_USERNAME],
                        user_input[CONF_PASSWORD],
                    )
                    LOGGER.debug("Logging into Cozi...")
                    await cozi.login()
            except (ClientConnectorError, asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except InvalidLoginException:
                errors[CONF_PASSWORD] = "invalid_auth"
            else:
                await self.async_set_unique_id(
                    user_input[CONF_USERNAME], raise_on_progress=False
                )

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        errors = {}

        if user_input is not None:
            try:
                async with timeout(10):
                    cozi = Cozi(
                        user_input[CONF_USERNAME],
                        user_input[CONF_PASSWORD],
                    )
                    LOGGER.debug("Logging into Cozi...")
                    await cozi.login()
            except (ClientConnectorError, asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except InvalidLoginException:
                errors[CONF_PASSWORD] = "invalid_auth"
            else:
                await self.async_set_unique_id(
                    user_input[CONF_USERNAME], raise_on_progress=False
                )

                self.hass.config_entries.async_update_entry(self.reauth_entry, data=user_input)
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
