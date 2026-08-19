# LinkedIn Article Template

Use this reference for a complete LinkedIn Article, newsletter edition, rewrite, or reusable prompt. Adapt the structure to the chosen angle; do not fill every optional section mechanically.

## Copy-Ready Authoring Prompt

```markdown
You are a LinkedIn long-form editor and evidence-led thought-leadership writer.

Create a native LinkedIn Article or newsletter edition for a defined professional audience. The article must make one defensible point, help the reader make a work-related decision, and invite a concrete professional discussion.

## Inputs

- Publish as: {{PERSONAL_PROFILE_OR_PAGE}}
- Format: {{ARTICLE_OR_NEWSLETTER}}
- Newsletter theme/cadence: {{OPTIONAL}}
- Target audience: {{ROLE_SENIORITY_INDUSTRY_SITUATION}}
- Topic: {{TOPIC}}
- Reader decision: {{WHAT_THEY_SHOULD_UNDERSTAND_COMPARE_DECIDE_OR_DO}}
- Core thesis: {{ONE_SENTENCE_THESIS}}
- Expertise basis: {{USER_PROVIDED_EXPERIENCE_VERIFIED_SOURCES_OR_EDITORIAL_ANALYSIS}}
- Primary topic phrase: {{PRIMARY_TOPIC_PHRASE}}
- Related topic cluster: {{RELATED_TOPICS}}
- Current trigger: {{WHY_NOW}}
- Business context: {{STAKEHOLDERS_ECONOMICS_IMPLEMENTATION_RISK_MEASUREMENT}}
- Target length: {{WORD_COUNT}}
- CTA or discussion goal: {{CTA}}
- Required links/mentions/disclosure: {{REQUIREMENTS}}
- Must avoid: {{RISKS}}

## Workflow

1. Create the LinkedIn brief.
2. Research LinkedIn search and current conversation signals; record queries, dates, filters, observations, and inferences separately.
3. Use Google `site:linkedin.com` queries to discover additional public LinkedIn Posts, Articles/Pulse pages, newsletters, and Company material.
4. Create the business insight map covering relevant stakeholders, economics, implementation, measurement, risk, scenarios, and next decisions.
5. Build a claim-source ledger and verify material facts.
6. Generate 5-8 headline options using different mechanisms, then select the clearest accurate headline.
7. Create an outline with a hook, thesis, TL;DR when useful, 3-6 main sections, business implications, counterpoint, takeaway, and discussion question.
8. Write the draft.
9. Audit professional relevance, business depth, originality, evidence, usefulness, readability, conversation quality, and publishing completeness.
10. Fix blocking and high-impact issues.
11. Run shared humanization and the final LinkedIn-specific 去 AI 化编辑 without inventing experience or changing verified meaning.
12. Recheck facts, links, disclosure, SEO fields, first-person provenance, and certainty.
13. Run the deterministic LinkedIn Markdown audit.
14. Save the final article and LinkedIn publishing pack as separate files.

## Writing Rules

- Establish the professional tension, thesis, and reader promise within roughly 120 words.
- Use one H1 and descriptive H2 headings.
- Keep most paragraphs to 1-4 sentences.
- Put practical implications near the evidence that supports them.
- Include specific examples, checks, steps, or decision criteria.
- Develop the relevant buyer/stakeholder, economics, implementation, measurement, risk, and ownership context; normally at least five dimensions for a substantial business article.
- Include a meaningful trade-off, limitation, or counterargument.
- Use first-person events only when supplied and approved.
- Do not fabricate customers, tests, interviews, internal data, metrics, or quotes.
- Do not call a topic hot, trending, viral, best, or most popular without dated evidence.
- Avoid engagement bait, generic inspiration, inflated significance, and a sales-heavy ending.
- Replace abstract claims about transformation, value, strategy, innovation, or efficiency with an owner, mechanism, baseline, condition, or measurable consequence.
- End with one specific takeaway and one answerable professional question.
- Add a source note and disclosure when they materially affect trust.
- Keep hashtags and operational publishing notes out of the public article body.

## LinkedIn SEO Settings

- SEO title: no more than 60 characters.
- SEO description: target 140-160 characters.
- Use the primary topic phrase naturally; do not stuff variants.
- Suggest a short, readable article URL slug.

## File Outputs

- `writer/linkedin-writer/output/<article-slug>/linkedin-brief.md`
- `writer/linkedin-writer/output/<article-slug>/linkedin-topic-map.md`
- `writer/linkedin-writer/output/<article-slug>/linkedin-insight-map.md`
- `writer/linkedin-writer/output/<article-slug>/source-ledger.md`
- `writer/linkedin-writer/output/<article-slug>/outline.md`
- `writer/linkedin-writer/output/<article-slug>/article-linkedin.md`
- `writer/linkedin-writer/output/<article-slug>/linkedin-audit.md`
- `writer/linkedin-writer/output/<article-slug>/linkedin-publishing-pack.md`
- `writer/linkedin-writer/output/<article-slug>/image-plan.md`
```

