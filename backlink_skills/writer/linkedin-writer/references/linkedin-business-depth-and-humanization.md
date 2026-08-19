# LinkedIn Business Depth and Final Humanization

Use this reference after initial topic discovery and again after the factual/editorial rewrite. It solves two different problems:

1. enrich a LinkedIn article with the business context that professional readers need;
2. remove generic, over-structured, or synthetic-sounding prose without inventing a personality or trying to defeat AI detectors.

The research pass creates `linkedin-insight-map.md`. The final pass records its result in `linkedin-audit.md`.

## Part 1: Google-to-LinkedIn Research

LinkedIn search can be thin, personalized, signed-in, or difficult to inspect consistently. Use Google as a second discovery surface for publicly indexed LinkedIn material.

Google supports quoted exact phrases, `site:`, exclusions with `-`, and date operators such as `after:` and `before:`. Use them to narrow discovery, not to manufacture search-volume or trend claims.

### Query patterns

Build 8-20 searches from the topic, reader role, decision, and commercial context:

```text
site:linkedin.com/posts "<topic>" "<role>"
site:linkedin.com/posts "<topic>" "<business outcome>"
site:linkedin.com/posts "<topic>" "<objection or failure>"
site:linkedin.com/posts "<topic>" "<buyer or stakeholder>" after:YYYY-MM-DD
site:linkedin.com/pulse "<topic>" "<implementation>"
site:linkedin.com/pulse "<topic>" "<ROI, cost, risk, or governance>"
site:linkedin.com/company "<topic>" "<official announcement or case>"
site:linkedin.com "<exact phrase>" -jobs -learning
```

Useful substitutions:

| Dimension | Search terms |
|---|---|
| Decision-maker | CEO, founder, CIO, CTO, CHRO, VP, head of, manager |
| Functional stakeholder | product, engineering, finance, legal, security, procurement, sales, marketing, HR, operations |
| Economics | ROI, budget, cost, margin, revenue, payback, total cost of ownership |
| Execution | implementation, rollout, integration, adoption, workflow, operating model, change management |
| Risk | failure, objection, governance, compliance, security, downside, trade-off |
| Proof | case study, benchmark, pilot, lessons, metrics, before and after |
| Buying context | evaluation, build vs buy, vendor, procurement, hidden buyer, buying committee |
| Time | `after:YYYY-MM-DD`, current year, new policy, launch, production |

Search in the target audience's language and in English when the subject is globally discussed. Record both; do not silently translate a market-specific conclusion into a global one.

### Result handling

For each useful result, record:

- query and search date;
- result URL and visible publication date when available;
- author role and organization as presented publicly;
- format: post, Article/Pulse, company content, newsletter, or profile;
- the professional question, tension, example, objection, or vocabulary it surfaces;
- whether the original LinkedIn page was opened;
- evidence status: `conversation signal`, `practitioner experience`, `vendor claim`, or `verified fact`;
- follow-up primary source needed;
- what must not be copied.

A Google result or LinkedIn post can reveal language and debate. It does not automatically verify the claim inside it. Open the original page when possible and verify material facts against primary or authoritative sources.

Do not copy a creator's hook, framework name, sequence, memorable phrasing, anecdote, or conclusion. Synthesize across multiple sources and add the author's legitimate perspective.

## Part 2: Business Depth Map

A business article is not richer because it contains more trends or more headings. It is richer when it helps a professional understand the decision around the topic.

Cover the dimensions that materially affect the selected thesis:

### 1. Decision and trigger

- What decision must be made?
- Why does it need attention now?
- What happens if the organization waits?
- What evidence would justify acting or not acting?

### 2. Stakeholder and buying group

- Who sponsors, uses, approves, blocks, pays for, secures, or supports the change?
- Where do incentives conflict?
- Which “hidden buyer” has a concern the obvious user may miss?
- Who owns the outcome after launch?

### 3. Economics

- What is the current baseline?
- Which costs are visible, and which are shifted to review, integration, support, risk, or change management?
- What creates revenue, margin, retention, quality, or strategic option value?
- Which ROI claim is measurable now, and which remains an assumption?

### 4. Workflow and implementation

- What changes before, during, and after the focal tool or decision?
- Which data, integration, permission, handoff, training, or governance prerequisite matters?
- What is a credible pilot boundary?
- What must be true before scaling?

### 5. Measurement

- What baseline, leading indicator, outcome metric, and guardrail should be recorded?
- Who reviews the metric and on what cadence?
- What result would falsify the recommendation?
- Which attractive metric is only a vanity proxy?

### 6. Risk and objection

- What is the strongest informed objection?
- Where can the recommendation fail by company size, industry, regulation, maturity, or use case?
- What is reversible and what has a large blast radius?
- Which control reduces the risk without destroying the value?

### 7. Scenario and example

- Can the article walk through one concrete, attributable, or explicitly hypothetical scenario?
- What changes for a small team versus an enterprise?
- What does “before” and “after” look like operationally?
- Which edge case exposes the weakness of the popular advice?

### 8. Action and next decision

- What should the reader do in the next meeting, evaluation, pilot, or review?
- What artifact should they create: scorecard, baseline, decision memo, workflow map, risk register, or experiment?
- Which question belongs to finance, legal, product, engineering, sales, HR, or leadership?
- When should the decision be revisited?

Do not force all eight dimensions into every article. For a substantial business article, normally develop at least five and ensure the omitted dimensions do not hide a material weakness.

## `linkedin-insight-map.md` Template

