from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import json
from typing import Optional


LOW_MAX = 30
MEDIUM_MAX = 60


@dataclass
class SECFinancialMetrics:
    """
    Already-extracted SEC metrics used by the risk scoring logic.

    Phase 7 does not fetch SEC data directly. Later phases will populate these
    values from the SEC Submissions API and SEC Company Facts API.
    """

    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_yoy_change: Optional[float] = None

    latest_10k_filing_date: Optional[str] = None
    latest_10q_filing_date: Optional[str] = None

    available_concepts: list[str] = field(default_factory=list)
    missing_concepts: list[str] = field(default_factory=list)


@dataclass
class PartnerRiskInput:
    """
    Internal partner data plus extracted SEC metrics.

    This mirrors the data we will later combine from Dataverse and SEC EDGAR.
    """

    partner_name: str
    ticker: str
    cik: str
    annual_spend_or_exposure: float
    business_criticality: str
    single_source_dependency: str
    sec_metrics: SECFinancialMetrics


@dataclass
class ScoreComponent:
    name: str
    score: int
    max_score: int
    explanation: str


@dataclass
class RiskScoreResult:
    partner_name: str
    ticker: str
    cik: str
    risk_score: int
    risk_band: str
    ranking_position: Optional[int]
    main_risk_driver: str
    summary: str
    components: list[ScoreComponent]
    evidence: dict


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def risk_band(score: int) -> str:
    if score <= LOW_MAX:
        return "Low"
    if score <= MEDIUM_MAX:
        return "Medium"
    return "High"


def score_current_ratio(value: Optional[float]) -> tuple[int, str]:
    if value is None:
        return 6, "Current ratio unavailable; moderate liquidity uncertainty added."
    if value < 1.0:
        return 10, "Current ratio below 1.0 indicates weak short-term liquidity."
    if value < 1.5:
        return 6, "Current ratio between 1.0 and 1.5 indicates moderate liquidity risk."
    if value < 2.5:
        return 3, "Current ratio is acceptable."
    return 1, "Current ratio is strong."


def score_debt_to_equity(value: Optional[float]) -> tuple[int, str]:
    if value is None:
        return 6, "Debt-to-equity unavailable; moderate leverage uncertainty added."
    if value < 0:
        return 10, "Debt-to-equity is negative, indicating possible balance-sheet stress."
    if value > 3.0:
        return 10, "Debt-to-equity above 3.0 indicates high leverage risk."
    if value > 1.5:
        return 7, "Debt-to-equity above 1.5 indicates elevated leverage risk."
    if value > 0.75:
        return 4, "Debt-to-equity is moderate."
    return 1, "Debt-to-equity is low."


def score_profit_margin(value: Optional[float]) -> tuple[int, str]:
    if value is None:
        return 5, "Profit margin unavailable; moderate profitability uncertainty added."
    if value < 0:
        return 8, "Negative profit margin indicates profitability risk."
    if value < 0.05:
        return 5, "Profit margin below 5% indicates modest profitability."
    if value < 0.15:
        return 2, "Profit margin is acceptable."
    return 1, "Profit margin is strong."


def score_revenue_trend(value: Optional[float]) -> tuple[int, str]:
    if value is None:
        return 4, "Revenue trend unavailable; moderate growth uncertainty added."
    if value < -0.10:
        return 7, "Revenue declined by more than 10% year over year."
    if value < 0:
        return 5, "Revenue declined year over year."
    if value < 0.05:
        return 3, "Revenue growth is flat to modest."
    return 1, "Revenue growth is positive."


def score_sec_financial_health(metrics: SECFinancialMetrics) -> ScoreComponent:
    """
    SEC financial health contributes up to 35 points.

    Higher score means higher risk.
    """

    current_score, current_reason = score_current_ratio(metrics.current_ratio)
    leverage_score, leverage_reason = score_debt_to_equity(metrics.debt_to_equity)
    margin_score, margin_reason = score_profit_margin(metrics.profit_margin)
    revenue_score, revenue_reason = score_revenue_trend(metrics.revenue_yoy_change)

    total = current_score + leverage_score + margin_score + revenue_score
    total = clamp(total, 0, 35)

    explanation = " ".join(
        [
            current_reason,
            leverage_reason,
            margin_reason,
            revenue_reason,
        ]
    )

    return ScoreComponent(
        name="SEC financial health indicators",
        score=total,
        max_score=35,
        explanation=explanation,
    )