## Headline Generation Matrix

Generate different headline mechanisms instead of minor rewrites:

1. Direct professional outcome: `How Product Teams Can Evaluate AI Agents Before Production`
2. Evidence-led change: `AI Adoption Is Becoming a Workforce Design Problem`
3. Decision tension: `Build or Buy an AI Agent? Start With the Workflow, Not the Model`
4. Contrarian but defensible: `Your Team Probably Does Not Need Another AI Pilot`
5. Role-specific guide: `What CHROs Need From an AI Workforce Plan`
6. Framework or playbook: `A 5-Part Operating Model for Human-AI Workflows`
7. Case or lessons: `Three Lessons From Moving an AI Workflow Into Production`
8. Current change: `What Skills-First Hiring Changes for Recruiters and Candidates`

Do not add a number unless the article truly contains that number of distinct items. Do not use fear, certainty, or novelty that the evidence cannot support.

## Recommended Native Article Structure

```markdown
# {{SELECTED_HEADLINE}}

*{{OPTIONAL_DECK_OR_SUBTITLE}}*

{{OPENING_TENSION_OR_SCENE}}

{{CORE_THESIS_AND_READER_PROMISE}}

## At a Glance

- {{TAKEAWAY_1}}
- {{TAKEAWAY_2}}
- {{TAKEAWAY_3}}

## {{H2_THAT_NAMES_THE_REAL_CHANGE_OR_PROBLEM}}

State the point first. Explain the evidence or professional context. Show who is affected and why the distinction matters.

## {{H2_THAT_EXPLAINS_THE_FRAMEWORK_OR_DECISION}}

Give the criteria, steps, or operating model. Include a concrete example or check.

## {{H2_THAT_CONNECTS_TO_IMPLEMENTATION_OR_ROLE_IMPACT}}

Explain what a practitioner, manager, executive, buyer, or candidate should do differently.

## {{H2_THAT_COVERS_THE_TRADE_OFF_OR_FAILURE_MODE}}

Present the strongest limitation, counterargument, or condition. Do not bury material risk in a footnote.

## {{OPTIONAL_H2_FOR_A_CHECKLIST_CASE_OR_NEXT_STEP}}

Give the reader a compact way to apply the article.

## The Practical Takeaway

Return to the thesis in concrete terms. State the next action, decision, or operating question.

{{ONE_ANSWERABLE_PROFESSIONAL_DISCUSSION_QUESTION}}

---

## Sources and Disclosure

- {{MATERIAL_SOURCE_OR_ATTRIBUTION}}
- {{COMMERCIAL_RELATIONSHIP_OR_NONE}}

<!-- The publishing pack below is operational and should be removed before pasting the public article body. -->

## LinkedIn Publishing Pack

- Selected headline:
- Subtitle/deck:
- Publish as:
- Format:
- SEO title:
- SEO description:
- Article URL slug:
- Cover image:
- Cover alt text:
- Feed commentary:
- Discussion question:
- Suggested hashtags:
- Mention candidates and reasons:
- Disclosure:
- Newsletter follow-up:
- Measurement plan:
```

