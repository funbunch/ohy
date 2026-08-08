# TELEMETRY.md — Data case for oversight reporting

This is what Ericka Lesley and the Rent Control Board need to report to
oversight and community advocates: what we measure, how it compares to the
reported baseline, and what questions the data can answer once it exists.

**Nothing below is a result.** These are field definitions for data collection
that starts once the system is in use. No improvement numbers are claimed —
none have been measured yet.

## What is measured, per ticket

| Field | Description |
|---|---|
| `channel` | How the constituent reached us: phone, text, or email |
| `urgency` | Triage tier: FAQ, normal, or URGENT (e.g., Airbnb/short-term rental cases) |
| `time_to_first_response` | Elapsed time from ticket received to first reply sent |
| `time_to_resolution` | Elapsed time from ticket received to the constituent confirming their question is covered |
| `escalated_to_human` | Boolean — whether the ticket left the automated path and went to staff |
| `constituent_confirmed_covered` | Boolean — whether the constituent answered "yes" to the closing question ("does this cover your question or do you need more info?") |
| `topic` | The rent-control topic the question falls under (e.g., general adjustment, eligibility, banked increases, eviction, coverage) |
| `party` | Whether the constituent identifies as a tenant, a landlord, or unspecified |
| `language` | Language the ticket was submitted in (en/es supported) |

## Future intake channels (not built)

`channel` today covers phone, text, and email. The office already has Google
Drive and GitHub connected, and mentioned **Zoom** as another channel worth
supporting later (e.g., a call transcript or meeting-derived ticket). This is
documented as a future channel value, not something implemented in this
build — adding it means extending `channel`'s allowed values and wiring an
intake source, not a telemetry design change.

## Design principle: data quality depends on capture being effortless

A field that's tedious to fill in gets filled in carelessly — that's not a
hypothetical, it's a known failure mode from people who've run enterprise
data systems for decades: if logging a ticket is a burden on the person doing
it, they will log something just to get past the form, and the telemetry
built on top of that is worthless no matter how well the fields are designed.

This means the fields above are aspirational unless the actual data-entry
step (whoever or whatever creates a ticket record) is as close to zero extra
effort as possible — ideally auto-captured from the channel and the
draft/critique/response flow itself, not hand-typed by a staff member after
the fact. Any implementation of this schema should treat "is this cheap to
fill in accurately" as a hard constraint on the ticket UI, not an
afterthought to optimize once the fields exist.

## Baseline comparison

**Baseline: 3–5 weeks per ticket.**

⚠️ This baseline is **reported by the Rent Control Board office**, not measured
by this system. It is the office's own estimate of current resolution time
under the existing process. It is not derived from ticket-level data and
should not be presented as a measurement.

Once this system is in use, `time_to_resolution` (measured, per ticket) is the
directly comparable figure. Until enough tickets have run through the system,
there is no measured resolution time to report, and no percentage or
multiplier of improvement should be stated.

## Questions this data can answer for oversight

Once ticket data accumulates, these fields support answering:

- **How many cases resolve without human intervention?**
  `escalated_to_human = false` count over total tickets.

- **Which topics generate the most consultations?**
  Distribution of `topic` across tickets. This is a proxy for where public
  communication about Santa Monica's rent control protections is weakest —
  the protections are strong but not widely known, so consultation volume by
  topic points directly at where outreach is needed.

- **How long do urgent cases take?**
  `time_to_resolution` filtered to `urgency = URGENT` (includes Airbnb/
  short-term rental cases, which are escalated to staff rather than
  answered automatically).

- **Who is the office serving — tenants or landlords?**
  Distribution of `party` across tickets. The office serves both; this shows
  the actual split in demand.

- **Are constituents actually satisfied, or just getting a reply?**
  `constituent_confirmed_covered = true` rate. A high `time_to_first_response`
  with a low confirmation rate would mean the system replies fast but isn't
  actually resolving questions — that gap matters more than speed alone.

## What this is not

This is not a report of results. It is the schema and the questions the
results will answer. Any number filled into these categories before real
ticket data exists would be invented — the red rule against fabricating facts
applies to telemetry claims exactly as it applies to legal facts.
