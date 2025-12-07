from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DEFAULT_DAYS,
    DOMAIN,
    CONF_SLUG,
    CONF_APIKEY,
    CONF_DAYS,
)


async def _slug_exists(hass: HomeAssistant, slug: str) -> bool:
    """Check if a config entry already exists for this slug."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_SLUG) == slug:
            return True
    return False


class MasjidBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MasjidBox."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            slug = user_input.get(CONF_SLUG, "").strip()
            apikey = user_input.get(CONF_APIKEY, "").strip()
            days = user_input.get(CONF_DAYS, DEFAULT_DAYS)

            if not slug:
                errors["base"] = "slug_required"
            elif not apikey:
                errors["base"] = "apikey_required"
            elif await _slug_exists(self.hass, slug):
                errors["base"] = "already_configured"
            else:
                # Use slug-based unique ID
                unique_id = f"{DOMAIN}_{slug}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                data = {
                    CONF_SLUG: slug,
                    CONF_APIKEY: apikey,
                    CONF_API_KEY: apikey,  # for compatibility with __init__.py import
                    CONF_DAYS: days,
                }

                return self.async_create_entry(
                    title=f"MasjidBox - {slug}",
                    data=data,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SLUG): str,
                vol.Required(CONF_APIKEY): str,
                vol.Optional(CONF_DAYS, default=DEFAULT_DAYS): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
