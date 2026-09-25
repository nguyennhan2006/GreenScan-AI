# USER_PERSONAS.md

> **Định vị sản phẩm đã được viết lại 2026-09-25** — xem [AUDITOR_WORKFLOW_POSITIONING.md](AUDITOR_WORKFLOW_POSITIONING.md). Người dùng là **kiểm toán viên đang làm thủ công**, không phải sáu persona; sản phẩm tự động hoá **đọc · định vị · ghi chép** và trả về một **hàng đợi đã xếp ưu tiên**, không phải một bảng verdict. Tài liệu này giữ lại phần mô tả nhu cầu và phạm vi còn dùng được.


Version: 0.1  
Status: Draft for MVP planning  
Owner: Product Owner / Research Lead  
Last updated: 2026-07-07

## 1. Purpose

This document defines the primary and secondary users of the Greenwashing Detection product. It translates the project problem definition and audit protocol into product-facing user groups, needs, workflows, success criteria, and constraints.

The product is not designed to replace auditors, regulators, or legal counsel. It is an evidence-first decision support system that helps users identify, inspect, and document greenwashing risk in sustainability-related claims.

## 2. Product principle for personas

Every persona must be able to answer:

```text
What claim was made?
What evidence supports or contradicts it?
How risky is the claim?
Can I trace the conclusion back to source documents?
What should I check next?
```

The depth of the answer differs by persona. A retail investor needs a simple risk summary. An ESG reviewer needs claim-level working papers and source citations.

## 3. Persona map

| Persona | Priority | Main job | Main output needed |
|---|---:|---|---|
| ESG reviewer / auditor | Primary | Verify claims and sign off high-risk cases | Evidence card, working paper, reviewer checklist |
| Sustainability / financial analyst | Primary | Analyze and compare companies | Claim table, dashboard, exportable report |
| Bank credit / green finance officer | Primary | Assess green loan, green bond, use-of-proceeds risk | Financial-greenwashing analysis, taxonomy alignment |
| Product owner / internal QA | Primary for build | Validate system behavior and demo quality | Test cases, traceable outputs, acceptance criteria |
| Investor / consumer researcher | Secondary | Understand whether a company’s green claims are credible | Plain-language risk summary, top red flags |
| Regulator / academic evaluator | Secondary | Inspect methodology and evidence trail | Methodology report, audit log, source register |

## 4. Persona 1 — ESG Reviewer / Auditor

### 4.1 Profile

An ESG reviewer, sustainability assurance staff member, internal auditor, or domain expert responsible for checking whether sustainability claims are fairly presented and sufficiently supported.

### 4.2 Goals

- Review extracted green claims without reading the full document from scratch.
- Check whether each claim is supported by appropriate evidence.
- Identify missing evidence, contradictions, and potential misleading wording.
- Approve, reject, or revise AI-suggested verdicts.
- Preserve an audit trail for future review.

### 4.3 Pain points

- Reports are long, repetitive, and inconsistent across companies.
- Claims are scattered across annual reports, ESG reports, websites, bond frameworks, and news.
- Evidence may be in tables, notes, appendices, or external sources.
- It is difficult to ensure two reviewers score claims consistently.

### 4.4 Key product needs

| Need | Product response |
|---|---|
| See exact claim text | Claim list with source document, page, and section |
| Check evidence quickly | Evidence card with supporting and contradicting evidence |
| Understand AI decision | Verdict explanation mapped to audit protocol |
| Override AI | Human review action with comment and sign-off |
| Preserve work | Claim verification working paper export |

### 4.5 Success criteria

- Reviewer can inspect a claim and its evidence in under 3 minutes for simple cases.
- Reviewer can trace every verdict to source document, page, and evidence item.
- Reviewer can see why a claim is high-risk without reading the full source report.
- Reviewer can change verdict and leave a reason.

### 4.6 Must not happen

- AI invents evidence or citations.
- AI hides uncertainty.
- AI marks a claim as supported when the evidence does not match scope, time period, or metric.
- Reviewer cannot find the original source.

## 5. Persona 2 — Sustainability / Financial Analyst

### 5.1 Profile

An analyst working in research, investment, consulting, academia, or an internal sustainability team. This user compares disclosures across companies or evaluates credibility of ESG-related narratives.

### 5.2 Goals

- Understand the greenwashing risk profile of one company or multiple companies.
- Compare risk by category: emissions, energy, waste, water, green finance, net-zero, compliance.
- Export structured results for reports or further analysis.
- Identify patterns: vague claims, missing baselines, unsupported targets, inconsistent metrics.

### 5.3 Pain points

- ESG reports are not standardized enough for quick comparison.
- Many claims are qualitative and hard to quantify.
- External contradictions are time-consuming to find.
- Manual spreadsheet review is slow and error-prone.

### 5.4 Key product needs

| Need | Product response |
|---|---|
| Company overview | Dashboard with risk score and verdict distribution |
| Detailed analysis | Filterable claim table |
| Evidence quality | Evidence strength and missing-evidence fields |
| Export | Markdown/CSV/PDF report export |
| Comparison | Company-level risk categories and summary |

### 5.5 Success criteria

- Analyst can identify top 5 risk claims in less than 10 minutes.
- Analyst can export claim-level data for external analysis.
- Analyst can distinguish between unsupported claims and contradicted claims.

## 6. Persona 3 — Bank Credit / Green Finance Officer

### 6.1 Profile

A bank officer or green finance reviewer responsible for checking whether a loan, project, or bond marketed as green has enough documentation and aligns with applicable green criteria.

### 6.2 Goals

