"""Config flow for Utility Meter integration."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta
from typing import Any, cast

import voluptuous as vol

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
)

from .const import (
    BIMONTHLY,
    CONF_METER_DELTA_VALUES,
    CONF_METER_NET_CONSUMPTION,
    CONF_METER_OFFSET,
    CONF_METER_PERIODICALLY_RESETTING,
    CONF_METER_TYPE,
    CONF_SENSOR_ALWAYS_AVAILABLE,
    CONF_SOURCE_SENSOR,
    CONF_TARIFFS,
    DAILY,
    DOMAIN,
    EVERY_FIVE_MINUTES,
    HALF_HOURLY,
    HALF_YEARLY,
    HOURLY,
    MONTHLY,
    QUARTER_HOURLY,
    QUARTERLY,
    WEEKLY,
    YEARLY,
)

METER_TYPES = [
    "none",
    EVERY_FIVE_MINUTES,
    QUARTER_HOURLY,
    HALF_HOURLY,
    HOURLY,
    DAILY,
    WEEKLY,
    MONTHLY,
    BIMONTHLY,
    QUARTERLY,
    HALF_YEARLY,
    YEARLY,
]


async def _validate_config(
    handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Validate config."""
    try:
        vol.Unique()(user_input[CONF_TARIFFS])
    except vol.Invalid as exc:
        raise SchemaFlowError("tariffs_not_unique") from exc
    offset_timedelta = timedelta(seconds=0)
    try:
        offset_timedelta = timedelta(seconds = user_input[CONF_METER_OFFSET]["seconds"] + \
            user_input[CONF_METER_OFFSET]["minutes"] * 60 + \
            user_input[CONF_METER_OFFSET]["hours"] * 3600 + \
            user_input[CONF_METER_OFFSET]["days"] * 86400)
    except vol.Invalid as exc:
        raise SchemaFlowError("invalid_meter_offset") from exc
    if user_input[CONF_METER_TYPE] == EVERY_FIVE_MINUTES:
        if offset_timedelta >= timedelta(minutes=5):
            raise SchemaFlowError(
                f"Offset for {CONF_METER_TYPE} must be less than 5 minutes"
            )
    elif user_input[CONF_METER_TYPE] == QUARTER_HOURLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(minutes=15):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 15 minutes"
            )
    elif user_input[CONF_METER_TYPE] == HALF_HOURLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(minutes=30):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 30 minutes"
            )
    elif user_input[CONF_METER_TYPE] == HOURLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(hours=1):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 1 hour"
            )
    elif user_input[CONF_METER_TYPE] == DAILY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=1):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 1 day"
            )
    elif user_input[CONF_METER_TYPE] == WEEKLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(weeks=1):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 1 week"
            )
    elif user_input[CONF_METER_TYPE] == MONTHLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=28):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 31 days"
            )
    elif user_input[CONF_METER_TYPE] == BIMONTHLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=59):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 59 days"
            )
    elif user_input[CONF_METER_TYPE] == QUARTERLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=90):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 90 days"
            )
    elif user_input[CONF_METER_TYPE] == HALF_YEARLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=183):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 183 days"
            )
    elif user_input[CONF_METER_TYPE] == YEARLY:
        if user_input[CONF_METER_OFFSET] >= timedelta(days=365):
            raise vol.Invalid(
                f"Offset for {CONF_METER_TYPE} must be less than 365 days"
            )
    return user_input


OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SENSOR_DOMAIN),
        ),
        vol.Required(
            CONF_METER_PERIODICALLY_RESETTING,
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_SENSOR_ALWAYS_AVAILABLE,
            default=False,
        ): selector.BooleanSelector(),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SENSOR_DOMAIN),
        ),
        vol.Required(CONF_METER_TYPE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=METER_TYPES, translation_key=CONF_METER_TYPE
            ),
        ),
        vol.Required(CONF_METER_OFFSET, default=None): selector.DurationSelector(
            selector.DurationSelectorConfig(
                enable_day= True,
                enable_millisecond=False,
                allow_negative=False,
            ),
        ),
        vol.Required(CONF_TARIFFS, default=[]): selector.SelectSelector(
            selector.SelectSelectorConfig(options=[], custom_value=True, multiple=True),
        ),
        vol.Required(
            CONF_METER_NET_CONSUMPTION, default=False
        ): selector.BooleanSelector(),
        vol.Required(
            CONF_METER_DELTA_VALUES, default=False
        ): selector.BooleanSelector(),
        vol.Required(
            CONF_METER_PERIODICALLY_RESETTING,
            default=True,
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_SENSOR_ALWAYS_AVAILABLE,
            default=False,
        ): selector.BooleanSelector(),
    }
)

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, validate_user_input=_validate_config)
}

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Utility Meter."""

    VERSION = 3

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return cast(str, options[CONF_NAME])
