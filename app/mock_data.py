from __future__ import annotations

from app.scoring import PartnerRiskInput, SECFinancialMetrics


def build_partner_inputs() -> list[PartnerRiskInput]:
    """
    Local Phase 8 data provider.

    This uses the 10 partner companies imported into Dataverse earlier, but it does
    not connect to Dataverse yet. The SEC metrics are local test values so we can
    test the MCP tool surface before adding real SEC/Dataverse integration.
    """

    return [
        PartnerRiskInput(
            partner_name="Intel",
            ticker="INTC",
            cik="0000050863",
            annual_spend_or_exposure=850_000,
            business_criticality="High",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.2,
                debt_to_equity=1.8,
                profit_margin=0.03,
                revenue_yoy_change=-0.04,
                latest_10k_filing_date="2026-01-31",
                latest_10q_filing_date="2026-05-01",
                available_concepts=["Assets", "Liabilities", "Revenues", "NetIncomeLoss", "StockholdersEquity"],
                missing_concepts=["AssetsCurrent", "LiabilitiesCurrent"],
            ),
        ),
        PartnerRiskInput(
            partner_name="3M",
            ticker="MMM",
            cik="0000066740",
            annual_spend_or_exposure=320_000,
            business_criticality="Medium",
            single_source_dependency="No",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.6,
                debt_to_equity=1.1,
                profit_margin=0.10,
                revenue_yoy_change=0.02,
                latest_10k_filing_date="2026-02-15",
                latest_10q_filing_date="2026-05-05",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                    "StockholdersEquity",
                ],
                missing_concepts=[],
            ),
        ),
        PartnerRiskInput(
            partner_name="Amkor Technology",
            ticker="AMKR",
            cik="0001047127",
            annual_spend_or_exposure=460_000,
            business_criticality="High",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.4,
                debt_to_equity=1.4,
                profit_margin=0.06,
                revenue_yoy_change=-0.02,
                latest_10k_filing_date="2026-02-20",
                latest_10q_filing_date="2026-05-07",
                available_concepts=["Assets", "Liabilities", "AssetsCurrent", "LiabilitiesCurrent", "Revenues"],
                missing_concepts=["CashAndCashEquivalentsAtCarryingValue"],
            ),
        ),
        PartnerRiskInput(
            partner_name="Amphenol",
            ticker="APH",
            cik="0000820313",
            annual_spend_or_exposure=390_000,
            business_criticality="High",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=2.0,
                debt_to_equity=0.8,
                profit_margin=0.14,
                revenue_yoy_change=0.06,
                latest_10k_filing_date="2026-02-14",
                latest_10q_filing_date="2026-05-03",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                    "StockholdersEquity",
                ],
                missing_concepts=[],
            ),
        ),
        PartnerRiskInput(
            partner_name="Analog Devices",
            ticker="ADI",
            cik="0000006281",
            annual_spend_or_exposure=420_000,
            business_criticality="High",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.8,
                debt_to_equity=0.6,
                profit_margin=0.18,
                revenue_yoy_change=0.01,
                latest_10k_filing_date="2026-01-22",
                latest_10q_filing_date="2026-05-02",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                    "StockholdersEquity",
                ],
                missing_concepts=[],
            ),
        ),
        PartnerRiskInput(
            partner_name="Corning",
            ticker="GLW",
            cik="0000024741",
            annual_spend_or_exposure=510_000,
            business_criticality="High",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.3,
                debt_to_equity=1.6,
                profit_margin=0.04,
                revenue_yoy_change=-0.03,
                latest_10k_filing_date="2026-02-10",
                latest_10q_filing_date="2026-05-06",
                available_concepts=["Assets", "Liabilities", "Revenues", "NetIncomeLoss", "StockholdersEquity"],
                missing_concepts=["AssetsCurrent"],
            ),
        ),
        PartnerRiskInput(
            partner_name="Flex",
            ticker="FLEX",
            cik="0000866374",
            annual_spend_or_exposure=920_000,
            business_criticality="Critical",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.1,
                debt_to_equity=2.2,
                profit_margin=0.02,
                revenue_yoy_change=-0.12,
                latest_10k_filing_date="2026-01-20",
                latest_10q_filing_date="2026-04-25",
                available_concepts=["Assets", "Liabilities", "Revenues", "NetIncomeLoss"],
                missing_concepts=[
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "CashAndCashEquivalentsAtCarryingValue",
                ],
            ),
        ),
        PartnerRiskInput(
            partner_name="Micron Technology",
            ticker="MU",
            cik="0000723125",
            annual_spend_or_exposure=780_000,
            business_criticality="Critical",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=1.7,
                debt_to_equity=0.9,
                profit_margin=-0.02,
                revenue_yoy_change=-0.08,
                latest_10k_filing_date="2026-01-25",
                latest_10q_filing_date="2026-05-04",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                ],
                missing_concepts=["StockholdersEquity"],
            ),
        ),
        PartnerRiskInput(
            partner_name="Qualcomm",
            ticker="QCOM",
            cik="0000804328",
            annual_spend_or_exposure=760_000,
            business_criticality="Critical",
            single_source_dependency="Partial",
            sec_metrics=SECFinancialMetrics(
                current_ratio=2.1,
                debt_to_equity=0.7,
                profit_margin=0.16,
                revenue_yoy_change=0.04,
                latest_10k_filing_date="2026-01-30",
                latest_10q_filing_date="2026-05-08",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                    "StockholdersEquity",
                ],
                missing_concepts=[],
            ),
        ),
        PartnerRiskInput(
            partner_name="Texas Instruments",
            ticker="TXN",
            cik="0000097476",
            annual_spend_or_exposure=430_000,
            business_criticality="High",
            single_source_dependency="No",
            sec_metrics=SECFinancialMetrics(
                current_ratio=2.5,
                debt_to_equity=0.5,
                profit_margin=0.22,
                revenue_yoy_change=0.03,
                latest_10k_filing_date="2026-02-01",
                latest_10q_filing_date="2026-05-09",
                available_concepts=[
                    "Assets",
                    "Liabilities",
                    "AssetsCurrent",
                    "LiabilitiesCurrent",
                    "Revenues",
                    "NetIncomeLoss",
                    "StockholdersEquity",
                ],
                missing_concepts=[],
            ),
        ),
    ]


def get_all_partner_inputs() -> list[PartnerRiskInput]:
    return build_partner_inputs()


def find_partner_input(partner_name: str) -> PartnerRiskInput | None:
    normalized_name = partner_name.strip().lower()

    for partner in build_partner_inputs():
        if partner.partner_name.lower() == normalized_name:
            return partner

        if partner.ticker.lower() == normalized_name:
            return partner

    return None