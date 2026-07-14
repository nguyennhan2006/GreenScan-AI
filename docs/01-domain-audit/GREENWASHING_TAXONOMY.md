# GREENWASHING_TAXONOMY.md

Version: 0.1  
Status: Draft for MVP + manual audit protocol  
Owner: Research Lead / Audit reviewer  
Last updated: 2026-07-07

## 1. Purpose

This document defines the taxonomy used to identify, classify, and review greenwashing-related claims in corporate, financial, ESG, and sustainability disclosures. It is designed for two users:

1. Human reviewers who manually score claims.
2. AI agents that extract claims, retrieve evidence, and produce preliminary verdicts.

The taxonomy must be treated as a controlled vocabulary. Claude Code and other implementation agents must not invent new claim categories without updating this document.

## 2. Source basis

This taxonomy is aligned with the following high-trust references:

- ESAs / ESMA common understanding of greenwashing: greenwashing occurs when sustainability-related statements, declarations, actions, or communications do not clearly and fairly reflect the underlying sustainability profile of an entity, financial product, or financial service, and may mislead consumers, investors, or other market participants.
- FTC Green Guides, 16 CFR Part 260: environmental claims should be truthful, not misleading, properly qualified, clear about the object of the claim, not overstated, and substantiated by a reasonable basis; environmental claims often require competent and reliable scientific evidence.
- IFRS S1: sustainability-related disclosure should help users of general purpose financial reports assess sustainability-related risks and opportunities that may affect cash flows, access to finance, or cost of capital.
- GRI Standards: sustainability reporting should help organizations report impacts on the economy, environment, and people in a comparable and credible way.
- ICMA Green Bond Principles: green bond assessment should cover use of proceeds, project evaluation and selection, management of proceeds, and reporting.

## 3. Core definitions

### 3.1 Green claim

A green claim is any statement, declaration, action, communication, label, metric, target, image, or implication that presents an entity, product, service, project, financing instrument, or activity as environmentally positive, environmentally less harmful, sustainable, ESG-aligned, transition-aligned, net-zero aligned, climate-friendly, or compliant with green criteria.

### 3.2 Greenwashing risk

Greenwashing risk is the risk that a green claim is misleading, overstated, vague, unsupported, selectively disclosed, contradicted by evidence, or not aligned with applicable legal/taxonomy/technical criteria.

### 3.3 Claim object

Every extracted claim must be stored as a structured object:

```json
{
  "claim_id": "C-0001",
  "claim_text": "...",
  "source_document_id": "...",
  "source_page": 12,
  "company": "...",
  "reporting_year": 2024,
  "claim_category": "ENV_EMISSIONS_REDUCTION",
  "greenwashing_pattern": ["QUANTITATIVE_CONTRADICTION"],
  "is_quantifiable": true,
  "requires_external_evidence": true,
  "materiality_level": "HIGH"
}
```

## 4. Claim category taxonomy

### 4.1 Environmental performance claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| ENV_EMISSIONS_REDUCTION | Emissions reduction | Claim that GHG emissions have decreased, been avoided, offset, neutralized, or controlled | Scope 1/2/3 data, baseline year, method, boundary, assurance |
| ENV_ENERGY_RENEWABLE | Renewable energy | Claim about using renewable energy, green electricity, solar, wind, biomass, RECs, PPAs | Energy mix, renewable share, certificates, contracts, period |
| ENV_ENERGY_EFFICIENCY | Energy efficiency | Claim about using less energy or improving energy intensity | Energy consumption, production volume, intensity metric, baseline |
| ENV_WATER | Water management | Claim about saving, recycling, treating, or reducing water use | Water withdrawal, discharge, treatment records, permits, location |
| ENV_WASTE | Waste and circularity | Claim about recycling, reducing waste, reuse, circular economy | Total waste, hazardous waste, recycled share, disposal records |
| ENV_POLLUTION | Pollution prevention | Claim about reducing air, soil, water, noise, or chemical pollution | Monitoring data, permits, incident records, regulatory reports |
| ENV_BIODIVERSITY | Biodiversity and ecosystem | Claim about restoration, conservation, tree planting, habitat protection | Project scope, location, survival rate, ecological outcome evidence |
| ENV_PRODUCT | Green product/service | Product or service claimed to be eco-friendly, low-carbon, recyclable, biodegradable | Product LCA, certification, technical standard, customer-facing claim context |