- Verify whether green-labelled financing has clear use of proceeds.
- Check whether a project fits relevant taxonomy or eligibility criteria.
- Identify missing allocation reports, project lists, impact metrics, or external reviews.
- Flag high-risk cases for deeper due diligence.

### 6.3 Pain points

- Use-of-proceeds documents can be vague.
- Allocation and impact reporting may be missing or delayed.
- A project may be labelled green without clear taxonomy alignment.
- Financial documents and environmental documents are often separated.

### 6.4 Key product needs

| Need | Product response |
|---|---|
| Green finance claim detection | FIN-01/FIN-02 claim taxonomy |
| Use-of-proceeds verification | Evidence checklist for bond/loan claims |
| Taxonomy alignment | Legal/taxonomy matching fields |
| Red flag detection | Missing allocation, unclear project, inconsistent CAPEX |
| Review trail | Working paper and reviewer sign-off |

### 6.5 Success criteria

- Officer can see whether a green bond/loan claim has project list, allocation report, management of proceeds, and impact reporting.
- Officer can see whether the evidence is direct, partial, or missing.
- Officer can hand off high-risk cases with a structured evidence packet.

## 7. Persona 4 — Product Owner / Internal QA

### 7.1 Profile

The person responsible for turning domain requirements into backlog items and making sure the system behaves consistently with audit logic.

### 7.2 Goals

- Translate audit protocol into implementation tasks.
- Ensure AI and code outputs follow the same schema and verdict definitions.
- Build demo cases that show the evidence-first workflow.
- Track known limitations and open questions.

### 7.3 Pain points

- Domain logic can drift between documents, prompts, and code.
- AI agents may invent logic unless docs are explicit.
- Demo UI may look convincing without being auditable.

### 7.4 Key product needs

| Need | Product response |
|---|---|
| Stable scope | MVP scope with in/out boundaries |
| Testable outputs | Output spec and acceptance criteria |
| Shared language | Glossary and fixed enums |
| Implementation sync | Task breakdown and handoff docs |

### 7.5 Success criteria

- Every implementation task maps to a documented product requirement.
- Every output field maps to a schema and user need.
- Demo can be reviewed against the QA checklist.

## 8. Persona 5 — Investor / Consumer Researcher

### 8.1 Profile

A non-expert or semi-expert user who wants to understand whether a company’s green narrative appears credible.

### 8.2 Goals

- See a simple risk summary.
- Understand top warning signs in plain language.
- Avoid being misled by vague sustainability language.
- Drill down only when needed.

### 8.3 Pain points

- Sustainability disclosures are technical.
- Terms like “green”, “eco-friendly”, “net-zero”, “carbon neutral” are confusing.
- It is hard to know whether a claim has real evidence.

### 8.4 Key product needs

| Need | Product response |
|---|---|
| Plain-language summary | Risk level and short explanation |
| Top red flags | Top 3–5 high-risk claims |
| Trust | Visible sources and page references |
| Caution | Clear disclaimer that output is risk assessment, not legal finding |

### 8.5 Success criteria

- User can understand why the system flagged a claim.
- User can distinguish “unsupported” from “contradicted”.
- User does not interpret the tool as a final legal judgment.

## 9. Persona 6 — Regulator / Academic Evaluator

### 9.1 Profile

A regulator, lecturer, research judge, or academic evaluator reviewing the methodology rather than only the product UI.

### 9.2 Goals

- Inspect whether the system is methodologically sound.
- Check whether the scoring rubric is transparent.
- Review evidence traceability and limitations.
- Evaluate reproducibility.

### 9.3 Key product needs

| Need | Product response |
|---|---|
| Method transparency | Audit protocol and scoring rubric |
| Evidence trail | Source register and audit log |
| Reproducibility | Versioned documents and outputs |
| Limitations | Safety boundaries and open questions |

## 10. Persona-to-feature matrix

| Feature | Reviewer | Analyst | Bank officer | Product owner | Investor | Evaluator |
|---|---:|---:|---:|---:|---:|---:|
| Upload documents | High | High | High | High | Medium | Medium |
| Claim extraction | High | High | High | High | Medium | High |
| Claim taxonomy | High | High | High | High | Low | High |
| Evidence card | High | High | High | High | Medium | High |
| Risk dashboard | Medium | High | High | High | High | Medium |
| Human review queue | High | Medium | High | High | Low | Medium |
| Audit working paper | High | Medium | High | High | Low | High |
| Export report | High | High | High | Medium | Medium | High |
| Methodology docs | Medium | Medium | Medium | High | Low | High |

## 11. Design implications

1. The product must have two levels of UI: a simple risk dashboard and a detailed evidence/audit view.
2. Reviewer workflows must preserve provenance and allow override.
3. Green finance users need use-of-proceeds and taxonomy fields, not only ESG text analysis.
4. Non-expert users need careful language to avoid overclaiming.
5. Product QA requires deterministic schemas, fixed verdict enums, and test cases.

## 12. Source alignment

This persona design is aligned with:

- `PROJECT_BRIEF.md`: target users and MVP scope.
- `PROBLEM_DEFINITION.md`: input/output and risk framing.
- `AUDIT_PROTOCOL.md`: manual review and evidence-first logic.
- `MANUAL_SCORING_RUBRIC.md`: claim-level and company-level scoring.
- ESMA/ESAs common understanding of greenwashing in financial markets.
- FTC Green Guides principles on environmental claim clarity and substantiation.
- IFRS S1 focus on sustainability-related information useful to users of general purpose financial reports.
- ICMA Green Bond Principles focus on use of proceeds, transparency, and reporting.