```markdown
# LinkedIn Business Insight Map

## Article decision

- Professional reader:
- Work situation:
- Decision:
- Core thesis:
- Why now:
- Author advantage:

## Google-to-LinkedIn query log

| Query | Date | Result/source | Author role | Signal | Evidence status | Primary-source follow-up |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | conversation signal / practitioner experience / vendor claim / verified fact | ... |

## Recurring professional language

| Phrase or question | Who uses it | What it may reveal | Use or reject |
|---|---|---|---|

## Business depth

| Dimension | Finding | Evidence | Article implication | Confidence |
|---|---|---|---|---|
| Decision and trigger | | | | |
| Stakeholders and buying group | | | | |
| Economics | | | | |
| Workflow and implementation | | | | |
| Measurement | | | | |
| Risk and objection | | | | |
| Scenario and example | | | | |
| Action and next decision | | | | |

## Synthesis

- What most LinkedIn content repeats:
- What it leaves unresolved:
- Strongest useful disagreement:
- Original contribution this article can make:
- Material claim still requiring verification:
- Content, framework, or phrasing that must not be copied:
```

## Part 3: LinkedIn-Specific Final Humanization

Run the shared `writer/references/humanization.md` first. Then use this LinkedIn-specific pass on the audit-corrected article.

Call the stage “final humanization” or “去 AI 化编辑” in the internal audit. It is not an AI-detector bypass. Never add typos, fake memories, unsupported opinions, slang, or random fragments to make text look human.

### 1. Anchor the voice in a real professional position

Write a one-line voice brief:

```text
Experienced [role/context] writing for [reader] about [decision]; direct, evidence-led, commercially aware, willing to name limits; first person only where supplied.
```

If the user provides an approved sample, match its degree of formality, directness, paragraph rhythm, vocabulary, and first-person use without copying distinctive phrases.

### 2. Replace generic business abstraction

Find words such as `innovation`, `transformation`, `value`, `efficiency`, `strategy`, `leverage`, `alignment`, and `impact`. Keep them only when the sentence names:

- what changes;
- for whom;
- how it is measured;
- under which condition;
- compared with what baseline.

Rewrite `AI improves efficiency` into the verified, bounded mechanism—for example, which step is faster, what review work remains, and what outcome the team should measure.

### 3. Remove synthetic LinkedIn performance

Look for clusters, not isolated words:

- `In today's fast-paced...`, `in an ever-evolving landscape`, or `with the rise of...`;
- `Here's the truth`, `let that sink in`, `read that again`, or `agree?`;
- `This changes everything`, `game-changer`, `revolutionary`, `pivotal`, or `unprecedented`;
- repeated `not just X, but Y`, `it isn't about X; it's about Y`, or false binary constructions;
- repeated three-item lists, one-sentence paragraphs, and slogan-like endings;
- ceremonial transitions such as `moreover`, `furthermore`, and `in conclusion` when the logic does not need them;
- generic claims that leaders “must adapt,” teams should “embrace change,” or the future “belongs to” a group;
- a question after every section or engagement bait at the end.

Replace performance with evidence, a decision, a real trade-off, or silence.

### 4. Break template symmetry

- Allow one section to be short and another to carry the hard analysis.
- Do not give every H2 the same point/evidence/list/takeaway rhythm.
- Merge headings that exist only because a template requested them.
- Convert lists to prose when relationships matter; use a table or list when comparison matters.
- Remove the TL;DR when it merely repeats the introduction.

### 5. Make judgment visible but bounded

A business audience expects a point of view. Add qualified editorial judgment only when the evidence supports it:

- `The safer default for a small team is... because...`
- `This metric is useful for adoption, but it does not establish ROI.`
- `The argument weakens when...`
- `Finance and product will reasonably evaluate this differently.`

Do not hide behind endless balance, and do not turn a recommendation into certainty.

### 6. Verify every first-person signal

For each `I`, `we`, `our team`, `our customers`, or `in my experience`, link it to user-provided or approved material. Remove or reframe anything without provenance.

Third-person prose is better than fabricated authenticity.

### 7. Read for spoken credibility

Simulate an experienced colleague reading the article aloud. Revise passages that sound like:

- a keynote slogan;
- a vendor landing page;
- a report summary with no author judgment;
- a chain of polished aphorisms;
- a generic consultant who never names owners, costs, evidence, or constraints.

Preserve checked facts, citations, links, names, disclosures, SEO fields, and the article's actual level of certainty.

### 8. Run the integrity recheck

After final humanization, confirm:

- the business thesis and reader decision are unchanged;
- every added example is attributable or explicitly hypothetical;
- verified facts, dates, numbers, and source scope are intact;
- no commercial claim became stronger;
- no required topic phrase became awkwardly repeated;
- the strongest objection and meaningful constraint remain visible;
- title, feed commentary, and publishing pack still match the final body;
- the deterministic audit was rerun.

## Audit Record

Add this section to `linkedin-audit.md`:

```markdown
## Final LinkedIn humanization

- Voice brief:
- Generic business abstractions made concrete:
- Synthetic or templated patterns removed:
- Section symmetry revised:
- Author judgments retained or added within evidence:
- First-person provenance verified:
- Facts, links, disclosure, SEO fields, and certainty rechecked:
- Remaining voice limitation:
- AI-detector bypass claimed: no
```

The correct completion claim is “final LinkedIn humanization completed and integrity-checked,” not “100% human,” “undetectable,” or “AI-free.”