### 4.2 Climate target and transition claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| CLM_NET_ZERO | Net-zero claim | Claim about net-zero target, carbon neutrality, climate neutrality | Scope coverage, target year, interim milestones, offsets policy, transition plan |
| CLM_TARGET | Climate target | Claim about reduction targets, science-based targets, Paris alignment | Baseline, target boundary, pathway, approval/certification if mentioned |
| CLM_OFFSET | Carbon offset claim | Claim that emissions are offset, neutralized, or compensated | Offset project registry, additionality, permanence, vintage, retirement proof |
| CLM_TRANSITION | Transition claim | Claim about transition strategy, decarbonization roadmap, green transformation | CAPEX plan, operational plan, target tracking, governance, scenario analysis |

### 4.3 Sustainable finance claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| FIN_GREEN_BOND | Green bond | Bond is labelled green, sustainable, climate, transition, ESG | Use of proceeds, project list, eligibility criteria, management of proceeds, allocation report, external review |
| FIN_GREEN_LOAN | Green loan / green credit | Loan or credit facility claimed to finance green activity | Loan purpose, borrower project, taxonomy alignment, covenants, monitoring |
| FIN_CAPEX_GREEN | Green CAPEX | Claim that investment spending is green, climate-aligned, or transition-aligned | CAPEX breakdown, project classification, taxonomy criteria, board approval |
| FIN_REVENUE_GREEN | Green revenue | Claim that revenue comes from green products/services | Revenue taxonomy mapping, eligible activity definitions, audit trail |
| FIN_USE_OF_PROCEEDS | Use-of-proceeds | Claim that funds are allocated to eligible green projects | Separate tracking, bank account/ledger, allocation schedule, unallocated balance |
| FIN_SUSTAINABILITY_LINKED | Sustainability-linked finance | Coupon/interest/terms linked to ESG KPI | KPI materiality, calibration, baseline, verification, penalty/step-up terms |

### 4.4 Legal, taxonomy, and compliance claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| LEG_COMPLIANCE | Environmental compliance | Claim of full compliance with environmental law | Permits, inspection records, violations, fines, enforcement decisions |
| LEG_TAXONOMY_ALIGNMENT | Green taxonomy alignment | Claim that project/activity meets green taxonomy or official green criteria | Technical screening criteria, DNSH/social safeguards if applicable, official confirmation |
| LEG_LICENSE | Permit and license | Claim that project is permitted or approved | Environmental permit, EIA/ĐTM, official approvals, expiry date |
| LEG_VIOLATION_RESPONSE | Violation remediation | Claim that past violations were remediated | Remediation plan, regulator confirmation, monitoring reports |

### 4.5 Governance, disclosure, and assurance claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| GOV_ASSURANCE | Independent assurance | Claim that ESG data is assured, audited, verified, certified | Assurance report, scope, standard, provider independence, limitations |
| GOV_DISCLOSURE_STANDARD | Reporting standard | Claim that report follows GRI, ISSB, SASB, TCFD, etc. | Content index, mapping table, required disclosures, omissions |
| GOV_ESG_RATING | ESG rating / award | Claim about ESG ranking, award, score, membership | Rating provider, date, methodology, scope, limitations |
| GOV_RISK_MANAGEMENT | ESG governance | Claim about governance, board oversight, risk management | Board minutes, policy, committee charter, management process |

### 4.6 CSR and social-environmental reputation claims

| Code | Category | Description | Typical evidence required |
|---|---|---|---|
| CSR_COMMUNITY | Community/environmental CSR | Tree planting, donations, clean-up, community environmental activities | Project record, scale, outcome, relation to material impact |
| CSR_BRAND_IMAGE | Green brand image | General green image, nature visuals, symbolic messaging | Claim context, supporting evidence, risk of creating misleading impression |
| CSR_PHILANTHROPY | Philanthropic environmental activity | Donations or sponsorships presented as sustainability | Donation amount, beneficiary, materiality versus core impact |

## 5. Greenwashing pattern taxonomy

Each claim may have one or more greenwashing patterns.

