"""Entry point for the agents' real actions.

    python -m tools.cli clients
    python -m tools.cli due
    python -m tools.cli check --platform meta --file <path>
    python -m tools.cli insights --client <slug> --campaign <slug>
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from .core import compliance, config, paths, schedule


def cmd_clients(args: argparse.Namespace) -> int:
    slugs = paths.client_slugs()
    if not slugs:
        print("אין לקוחות. פתח לקוח: cp -r clients/_template clients/<slug>")
        return 0
    for slug in slugs:
        cfg = config.client(slug)
        active = ", ".join(config.active_platforms(slug)) or "—"
        offers = [p.name for p in paths.offerings(slug)]
        print(f"{slug}  ({cfg.get('name', '')})  status={cfg.get('status')}")
        print(f"  רשתות פעילות: {active}")
        print(f"  הצעות: {', '.join(offers) or '—'}")
        print(f"  קמפיינים: {len(paths.campaigns(slug))}")
    return 0


def cmd_due(args: argparse.Namespace) -> int:
    items = schedule.due()
    if not items:
        print("אין קמפיינים שמחכים לסבב אופטימיזציה.")
        return 0
    print("קמפיינים שהגיע להם סבב אופטימיזציה:\n")
    for item in items:
        print(f"  {item.client} / {item.campaign}")
        print(f"    קצב: {item.cadence} | {item.reason}")
        if item.min_spend:
            print(
                f"    ⚠ ודא הוצאה ≥ {item.min_spend} ₪ מאז הדוח האחרון לפני שמריצים"
            )
    print("\nהשלב הבא: הפעל את analyst על כל אחד. ראה policies/optimization-loop.md")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
    if not text:
        print("צריך --file או --text", file=sys.stderr)
        return 2
    report = compliance.check_text(text, args.platform)
    if not report.findings:
        print("✓ עבר — לא נמצאו הפרות")
        return 0
    for finding in report.findings:
        print(finding)
    if report.blocked:
        print("\n✗ נחסם. תקן את הניסוח — ראה policies/compliance.md")
        return 1
    print("\n⚠ עבר עם אזהרות. אדם מכריע.")
    return 0


def cmd_insights(args: argparse.Namespace) -> int:
    from .platforms import get_platform

    campaign = paths.campaign(args.client, args.campaign)
    until = date.today()
    since = until - timedelta(days=args.days)
    platforms = args.platforms or config.active_platforms(args.client)
    if not platforms:
        print(f"אין רשתות פעילות ל-{args.client} (בדוק accounts ב-client.yaml)")
        return 1
    for name in platforms:
        platform = get_platform(name, args.client)
        try:
            rows = platform.read_insights(since, until)
        except NotImplementedError as exc:
            print(f"{name}: {exc}")
            continue
        for row in rows:
            print(f"{name} {row.day} {row.entity_name}: הוצאה {row.spend} המרות {row.conversions}")
    print(f"\nקמפיין: {campaign.path.relative_to(paths.ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("clients", help="רשימת הלקוחות והמצב שלהם").set_defaults(func=cmd_clients)
    sub.add_parser("due", help="לאילו קמפיינים הגיע סבב אופטימיזציה").set_defaults(func=cmd_due)

    check = sub.add_parser("check", help="בדיקת ציות לטקסט לפני שהוא נכתב לטיוטה")
    check.add_argument("--platform", choices=paths.PLATFORMS, default=None)
    check.add_argument("--file")
    check.add_argument("--text")
    check.set_defaults(func=cmd_check)

    insights = sub.add_parser("insights", help="משיכת נתוני ביצועים")
    insights.add_argument("--client", required=True)
    insights.add_argument("--campaign", required=True)
    insights.add_argument("--days", type=int, default=7)
    insights.add_argument("--platforms", nargs="*", choices=paths.PLATFORMS)
    insights.set_defaults(func=cmd_insights)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
