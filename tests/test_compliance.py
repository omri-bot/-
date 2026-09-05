from tools.core import compliance


def test_personal_attribution_is_blocked():
    report = compliance.check_text("אתה סובל מכאבי גב? יש פתרון", "meta")
    assert report.blocked
    assert any(f.rule_id == "personal_attribution" for f in report.findings)


def test_guaranteed_results_is_blocked():
    assert compliance.check_text("תוצאות מובטחות תוך חודש").blocked


def test_compliant_copy_passes():
    text = "אימון של 30 דקות, שלוש פעמים בשבוע. בבית, בלי ציוד."
    assert not compliance.check_text(text, "meta").blocked


def test_superlative_only_warns():
    report = compliance.check_text("המוביל בישראל בתחומו", "meta")
    assert not report.blocked
    assert report.warnings


def test_platform_scoped_rule_does_not_leak():
    text = "דרושים מפתחים עד גיל 30"
    assert compliance.check_text(text, "linkedin").blocked
    assert not compliance.check_text(text, "tiktok").blocked


def test_field_length_limit():
    report = compliance.check_fields({"headline": "א" * 80}, "meta")
    assert report.blocked
    assert any(f.rule_id == "field_length" for f in report.findings)
