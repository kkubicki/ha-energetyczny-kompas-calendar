from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType

from custom_components.energetyczny_kompas.config_flow import (
    EnergetycznyKompasConfigFlow,
)


@pytest.mark.asyncio
async def test_config_flow_form() -> None:
    """Test initial form is shown when user_input is None."""
    flow = EnergetycznyKompasConfigFlow()
    flow.hass = MagicMock()

    with patch.object(flow, "_async_current_entries", return_value=[]):
        result = await flow.async_step_user(user_input=None)
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_config_flow_create_entry() -> None:
    """Test entry is created when user_input is provided."""
    flow = EnergetycznyKompasConfigFlow()
    flow.hass = MagicMock()

    with patch.object(flow, "_async_current_entries", return_value=[]):
        result = await flow.async_step_user(user_input={})
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Energetyczny Kompas Calendar"


@pytest.mark.asyncio
async def test_config_flow_single_instance_abort() -> None:
    """Test flow aborts if an entry already exists."""
    flow = EnergetycznyKompasConfigFlow()
    flow.hass = MagicMock()

    with patch.object(flow, "_async_current_entries", return_value=["existing_entry"]):
        result = await flow.async_step_user(user_input=None)
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "single_instance_allowed"