def score_annual_spend_or_exposure(value: float) -> ScoreComponent:
    """
    Internal annual spend/exposure contributes up to 20 points.

    These thresholds are intentionally simple and transparent for a portfolio demo.
    """

    if value >= 800_000:
        score = 20
        explanation = "Annual spend/exposure is very high."
    elif value >= 600_000:
        score = 15
        explanation = "Annual spend/exposure is high."
    elif value >= 400_000:
        score = 10
        explanation = "Annual spend/exposure is moderate."
    elif value > 0:
        score = 5
        explanation = "Annual spend/exposure is low to moderate."
    else:
        score = 2
        explanation = "Annual spend/exposure is missing or zero."

    return ScoreComponent(
        name="Internal annual spend or exposure",
        score=score,
        max_score=20,
        explanation=explanation,
    )


def score_business_criticality(value: str) -> ScoreComponent:
    """
    Business criticality contributes up to 20 points.
    """

    normalized = value.strip().lower()

    if normalized == "critical":
        score = 20
        explanation = "Partner is marked Critical to Orion Devices."
    elif normalized == "high":
        score = 15
        explanation = "Partner has High business criticality."
    elif normalized == "medium":
        score = 8
        explanation = "Partner has Medium business criticality."
    elif normalized == "low":
        score = 3
        explanation = "Partner has Low business criticality."
    else:
        score = 10
        explanation = f"Business criticality value '{value}' is not recognized; moderate risk assigned."

    return ScoreComponent(
        name="Business criticality",
        score=score,
        max_score=20,
        explanation=explanation,
    )


def score_single_source_dependency(value: str) -> ScoreComponent:
    """
    Single-source dependency contributes up to 15 points.
    """

    normalized = value.strip().lower()

    if normalized == "yes":
        score = 15
        explanation = "Partner is a full single-source dependency."
    elif normalized == "partial":
        score = 8
        explanation = "Partner has partial single-source dependency."
    elif normalized == "no":
        score = 0
        explanation = "Partner is not a single-source dependency."
    else:
        score = 8
        explanation = f"Single-source dependency value '{value}' is not recognized; partial dependency risk assigned."

    return ScoreComponent(
        name="Single-source dependency",
        score=score,
        max_score=15,
        explanation=explanation,
    )


def latest_filing_date(metrics: SECFinancialMetrics) -> Optional[date]:
    filing_dates = [
        parse_iso_date(metrics.latest_10k_filing_date),
        parse_iso_date(metrics.latest_10q_filing_date),
    ]
    valid_dates = [item for item in filing_dates if item is not None]

    if not valid_dates:
        return None

    return max(valid_dates)


def score_filing_freshness(metrics: SECFinancialMetrics, as_of: date) -> tuple[int, str]:
    latest_date = latest_filing_date(metrics)

    if latest_date is None:
        return 5, "No recent 10-K or 10-Q filing date was available."

    age_days = (as_of - latest_date).days

    if age_days <= 120:
        return 0, f"Latest SEC filing is fresh at {age_days} days old."
    if age_days <= 240:
        return 2, f"Latest SEC filing is somewhat recent at {age_days} days old."
    if age_days <= 450:
        return 4, f"Latest SEC filing is aging at {age_days} days old."

    return 5, f"Latest SEC filing is stale at {age_days} days old."


