# 03 — Tài liệu bắt buộc theo profile

Không phải 29 target đều là doanh nghiệp niêm yết cùng kiểu. Crawler phải lấy đúng loại tài liệu phù hợp với pháp nhân và loại case.

## `asset_manager`

**Bắt buộc:**

- `authority_case_pack`
- `parent_or_adviser_annual_report_or_filing`
- `esg_or_responsible_investment_policy`
- `case_product_pds_prospectus_or_methodology`
- `case_product_holdings_or_screen_evidence_if_official`

**Ưu tiên:**

- `stewardship_report`
- `sustainable_investing_report`
- `product_webpage_snapshot_metadata`

> Do not force a sustainability report if the legal claim is product-level; product disclosure is primary evidence.

## `super_fund`

**Bắt buộc:**

- `authority_case_pack`
- `fund_annual_report`
- `pds_or_member_disclosure`
- `investment_or_responsible_investment_policy`
- `case_product_document`

**Ưu tiên:**

- `annual_member_meeting_material`
- `holdings_or_exclusion_policy`

> Track trustee/entity changes and mergers by effective date.

## `energy_company`

**Bắt buộc:**

- `authority_case_pack`
- `annual_or_integrated_report`
- `sustainability_or_climate_report_if_separate`
- `challenged_ad_or_market_announcement_if_official`

**Ưu tiên:**

- `climate_transition_plan`
- `assurance_statement`
- `esg_data_book`

> If sustainability is integrated in annual report, mark integrated; do not duplicate the same PDF as two docs.

## `mining_agriculture`

**Bắt buộc:**

- `authority_case_pack`
- `annual_report_or_asx_filing`
- `market_announcements_related_to_case`
- `sustainability_or_project_environmental_material_if_official`

**Ưu tiên:**

- `project_technical_or_reforestation_document`

> Use official company/ASX sources for historical announcements.

## `consumer_brand`

**Bắt buộc:**

- `authority_case_pack`
- `parent_annual_or_integrated_report`
- `sustainability_or_esg_report_if_separate`
- `challenged_ad_packaging_or_product_claim_artifact`

**Ưu tiên:**

- `product_lca_or_substantiation_document`
- `assurance_or_esg_data`

> Exact challenged marketing representation is more important than unrelated parent ESG statements.

## `retail_brand`

**Bắt buộc:**

- `authority_case_pack`
- `parent_annual_report`
- `sustainability_report_or_plan`
- `challenged_ad_or_product_claim_artifact`

**Ưu tiên:**

- `product_lca_or_methodology`
- `esg_data_book`

> Keep product claim scope separate from corporate sustainability statements.

## `bank`

**Bắt buộc:**

- `authority_case_pack`
- `annual_report`
- `esg_or_climate_report`
- `financed_emissions_or_climate_datapack`
- `challenged_ad_artifact`

**Ưu tiên:**

- `transition_plan`
- `sector_policy`
- `assurance_statement`

> Financed-emissions context is often material; retrieve quantitative disclosure and methodology.

## `airline_public`

**Bắt buộc:**

- `authority_case_pack`
- `annual_report`
- `sustainability_or_nonfinancial_statement`
- `challenged_ad_artifact`

**Ưu tiên:**

- `sustainability_fact_sheet`
- `tcfd_or_sasb_report`
- `fleet_emissions_data`

> Collect aviation emissions methodology where available.

## `airline_private`

**Bắt buộc:**

- `authority_case_pack`
- `sustainability_or_environment_report`
- `challenged_ad_artifact`

**Ưu tiên:**

- `official_financial_or_annual_disclosure_if_public`
- `saf_or_offset_methodology`

> Do not invent annual-report coverage for private entities; mark official unavailability.

## `automotive`

**Bắt buộc:**

- `authority_case_pack`
- `integrated_or_annual_report`
- `sustainability_report`
- `challenged_ad_or_vehicle_claim_artifact`

**Ưu tiên:**

- `lca_methodology`
- `environmental_data`
- `third_party_verification`

> Vehicle/product lifecycle claims require product-specific substantiation.

## `fashion_brand`

**Bắt buộc:**

- `authority_case_pack`
- `parent_annual_or_integrated_report`
- `sustainability_or_impact_report`
- `challenged_product_or_material_claim_artifact`

**Ưu tiên:**

- `material_standard_or_methodology`
- `supply_chain_environmental_data`
- `assurance_report`

> Map local advertising entity/brand to parent reporting entity; do not transfer labels to all products.