`At a Glance` is strongly recommended for analytical, report-led, technical, and decision-guide articles. Omit it for a narrative piece when it would spoil the reading experience.

## Opening Patterns

### Professional contradiction

```text
Most teams treat {{TOPIC}} as {{COMMON_ASSUMPTION}}. The harder problem is {{REAL_PROBLEM}}.
```

### Decision point

```text
The decision is not whether {{BROAD_CHANGE}} matters. It is where to change the workflow, who owns the risk, and what evidence should count as progress.
```

### Current signal

```text
{{VERIFIED_CHANGE_OR_DATA_POINT}}. That matters less as a headline than as a change in how {{AUDIENCE}} should {{DECISION_OR_ACTION}}.
```

### Attributable practitioner observation

```text
In {{USER_PROVIDED_CONTEXT}}, I kept seeing the same failure point: {{APPROVED_OBSERVATION}}.
```

### Concrete work scene

```text
A {{ROLE}} can now {{NEW_CAPABILITY}} in minutes. The review, governance, and handoff around that output still determine whether it is useful.
```

Do not use a first-person pattern unless the underlying experience is supplied and approved.

## Section Quality Pattern

Each main section should normally contain:

1. Point: one sentence that advances the thesis.
2. Evidence or reasoning: why the point is credible.
3. Application: an example, check, method, role impact, or decision criterion.
4. Boundary: a condition, trade-off, or limitation when relevant.
5. Transition: why the next section follows.

Vary section length according to the information. Do not force every section into the same paragraph count.

## Business Depth Pattern

Across the full article—not mechanically inside every section—answer the relevant questions:

1. Decision: what must the reader or organization decide, and why now?
2. Stakeholders: who sponsors, uses, approves, blocks, pays, secures, and owns the result?
3. Economics: what is the baseline, cost, ROI hypothesis, revenue/margin effect, or hidden operational burden?
4. Implementation: what workflow, data, integration, training, adoption, or governance dependency matters?
5. Measurement: which leading indicator, outcome metric, and guardrail should be reviewed?
6. Risk: what is the strongest objection, failure mode, boundary, or non-reversible downside?
7. Scenario: what attributable or explicitly hypothetical example makes the decision concrete?
8. Action: what artifact, meeting, pilot, or review should happen next?

Do not add fake case studies or pretend a hypothetical scenario happened. Label hypothetical examples clearly.

## Type-Specific Structures

### Practitioner playbook

- problem and operating context;
- prerequisites;
- repeatable steps or framework;
- review and measurement;
- failure modes;
- next action.

### Evidence-led point of view

- current signal;
- thesis;
- evidence and interpretation;
- strongest counterargument;
- implications by role;
- practical conclusion.

### Change analysis

- what changed;
- what did not change;
- affected roles and workflows;
- near-term decision;
- risks and unknowns;
- next signal to watch.

### Decision guide

- decision and stakes;
- criteria before options;
- scenario-based comparison;
- costs, risks, and prerequisites;
- choose this if / avoid this if;
- review point after implementation.

### Career and skills guide

- labor or role change;
- capability vs tool-name distinction;
- evidence employers or clients can assess;
- learning and portfolio plan;
- limitations and market variance;
- next practical step.

### Leadership memo

- decision leaders face;
- verified external signal;
- operating implications;
- ownership and cross-functional dependencies;
- metrics and risks;
- questions for the next leadership meeting.

## Discussion Question Design

A strong discussion question is:

- specific enough to answer from work experience;
- connected to the article's unresolved tension;
- open to more than one defensible answer;
- safe to answer without revealing confidential information;
- useful even when the reader disagrees.

Good:

```text
Which part of your AI workflow is hardest to measure today: output quality, adoption, time saved, or downstream business value?
```

Weak:

```text
Do you agree? Let me know in the comments!
```

## LinkedIn Publishing Pack Template

Save this separately as `linkedin-publishing-pack.md`:

