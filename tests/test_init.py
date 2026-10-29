from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.energetyczny_kompas import (
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)


@pytest.mark.asyncio
async def test_async_setup_and_unload_entry() -> None:
    """Test setting up and unloading config entry."""
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    entry = MagicMock()

    setup_result = await async_setup_entry(hass, entry)
    assert setup_result is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, PLATFORMS
    )

    unload_result = await async_unload_entry(hass, entry)
    assert unload_result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry, PLATFORMS
    )

