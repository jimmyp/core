"""Test the Genio IR remote."""


# from unittest.mock import MagicMock , patch
# import pytest

from tuya_iot import AuthType

from homeassistant.components.tuya.const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_AUTH_TYPE,
    CONF_ENDPOINT,
    DOMAIN,
)
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

# @pytest.fixture(name="tuya")
# def tuya_fixture() -> MagicMock:
#     """Patch libraries."""
#     with patch("homeassistant.components.tuya.config_flow.TuyaOpenAPI") as tuya:
#         yield tuya


# @pytest.fixture(name="tuya_setup", autouse=True)
# def tuya_setup_fixture() -> None:
#     """Mock tuya entry setup."""
#     with patch("homeassistant.components.tuya.async_setup_entry", return_value=True):
#         yield


# @pytest.mark.parametrize(
#     ("app_type", "side_effects", "project_type"),
#     [
#         ("", [RESPONSE_SUCCESS], 1),
#         (TUYA_SMART_APP, [RESPONSE_ERROR, RESPONSE_SUCCESS], 0),
#         (SMARTLIFE_APP, [RESPONSE_ERROR, RESPONSE_ERROR, RESPONSE_SUCCESS], 0),
#     ],
# )


async def test_entity_registration(
    hass: HomeAssistant,
    # tuya: MagicMock,
    # app_type: str,
    # side_effects: list[dict[str, Any]],
) -> None:
    """Ensure entity is added."""

    # tuya().connect = MagicMock(side_effect=side_effects)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_TYPE: AuthType.SMART_HOME,
            CONF_ENDPOINT: "",
            CONF_ACCESS_ID: "",
            CONF_ACCESS_SECRET: "",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # mocks start with current activity == Watch TV
    remote = hass.states.get("remote.<name>")
    assert remote is not None
