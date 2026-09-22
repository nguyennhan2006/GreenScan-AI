from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

class CrawlPolicy(BaseModel):
    max_depth: int = Field(default=4, ge=0, le=8)
    delay_seconds: float = Field(default=2.5, ge=0.1)
    max_requests_per_minute: int = Field(default=18, ge=1, le=300)
    verify_ssl: bool = True
    robots_on_missing: Literal["allow", "deny"] = "allow"
    robots_on_error: Literal["skip", "allow"] = "skip"
    use_sitemaps: bool = True
    max_sitemap_urls: int = Field(default=5000, ge=0, le=50000)
    save_relevant_html: bool = True
    user_agent: str = "GreenScanVNResearchBot/1.0 (+replace-with-team-email)"

class CompanyConfig(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    ticker: str
    exchange: Literal["HOSE", "HNX", "UPCOM"]
    company: str
    sector: str
    aliases: list[str]
    years: list[int]
    enabled: bool = True
    official_domains: list[str]
    attachment_domains: list[str] = []
    official_start_urls: list[HttpUrl]
    cafef_urls: list[HttpUrl]
    hnx_urls: list[HttpUrl] = []
    policy: CrawlPolicy = CrawlPolicy()

    @field_validator("years")
    @classmethod
    def validate_years(cls, value: list[int]) -> list[int]:
        years=sorted(set(value))
        if not years or min(years)<2000 or max(years)>2100:
            raise ValueError("invalid years")
        return years

class Registry(BaseModel):
    companies: list[CompanyConfig]
