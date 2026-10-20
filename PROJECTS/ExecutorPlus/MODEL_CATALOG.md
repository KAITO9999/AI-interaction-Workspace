# Executor++ — model characteristics catalog

Status: schema established; profiles below are placeholders until verified. This file is intentionally separate from the project plan and work-model procedures.

## Mandatory rules

1. State the exact model name/version and provider when recording model-specific work. If not observable, use `unknown/unverified`; never infer from style.
2. Every factual claim about a model must have at least one source URL and source publication/access date. Prefer official model cards, release notes, API docs, and original benchmark papers/datasets.
3. A source must actually support the adjacent claim. Separate provider claims from independent measurements and third-party reports.
4. Label each field: `source-confirmed`, `independently measured`, `inferred`, `disputed`, or `unknown`.
5. For benchmarks, include benchmark/task, evaluation date, model version, test setup, scoring method, and source. Do not treat results from incompatible setups as directly comparable.
6. For pricing and availability, include region/date and link to the official current source; recheck time-sensitive fields before presenting them.
7. Record conflicting sources and uncertainty. Never fill missing fields by guessing. Do not present model-generated descriptions as independent evidence.

## Profile template

For each model/version, record:

- **Exact model identifier / provider:**
- **Verification status:** unverified / partially verified / verified
- **Source-confirmed capabilities:**
- **Context window and output limits:**
- **Modalities and tool/function calling:**
- **Reasoning / latency / throughput notes:**
- **Pricing and availability (with date/region):**
- **Benchmarks:** task, date, setup, metric, score, source
- **Strengths / limitations:** each claim source-linked
- **Independent test results:** test suite/version, date, environment, results
- **Conflicting reports / caveats:**
- **Sources:** title, publisher/authors, publication date, access date, URL, supported claim
- **Last reviewed:**
- **Reviewer / model attribution:**

## Requested initial profile slots

These are requested catalog slots, not assertions that all names, versions, or public specifications are currently verified. Do not fill characteristics without reliable evidence.

### GPT-6
- **Verification status:** pending source-backed profile completion
- **Source-confirmed characteristics:** none recorded in this catalog yet
- **Sources:** add official model/product documentation and dated sources before publishing factual claims

### Sonnet 5
- **Verification status:** pending identity and source verification
- **Source-confirmed characteristics:** none recorded in this catalog yet
- **Sources:** confirm exact model identifier with official provider documentation before publishing factual claims

### Grok 4.5
- **Verification status:** pending identity and source verification
- **Source-confirmed characteristics:** none recorded in this catalog yet
- **Sources:** confirm exact model identifier with official provider documentation before publishing factual claims

## Update checklist

- [ ] Verify the exact public model/version identifier.
- [ ] Gather official sources and relevant independent evaluations.
- [ ] Attach a source and date to every factual field.
- [ ] Check benchmark comparability and disclose setup.
- [ ] Mark unsupported, stale, or conflicting claims explicitly.
- [ ] Review model-to-model comparisons for equivalent settings.
- [ ] Record reviewer identity and review date.