```markdown
# LinkedIn Publishing Pack

## Destination

- Publish as: {{PROFILE_OR_PAGE}}
- Format: {{ARTICLE_OR_NEWSLETTER}}
- Newsletter name/theme: {{IF_APPLICABLE}}
- Audience: {{ROLE_SENIORITY_INDUSTRY}}

## Article settings

- Headline: {{PUBLIC_HEADLINE}}
- Subtitle/deck: {{OPTIONAL}}
- SEO title: {{MAX_60_CHARACTERS}}
- SEO title length: {{COUNT}}
- SEO description: {{TARGET_140_160_CHARACTERS}}
- SEO description length: {{COUNT}}
- Article URL slug: {{SHORT_READABLE_SLUG}}
- Public visibility check: required before publishing / not checked

## Visuals

- Cover file: {{FILENAME}}
- Recommended size: 1920x1080 for a newsletter edition; verify the current preview for a standalone Article
- Cover alt text: {{ALT_TEXT}}
- In-body files: {{FILES_OR_NONE}}
- Upload status: local only / uploaded / not requested

## Feed commentary

{{60_150_WORD_CONTEXT_THAT_ADDS_A_REASON_TO_READ}}

## Conversation

- Primary discussion question: {{QUESTION}}
- Suggested hashtags: {{ZERO_TO_FIVE_OR_NONE}}
- Mention candidates: {{NAME_PAGE_AND_CONTENT_REASON_OR_NONE}}
- Comment response plan: {{WHAT_TO_CLARIFY_ASK_OR_COLLECT}}

## Trust

- Material sources: {{SUMMARY_OR_LINK_TO_SOURCE_LEDGER}}
- Disclosure: {{DISCLOSURE_OR_NONE}}
- Time-sensitive claims checked on: {{DATE}}

## Follow-up and measurement

- Follow-up angle: {{NEXT_TOPIC_OR_NONE}}
- Check after publication: article views, relevant engagement, audience demographics, profile/follower effects where exposed, newsletter email metrics if applicable, and qualitative comment themes.
- Publication status: not published / scheduled / published and verified
```

## Short Feed Post Variant

When the user wants only a LinkedIn feed post, do not use the full long-form structure. Produce:

1. A first line with a concrete professional tension.
2. 3-6 short paragraphs that deliver one idea.
3. One example, criterion, or actionable takeaway.
4. One limitation or condition when relevant.
5. One discussion question.
6. 0-5 useful hashtags.
7. A source/disclosure note when needed.

Keep a short post focused on one claim. Link to the long article only when the post delivers standalone value.

## Visual Prompt Pattern

```text
Create a 16:9 editorial cover image for a LinkedIn Article about {{TOPIC}}.
Professional audience: {{AUDIENCE}}.
Article thesis: {{THESIS}}.
Visual concept: {{SPECIFIC_WORK_SCENE_FRAMEWORK_OR_TENSION}}.
Style: credible professional editorial, clear focal point, modern but restrained, useful visual hierarchy, central safe area for platform cropping.
Avoid: generic handshake imagery, fake product UI, fabricated data, fake logos, awards, tiny text, motivational-poster styling, visual clutter.
Output: 1920x1080 or another exact 16:9 size.
```

## Final Copy Gate

- The headline promise is delivered by the body.
- The opening contains a real professional tension and a clear reader promise.
- The thesis is visible without reading the publishing pack.
- Every main section changes what the reader understands or can do.
- The article develops the business context needed for the decision rather than adding unrelated trend facts.
- Google-discovered LinkedIn material is logged as conversation evidence and material claims are independently verified.
- Evidence is attributed at the point where it matters.
- The strongest limitation is visible.
- No experience, results, quotes, or customer stories were invented.
- The closing question is specific and useful.
- SEO title and description meet LinkedIn's current settings guidance.
- The public article body is cleanly separable from the operational publishing pack.
- Final LinkedIn humanization made generic abstractions concrete, removed templated or synthetic performance, verified first-person provenance, and preserved facts, links, disclosure, SEO fields, and certainty.
- No AI-detector bypass, “100% human,” “undetectable,” or “AI-free” claim is made.
