"""Generate comprehensive dataset acquisition permissions matrix."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
evidence_dir = ROOT / "research/evidence"
evidence_dir.mkdir(parents=True, exist_ok=True)

matrix = [
    {
        "provider": "Tiingo (Free / Starter Tier)",
        "source_type": "Commercial REST API with Free Developer Tier",
        "primary_url": "https://api.tiingo.com/documentation/end-of-day",
        "api_access": "PERMITTED (500 symbols/month, 50 requests/hour with free API token)",
        "transient_processing": "PERMITTED (In-memory streaming, analysis, and metric calculation allowed)",
        "local_retention": "PROHIBITED (Terms of Use Section 3 forbid durable caching or local database/file storage)",
        "derived_result_publication": "PERMITTED (Aggregate performance metrics, Sharpe, drawdown curves publishable)",
        "raw_data_redistribution": "PROHIBITED (Public git commits, sublicensing, or file sharing strictly forbidden)",
        "engine_compliance_policy": "Enforced by StorageComplianceGuard: must use InMemoryStreamProvider; disk writes blocked."
    },
    {
        "provider": "Polygon.io (Free Tier)",
        "source_type": "Commercial REST API with Free Community Tier",
        "primary_url": "https://polygon.io/docs/stocks",
        "api_access": "PERMITTED (5 requests/minute; restricted to 2-year trailing history)",
        "transient_processing": "PERMITTED",
        "local_retention": "PERMITTED FOR INTERNAL USE (Internal dev caching allowed under TOS Section 2.1)",
        "derived_result_publication": "PERMITTED",
        "raw_data_redistribution": "PROHIBITED (TOS Section 3.2 prohibits public redistribution)",
        "engine_compliance_policy": "Can store in git-ignored data_cache/ if authorized; 2-year history limits multi-regime backtesting."
    },
    {
        "provider": "Polygon.io (Paid Starter Tier - $29/mo)",
        "source_type": "Commercial REST API / Flat Files",
        "primary_url": "https://polygon.io/pricing",
        "api_access": "PERMITTED (Unlimited queries; full 15+ years historical SIP aggregates)",
        "transient_processing": "PERMITTED",
        "local_retention": "PERMITTED FOR INTERNAL USE (Durable caching in git-ignored data_cache/ authorized)",
        "derived_result_publication": "PERMITTED",
        "raw_data_redistribution": "PROHIBITED (Raw data cannot be pushed to GitHub or shared)",
        "engine_compliance_policy": "Requires user purchase decision and private API key stored in root .env."
    },
    {
        "provider": "Yahoo Finance (via yfinance)",
        "source_type": "Unlicensed web scraper / undocumented endpoint wrapper",
        "primary_url": "https://query1.finance.yahoo.com/v8/finance/chart/",
        "api_access": "UNLICENSED (Yahoo TOS Section 1.3 explicitly prohibits automated queries)",
        "transient_processing": "LEGALLY UNRESOLVED (Tolerated by upstream starter runner, but vulnerable to IP throttling)",
        "local_retention": "LEGALLY UNRESOLVED (No redistribution or storage rights granted by Yahoo)",
        "derived_result_publication": "PERMITTED",
        "raw_data_redistribution": "PROHIBITED",
        "engine_compliance_policy": "Flagged as high-risk; suffers from retroactive cash-dividend restatements and survivor bias."
    },
    {
        "provider": "Stooq (stooq.com)",
        "source_type": "Public web CSV endpoint",
        "primary_url": "https://stooq.com/q/d/l/?s=spy.us&i=d",
        "api_access": "PERMITTED FOR MANUAL USE (Automated bulk queries encounter CAPTCHA/throttling)",
        "transient_processing": "PERMITTED",
        "local_retention": "PERMITTED FOR PERSONAL RESEARCH",
        "derived_result_publication": "PERMITTED",
        "raw_data_redistribution": "PROHIBITED",
        "engine_compliance_policy": "Lacks corporate action detail; survivor-biased."
    },
    {
        "provider": "In-Repo Sample Regimes (sample_regimes.json.gz)",
        "source_type": "Committed repository fixture",
        "primary_url": "Official starter repository (MIT License)",
        "api_access": "PERMITTED (Local file access)",
        "transient_processing": "PERMITTED",
        "local_retention": "PERMITTED (Committed in git)",
        "derived_result_publication": "PERMITTED",
        "raw_data_redistribution": "PERMITTED (Open-source competition asset)",
        "engine_compliance_policy": "Supported by StaticRegimeProvider; strictly in-sample diagnostic calibration."
    },
    {
        "provider": "CRSP / WRDS (Academic Institutional Feed)",
        "source_type": "Institutional Academic Database",
        "primary_url": "https://wrds-www.wharton.upenn.edu/",
        "api_access": "RESTRICTED (Requires institutional academic credentials)",
        "transient_processing": "PERMITTED FOR AUTHORIZED RESEARCHERS",
        "local_retention": "RESTRICTED (Secure institutional machines only)",
        "derived_result_publication": "PERMITTED (Academic reporting of summary statistics)",
        "raw_data_redistribution": "STRICTLY PROHIBITED (Severe copyright violation)",
        "engine_compliance_policy": "UNAVAILABLE without university credentials; redistribution completely barred."
    }
]

(evidence_dir / "dataset_acquisition_permissions_matrix.json").write_text(
    json.dumps(matrix, indent=2), encoding="utf-8"
)
print(f"Generated dataset_acquisition_permissions_matrix.json in {evidence_dir}")
