from datetime import date

import pytest

from tools.core import approvals, config, paths, schedule
from tools.platforms import SUPPORTED, get_platform

CLIENT = "example-fitlab"


def test_template_is_not_listed_as_a_client():
    assert paths.TEMPLATE not in paths.client_slugs()
    assert CLIENT in paths.client_slugs()


def test_client_has_both_offering_types():
    types = set()
    for offering in paths.offerings(CLIENT):
        text = (offering / "offering.md").read_text(encoding="utf-8")
        types.add("service" if "type: service" in text else "product")
    assert types == {"product", "service"}


def test_due_uses_client_cadence():
    items = schedule.due(today=date(2026, 9, 5))
    assert any(i.client == CLIENT for i in items)  # last report 2026-09-01, cadence 3d
    assert not schedule.due(today=date(2026, 9, 2))


@pytest.mark.parametrize("name", SUPPORTED)
def test_every_platform_implements_the_interface(name):
    platform = get_platform(name, CLIENT)
    campaign = paths.campaign(CLIENT, "2026-Q1-coaching-leads")
    payload = platform.build_payload(campaign)
    # each network names it differently; the invariant is that nothing starts live
    paused = payload.get("status") or payload.get("operation_status")
    assert paused in ("PAUSED", "DISABLE")


def test_draft_with_violating_copy_is_refused(tmp_path):
    campaign = paths.campaign(CLIENT, "2026-Q1-coaching-leads")
    platform = get_platform("meta", CLIENT)
    with pytest.raises(approvals.ComplianceFailure):
        platform.draft_campaign(campaign, rationale="test", primary_text="אתה סובל מכאבי גב?")


def test_live_writes_are_off_by_default():
    assert not config.live_writes_allowed()
