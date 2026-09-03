from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.mock_data import find_partner_input, get_all_partner_inputs
from app.scoring import (
    RiskScoreResult,
    assess_partner_risk,
    rank_partner_risks,
    risk_snapshot_payload,
)


TOOL_NAMES = [
    "assess_partner",
    "rank_partners",
    "explain_partner_score",
    "generate_weekly_report",
]


def _today_or_report_date(report_date: str = "") -> date:
    cleaned_report_date = (
        report_date.strip()
        .replace("–", "-")
        .replace("—", "-")
        .replace("-", "-")
    )

    if not cleaned_report_date:
        return date.today()

    try:
        return datetime.strptime(cleaned_report_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"report_date must use YYYY-MM-DD format. Received: {report_date!r}"
        ) from exc


def _result_to_dict(result: RiskScoreResult) -> dict[str, Any]:
    return {
        "partner_name": result.partner_name,
        "ticker": result.ticker,
        "cik": result.cik,
        "risk_score": result.risk_score,
        "risk_band": result.risk_band,
        "ranking_position": result.ranking_position,
        "main_risk_driver": result.main_risk_driver,
        "summary": result.summary,
        "components": [asdict(component) for component in result.components],
        "evidence": result.evidence,
    }


def _ranked_table(results: list[RiskScoreResult]) -> list[dict[str, Any]]:
    return [
        {
            "rank": result.ranking_position,
            "partner_name": result.partner_name,
            "ticker": result.ticker,
            "risk_score": result.risk_score,
            "risk_band": result.risk_band,
            "main_risk_driver": result.main_risk_driver,
        }
        for result in results
    ]


def _risk_counts(results: list[RiskScoreResult]) -> dict[str, int]:
    return {
        "high_risk_count": sum(1 for result in results if result.risk_band == "High"),
        "medium_risk_count": sum(1 for result in results if result.risk_band == "Medium"),
        "low_risk_count": sum(1 for result in results if result.risk_band == "Low"),
    }


def _partners_without_sec_coverage() -> list[str]:
    """
    Phase 8 local assumption.

    You confirmed that all imported partners have SEC coverage, so this returns
    an empty list for the current project dataset.
    """

    return []


def _build_email_body(report_date_value: date, results: list[RiskScoreResult]) -> str:
    counts = _risk_counts(results)
    high_risk = [result for result in results if result.risk_band == "High"]
    without_sec = _partners_without_sec_coverage()

    ranked_lines = [
        f"{result.ranking_position}. {result.partner_name} ({result.ticker}) "
        f"- {result.risk_score}/100 - {result.risk_band} "
        f"- Main driver: {result.main_risk_driver}"
        for result in results
    ]

    high_risk_lines = [
        f"- {result.partner_name} ({result.ticker}): {result.risk_score}/100"
        for result in high_risk
    ]

    without_sec_lines = [f"- {partner_name}" for partner_name in without_sec] or [
        "- None. All listed partners currently have SEC coverage."
    ]

    action_lines = [
        "- Review high-risk partners with procurement and supply chain owners.",
        "- Check whether critical or partial single-source dependencies need mitigation plans.",
        "- Review high-exposure partners for alternate suppliers or contract protections.",
        "- Re-run the report after major quarterly filings are available.",
    ]

    return "\n".join(
        [
            f"Orion Devices Weekly Partner Risk Report",
            f"Report date: {report_date_value.isoformat()}",
            "",
            "Summary",
            f"- Partners scored: {len(results)}",
            f"- High risk: {counts['high_risk_count']}",
            f"- Medium risk: {counts['medium_risk_count']}",
            f"- Low risk: {counts['low_risk_count']}",
            f"- Partners without SEC coverage: {len(without_sec)}",
            "",
            "Ranked partner table",
            *ranked_lines,
            "",
            "High-risk partners",
            *(high_risk_lines or ["- None"]),
            "",
            "Partners without SEC coverage",
            *without_sec_lines,
            "",
            "Recommended review actions",
            *action_lines,
        ]
    )


def register_mcp_tools(mcp: FastMCP) -> None:
    """
    Register exactly the four approved MCP tools.
    """

    @mcp.tool()
    def assess_partner(partner_name: str) -> dict[str, Any]:
        """
        Assess one Orion Devices partner by name or ticker and return its risk score,
        risk band, main risk driver, component scores, and Risk Snapshot-style payload.
        """

        partner = find_partner_input(partner_name)

        if partner is None:
            return {
                "found": False,
                "message": f"Partner '{partner_name}' was not found in the Orion Devices partner list.",
            }

        result = assess_partner_risk(partner)

        return {
            "found": True,
            "assessment": _result_to_dict(result),
            "risk_snapshot_payload": risk_snapshot_payload(result),
        }

    @mcp.tool()
    def rank_partners() -> dict[str, Any]:
        """
        Rank all Orion Devices partners from highest risk to lowest risk.
        """

        results = rank_partner_risks(get_all_partner_inputs())

        return {
            "number_of_partners_scored": len(results),
            "partners_without_sec_coverage": _partners_without_sec_coverage(),
            "ranking": _ranked_table(results),
            "details": [_result_to_dict(result) for result in results],
        }

    @mcp.tool()
    def explain_partner_score(partner_name: str) -> dict[str, Any]:
        """
        Explain why a partner received its risk score and identify the main risk drivers.
        """

        partner = find_partner_input(partner_name)

        if partner is None:
            return {
                "found": False,
                "message": f"Partner '{partner_name}' was not found in the Orion Devices partner list.",
            }

        result = assess_partner_risk(partner)

        return {
            "found": True,
            "partner_name": result.partner_name,
            "ticker": result.ticker,
            "risk_score": result.risk_score,
            "risk_band": result.risk_band,
            "main_risk_driver": result.main_risk_driver,
            "summary": result.summary,
            "component_explanations": [
                {
                    "component": component.name,
                    "score": component.score,
                    "max_score": component.max_score,
                    "explanation": component.explanation,
                }
                for component in result.components
            ],
        }

    @mcp.tool()
    def generate_weekly_report(report_date: str = "") -> dict[str, Any]:
        """
        Generate the current weekly partner risk report content.

        This Phase 8 version returns the report payload and email body. It does not
        create Dataverse Weekly Report records or send Outlook email yet.
        """

        report_date_value = _today_or_report_date(report_date)
        results = rank_partner_risks(get_all_partner_inputs(), as_of=report_date_value)
        counts = _risk_counts(results)
        without_sec = _partners_without_sec_coverage()

        report_summary = (
            f"{len(results)} partners were scored. "
            f"{counts['high_risk_count']} are High risk, "
            f"{counts['medium_risk_count']} are Medium risk, and "
            f"{counts['low_risk_count']} are Low risk. "
            f"{len(without_sec)} partners are without SEC coverage."
        )

        return {
            "report_date": report_date_value.isoformat(),
            "number_of_partners_scored": len(results),
            **counts,
            "partners_without_sec_coverage": without_sec,
            "ranked_partner_table": _ranked_table(results),
            "high_risk_partners": [
                item for item in _ranked_table(results) if item["risk_band"] == "High"
            ],
            "report_summary": report_summary,
            "recommended_review_actions": [
                "Review high-risk partners with procurement and supply chain owners.",
                "Check critical or partial single-source dependencies for mitigation plans.",
                "Review high-exposure partners for alternate suppliers or contract protections.",
                "Re-run the report after major quarterly filings are available.",
            ],
            "email_subject": f"Orion Devices Weekly Partner Risk Report - {report_date_value.isoformat()}",
            "email_body": _build_email_body(report_date_value, results),
            "email_sent": False,
        }