| Pattern code | Pattern | Description | Warning signal |
|---|---|---|---|
| VAGUE_CLAIM | Vague claim | Uses broad words without measurable content | “green”, “eco-friendly”, “sustainable”, “for the planet” |
| NO_EVIDENCE | Unsupported claim | Claim exists but evidence is absent or weak | No data, no source, no page, no method |
| SELECTIVE_DISCLOSURE | Cherry-picking | Highlights a small positive action while omitting major negative impact | Tree planting emphasized; emissions omitted |
| QUANTITATIVE_CONTRADICTION | Quantitative contradiction | Claim conflicts with numeric data | Says emissions decreased; Scope 1+2 increased |
| LEGAL_CONTRADICTION | Legal contradiction | Claim conflicts with legal or enforcement evidence | Claims compliance; has environmental fines |
| FINANCIAL_GREENWASHING | Financial greenwashing | Financing labelled green without credible use-of-proceeds or taxonomy alignment | No project list, no allocation report, unclear tracking |
| EMPTY_FUTURE_COMMITMENT | Empty future commitment | Long-term target without plan, milestones, CAPEX, or KPI | “Net zero 2050” without 2030 target |
| SCOPE_SHIFTING | Scope shifting | Claim appears positive by changing boundary or excluding material scopes | Only Scope 2 reduced; Scope 1/3 omitted |
| BASELINE_MANIPULATION | Baseline manipulation | Baseline chosen or changed to exaggerate progress | Uses abnormal pandemic year as baseline |
| OFFSET_OVERRELIANCE | Offset overreliance | Neutrality claim relies on offsets instead of actual reduction | Carbon neutral with no operational reduction |
| LABEL_CONFUSION | Weak label/certification | Uses labels, awards, seals without clear meaning or independent basis | “certified green” with no certifier |
| IMPLIED_CLAIM | Implied environmental claim | Visuals, symbols, design imply environmental benefit | Leaves, earth imagery, green badges |
| COMPARATIVE_UNCLEAR | Unclear comparison | Comparative claim lacks comparator and basis | “greener”, “less polluting”, “better for climate” |
| MATERIAL_OMISSION | Material omission | Omits information necessary to avoid misleading impression | Does not disclose hazardous waste or violations |
| CSR_DISTRACTION | CSR distraction | Uses philanthropy to distract from operational environmental harm | Small donation highlighted over core impacts |

## 6. Materiality levels

| Level | Definition | Handling |
|---|---|---|
| HIGH | Claim relates to core environmental impact, financing, law, or strategic targets | Must be verified with strong evidence; human review if high risk |
| MEDIUM | Claim relates to relevant but non-core sustainability activity | Verify with normal evidence standard |
| LOW | Claim is peripheral CSR or brand language | Verify if misleading impression risk exists; lower weight in company score |

Materiality must be determined by industry and company profile. For example:

- Cement, steel, energy: emissions, energy, pollution, permits are high materiality.
- Banks: green credit, financed emissions, use-of-proceeds, sector exposure are high materiality.
- Real estate: green buildings, energy efficiency, permits, land use, water, construction waste are high materiality.
- Consumer goods: packaging, recyclable claims, product claims, supply chain impact are high materiality.

## 7. Evidence requirement by claim type

| Claim type | Minimum evidence for “Supported” |
|---|---|
| Quantitative reduction claim | Metric value, baseline, current period, unit, method, organizational boundary |
| Renewable energy claim | Renewable amount/share, total energy, source, certificate/contract if applicable |
| Net-zero claim | Scope coverage, target year, interim targets, reduction plan, offset treatment |
| Green bond claim | Use of proceeds, eligibility criteria, project list, management of proceeds, allocation/impact reporting |
| Taxonomy alignment claim | Specific taxonomy criteria, project mapping, confirmation or documented self-assessment |
| Compliance claim | Permits, absence/presence of enforcement actions, inspection/legal records |
| Assurance claim | Assurance provider, scope, standard, conclusion, limitations |

## 8. Non-green claims and exclusions

The following should not be scored as greenwashing unless they create an environmental impression:

- Purely social or governance claims with no environmental or ESG implication.
- Generic business performance claims.
- Philanthropy not connected to environmental messaging.
- Mandatory legal statements that do not imply environmental benefit.

If uncertain, extract the claim but mark `scope_status = NEEDS_REVIEW`.

## 9. Implementation notes

- Store claim categories as enums.
- Store greenwashing patterns as an array because one claim can trigger multiple patterns.
- Do not treat a claim as false only because evidence is missing. Missing evidence maps to `UNSUPPORTED` or `INSUFFICIENT_EVIDENCE`, not automatically `CONTRADICTED`.
- A claim becomes `CONTRADICTED` only when reliable evidence conflicts with it.
- Claims with `HIGH` materiality and verdict `CONTRADICTED` or score above 70 must go to human review.

## 10. Open issues

- Vietnam-specific taxonomy mapping needs verified legal source files and exact criteria extraction.
- Sector-specific materiality thresholds need calibration.
- Claims mixing E, S, and G need a multi-label tagging rule.