def score_sec_completeness_and_freshness(
    metrics: SECFinancialMetrics,
    as_of: Optional[date] = None,
) -> ScoreComponent:
    """
    SEC data completeness and filing freshness contributes up to 10 points.

    Completeness: up to 5 points.
    Filing freshness: up to 5 points.
    """

    if as_of is None:
        as_of = date.today()

    available_count = len(metrics.available_concepts)
    missing_count = len(metrics.missing_concepts)
    total_checked = available_count + missing_count

    if total_checked == 0:
        completeness_score = 3
        completeness_reason = "No concept availability check was provided; moderate data completeness uncertainty added."
    else:
        missing_ratio = missing_count / total_checked
        completeness_score = round(missing_ratio * 5)
        completeness_reason = (
            f"{available_count} checked financial concepts were available and "
            f"{missing_count} were missing."
        )

    freshness_score, freshness_reason = score_filing_freshness(metrics, as_of)

    total = clamp(completeness_score + freshness_score, 0, 10)

    return ScoreComponent(
        name="SEC data completeness and filing freshness",
        score=total,
        max_score=10,
        explanation=f"{completeness_reason} {freshness_reason}",
    )


def find_main_risk_driver(components: list[ScoreComponent]) -> str:
    """
    Select the component with the highest proportion of its maximum score.
    """

    if not components:
        return "No risk drivers available."

    highest = max(components, key=lambda item: item.score / item.max_score)
    return highest.name


def build_summary(
    partner: PartnerRiskInput,
    score: int,
    band: str,
    main_driver: str,
    components: list[ScoreComponent],
) -> str:
    component_text = "; ".join(
        f"{component.name}: {component.score}/{component.max_score}"
        for component in components
    )

    return (
        f"{partner.partner_name} is rated {band} risk with a score of {score}/100. "
        f"The main risk driver is {main_driver}. "
        f"Component scores: {component_text}."
    )


def assess_partner_risk(
    partner: PartnerRiskInput,
    as_of: Optional[date] = None,
) -> RiskScoreResult:
    """
    Calculate the transparent 0-100 risk score for one partner.
    """

    components = [
        score_sec_financial_health(partner.sec_metrics),
        score_annual_spend_or_exposure(partner.annual_spend_or_exposure),
        score_business_criticality(partner.business_criticality),
        score_single_source_dependency(partner.single_source_dependency),
        score_sec_completeness_and_freshness(partner.sec_metrics, as_of=as_of),
    ]

    total_score = clamp(sum(component.score for component in components), 0, 100)
    band = risk_band(total_score)
    main_driver = find_main_risk_driver(components)
    summary = build_summary(partner, total_score, band, main_driver, components)

    evidence = {
        "partner": {
            "partner_name": partner.partner_name,
            "ticker": partner.ticker,
            "cik": partner.cik,
            "annual_spend_or_exposure": partner.annual_spend_or_exposure,
            "business_criticality": partner.business_criticality,
            "single_source_dependency": partner.single_source_dependency,
        },
        "sec_metrics": asdict(partner.sec_metrics),
        "component_scores": [asdict(component) for component in components],
    }

    return RiskScoreResult(
        partner_name=partner.partner_name,
        ticker=partner.ticker,
        cik=partner.cik,
        risk_score=total_score,
        risk_band=band,
        ranking_position=None,
        main_risk_driver=main_driver,
        summary=summary,
        components=components,
        evidence=evidence,
    )


def rank_partner_risks(
    partners: list[PartnerRiskInput],
    as_of: Optional[date] = None,
) -> list[RiskScoreResult]:
    """
    Score and rank partners from highest risk to lowest risk.
    """

    results = [assess_partner_risk(partner, as_of=as_of) for partner in partners]
    results.sort(key=lambda item: item.risk_score, reverse=True)

    for index, result in enumerate(results, start=1):
        result.ranking_position = index

    return results


def evidence_json(result: RiskScoreResult) -> str:
    """
    Format evidence for the Dataverse Evidence JSON multiline text column.
    """

    return json.dumps(result.evidence, indent=2, sort_keys=True)


def risk_snapshot_payload(result: RiskScoreResult, score_date: Optional[date] = None) -> dict:
    """
    Create a dictionary shaped like the future Risk Snapshot row.

    This does not write to Dataverse. Dataverse writing comes later.
    """

    if score_date is None:
        score_date = date.today()

    return {
        "Score Date": score_date.isoformat(),
        "Risk Score": result.risk_score,
        "Risk Band": result.risk_band,
        "Ranking Position": result.ranking_position,
        "Main Risk Driver": result.main_risk_driver,
        "Summary": result.summary,
        "Evidence JSON": evidence_json(result),
    }