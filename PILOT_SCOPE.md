# Fixed-Scope Pilot: CSV/Excel Data Preparation + KPI Report

This document describes a **potential** paid work package for a BI or software agency. It is not a quote or service-level guarantee.

## Typical request

> We receive an order export and a customer workbook. The keys are inconsistent, some records are invalid, and we need a repeatable revenue report that analysts can trust.

## Inputs to confirm before pricing

- Up to two agreed source formats (for example, CSV and Excel) and their expected volume.
- A **sanitized sample** with no real client identifiers or confidential personal data.
- Exact matching keys, accepted statuses, metric definitions and target output example.
- Who signs off the data quality exclusions and the delivery deadline.

## Deliverables

1. Cleaned, joined dataset with normalized fields.
2. Reproducible Python workflow with local run instructions.
3. Quality issue log: source rows, validation reason(s), and summary counts.
4. KPI outputs by agreed dimensions and one offline HTML overview.
5. Tests for the agreed business rules; clear run evidence and a short handoff.
6. One correction round for discrepancies against the agreed acceptance criteria.

## Acceptance criteria

- Every source row is either present in the cleaned output or listed with a reason for exclusion.
- Keys are unique where required; ambiguous duplicate IDs are surfaced, not guessed.
- An agreed sample of KPI figures reconciles to source transactions.
- Re-running with unchanged source files yields the same results.
- Inputs and outputs are documented; the agency can run the script without the freelancer.

## Exclusions unless separately quoted

Production API connectors, authentication, private-cloud deployment, undefined KPI logic, machine-learning training, open-ended dashboard design, continuous maintenance or data hosting.

## Commercial model

Fixed scope, fee and schedule **after** examining sample data and confirming required outputs. A 48–72-hour turnaround may be achievable for small, cleanly scoped tasks but is **not promised by default**. The agency and freelancer must agree in writing on payment schedule, confidentiality, intellectual property and white-label use.

**Portfolio:** https://senanur-cetin.vercel.app/  
**Code samples:** https://github.com/senanurcetin  
**Contact:** senanur.cetin.work@gmail.com
