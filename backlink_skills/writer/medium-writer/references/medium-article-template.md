# Medium Story Template

Use this reference for a complete Medium story, Publication submission draft, rewrite, or reusable authoring prompt. Adapt the structure to the story architecture. Medium rewards a story with movement, not a document that mechanically fills every heading.

## Copy-Ready Author-Assistance Prompt

```markdown
You are a Medium-native developmental editor, researcher, and author-assistance partner.

Help the author turn their original experience, expertise, notes, research, or thesis into a reader-centered Medium story. Do not invent personal material or disguise generated writing as human-created work.

## Inputs

- Author and authority basis: {{AUTHOR_MATERIAL}}
- Target reader: {{READER}}
- Reader tension: {{PROBLEM_EMOTION_DECISION_OR_CURIOSITY}}
- Core idea: {{INSIGHT_OR_TRANSFORMATION}}
- Story type: {{ESSAY_TUTORIAL_EXPLAINER_REVIEW_COMPARISON_CASE_REPORTED_ANALYSIS_LIST}}
- Primary Medium Topic: {{PRIMARY_TOPIC}}
- Supporting Topics: {{UP_TO_FOUR}}
- Publication target: {{PUBLICATION_OR_PROFILE_ONLY}}
- Current trigger: {{WHY_NOW}}
- Evidence/source material: {{SOURCES}}
- Narrative material: {{SCENES_EXAMPLES_EXPERIMENTS_CODE_DATA}}
- Target length: {{WORD_COUNT_OR_PURPOSE_BASED}}
- Required links/CTA/disclosure: {{REQUIREMENTS}}
- AI assistance status: {{OUTLINE_RESEARCH_EDITING_GENERATED_TEXT_IMAGES}}
- Must avoid: {{RISKS}}

## Workflow

1. Create the Medium story brief.
2. Research Medium search, relevant Topic pages, adjacent Topics, and Publication fit.
3. Record observations, external evidence, author advantage, and editorial inference separately.
4. Build a source and authorship ledger.
5. Generate 5-8 distinct title/subtitle pairs and select the clearest truthful pair.
6. Create an outline with narrative movement, section transitions, evidence/material, a limitation, and an ending turn.
7. Draft the story without inventing experience.
8. Fact-check current and material claims.
9. Apply the Medium editorial rubric and revise blocking/high-impact issues.
10. Humanize the corrected draft without hiding AI assistance or fabricating voice.
11. Add required AI disclosure within the first two paragraphs when generated text remains.
12. Add captions identifying AI-generated or AI-assisted images.
13. Run the deterministic Medium Markdown audit.
14. Save the public story and publishing pack separately.

## Writing Rules

- Give the reader a real scene, tension, question, claim, or decision within 100-150 words.
- Make the author's legitimate reason for telling the story visible.
- Use one H1, one subtitle, and meaningful section headings.
- Keep most paragraphs between 1 and 5 sentences.
- Make every section change the reader's understanding, not restate the premise.
- Use concrete experience, examples, code, evidence, or practical checks.
- Preserve uncertainty and meaningful counterarguments.
- Keep product, affiliate, or self-promotion secondary and disclosed.
- Do not copy another writer's structure, voice, story, examples, or ending.
- Do not add FAQ, summary bullets, or an image after every H2 unless the format truly benefits.
- End with an earned insight, image, action, or question.
- Do not claim Boost, General Distribution, Publication acceptance, paywall eligibility, or performance.

## Policy Rules

- If generated prose remains, include a clear AI-assistance disclosure within the first two paragraphs.
- If the story is primarily AI-generated, mark it as not paywall-eligible under current Medium policy.
- If AI-generated images appear, identify them in their captions.
- Treat Boost as a post-publication curation outcome, never a draft status.
- Require substantive author review before publication when original material is insufficient.

## File Outputs

- `writer/medium-writer/output/<story-slug>/medium-brief.md`
- `writer/medium-writer/output/<story-slug>/medium-topic-map.md`
- `writer/medium-writer/output/<story-slug>/source-ledger.md`
- `writer/medium-writer/output/<story-slug>/outline.md`
- `writer/medium-writer/output/<story-slug>/article-medium.md`
- `writer/medium-writer/output/<story-slug>/medium-audit.md`
- `writer/medium-writer/output/<story-slug>/medium-publishing-pack.md`
- `writer/medium-writer/output/<story-slug>/image-plan.md`
```

## Title and Subtitle Matrix

Generate distinct mechanisms, not small wording variations:

1. Experience and change: `I Stopped Measuring AI by the Time It Saved`
   - Subtitle: `A production workflow taught me to track review cost, failure recovery, and downstream decisions instead.`
2. Concrete contradiction: `The “Simple” Interface That Exhausted Our Users`
   - Subtitle: `Minimal screens can hide a high cognitive cost. Here is what the research and redesign revealed.`
3. Practical promise: `How to Evaluate an AI Agent Before It Reaches Production`
   - Subtitle: `A workflow-first method for testing quality, ownership, recovery, and real business value.`
4. Fresh evidence: `The Color Statistic That Went Unchecked for 80 Years`
   - Subtitle: `What happens when a familiar number travels farther than its original evidence.`
5. Career tension: `Programming Is Becoming a Strategy Job`
   - Subtitle: `As agents write more code, context, timing, architecture, and judgment become the developer's leverage.`
6. Personal essay image: `The Cost of Coming Back`
   - Subtitle: `I thought returning to an old habit would feel like recovery. It felt more like meeting a former self.`
7. Decision story: `I Built the Prototype in a Day. The Hard Part Started Afterward.`
   - Subtitle: `AI removed the build barrier, then exposed every unresolved product and operating decision.`
8. Myth audit: `Your Productivity System May Be Protecting You From the Work`
   - Subtitle: `Optimization can become a sophisticated form of avoidance. A smaller practice worked better for me.`

The subtitle should add audience, stakes, method, or context. It should not repeat the title in longer words.

Avoid:

- mysterious titles that conceal the actual subject;
- sensational or tabloid language;
- “You Won't Believe,” “This Changes Everything,” or unsupported certainty;
- numbers that the body cannot deliver;
- formulaic year labels unless timeliness is essential and verified;
- a product name as the whole title when the piece is meant to be editorial.

## Native Story Shell

Use only the sections that fit:

```markdown
{{OPTIONAL_KICKER}}

# {{PUBLIC_STORY_TITLE}}

*{{SUBTITLE_THAT_ADDS_CONTEXT_OR_STAKES}}*

{{OPENING_SCENE_TENSION_QUESTION_OR_CLAIM}}

{{AUTHOR_REASON_AND_READER_PROMISE}}

{{AI_ASSISTANCE_DISCLOSURE_IF_REQUIRED_WITHIN_FIRST_TWO_PARAGRAPHS}}

## {{FIRST_REAL_TURN_IN_THE_STORY}}

Develop the tension with experience, evidence, an example, or a concrete model.

## {{SECOND_TURN_OR_DEEPER_COMPLICATION}}

Change what the reader understands. Do not merely add another benefit.

## {{METHOD_CASE_OR_APPLICATION}}

Give the reader something they can examine, reproduce, decide, or use.

## {{LIMIT_COUNTERPOINT_OR_FAILURE}}

Show where the idea breaks, what it costs, or what remains uncertain.

## {{OPTIONAL_FINAL_SECTION_TITLE}}

Bring the argument, scene, or transformation into its final form.

{{EARNED_ENDING_IMAGE_INSIGHT_ACTION_OR_QUESTION}}

---

## Sources and Disclosures

- {{MATERIAL_SOURCE}}
- {{AFFILIATION_SPONSORSHIP_AFFILIATE_OR_PRODUCT_DISCLOSURE}}
- {{AI_ASSISTANCE_DISCLOSURE_REFERENCE_IF_NEEDED}}
```

Keep `medium-publishing-pack.md` outside this public story file. If an operational pack is temporarily appended for transport, place it after an explicit HTML comment and remove it before Medium publication.

## Opening Patterns

### Scene with consequence

```text
{{USER_PROVIDED_CONCRETE_MOMENT}}. The detail that mattered was not {{EXPECTED_DETAIL}}. It was {{SURPRISING_CONSEQUENCE}}.
```

### Specific contradiction

```text
The interface had fewer controls, fewer decisions, and better visual hierarchy. Users still found it exhausting.
```

### Question with stakes

```text
What does a developer become when producing code is no longer the slowest part of the job?
```

### Evidence that changes the premise

```text
{{VERIFIED_FINDING}}. The interesting part is not the number itself, but the assumption it makes impossible to keep.
```

### Decision under uncertainty

```text
We could automate the step, keep a human reviewer, or remove the feature. Each option solved a different problem—and created a different kind of risk.
```

### Tutorial failure point

```text
The demo worked on the first document. The second one exposed the missing assumption that would shape the rest of the build.
```

Do not use a first-person pattern without user-provided material.

## Section Movement Test

For each section, identify:

- What does the reader believe before this section?
- What new evidence, experience, or model appears?
- What does the reader understand afterward?
- Why must the next section follow?

If the before/after understanding is the same, merge, cut, or rewrite the section.

## Type-Specific Templates

### Personal essay

```text
Opening scene -> immediate tension -> earlier context -> complication -> honest self-implication -> changed understanding -> resonant return or open ending
```

Required material:

- at least one user-provided scene;
- consequence or emotional stake;
- reflection that changes rather than decorates the event;
- no manufactured vulnerability or invented dialogue.

### Practitioner essay

```text
Observed problem -> why common advice fails -> experience/evidence -> new model -> application -> limit -> practical implication
```

### Tutorial

```text
Reader problem -> prerequisites -> target result -> guided implementation -> verification -> common failure -> adaptation -> next step
```

Include version, environment, assumptions, and code provenance where relevant.

### Explainer

```text
Concrete question -> intuitive explanation -> evidence/examples -> misconception -> consequence -> application
```

### Review

```text
Real use context -> evaluation criteria -> observed strengths -> observed limitations -> fit by reader scenario -> disclosed judgment
```

Do not write “I tested” unless that test actually occurred and was supplied.

### Comparison

```text
Decision stakes -> criteria -> meaningful differences -> scenario tests -> trade-offs -> conditional recommendation
```

### Case study or teardown

```text
Context -> constraint -> decision -> execution -> evidence/result -> interpretation -> what transfers -> what does not
```

Never invent a client or product case to fill the structure.

### Reported analysis

```text
Current signal -> thesis -> primary evidence -> competing interpretation -> affected readers -> limits -> next signal to watch
```

### List essay

```text
Unifying argument -> substantial items with progression -> cross-item pattern -> synthesis -> next decision
```

Each item must contain insight or application. A list of links is not a Medium story.

## Source and Link Style

- Attribute important evidence in the sentence where it changes the argument.
- Prefer descriptive anchor text over raw URLs.
- Keep a short source list for materials the reader may want to inspect.
- Do not bury affiliate or ownership disclosure in the source list.
- For health, legal, financial, safety, policy, or scientific claims, preserve scope and uncertainty.
- If republishing the author's own story, set or verify the canonical link instead of pretending it is new.

## Image Pattern

Use 0-3 in-body images according to need. The featured image may be one of the in-body images because Medium requires the featured image to be present in the story.

```markdown
![{{DESCRIPTIVE_ALT_TEXT}}](./featured-medium-16x9.png)

*{{IMAGE_CAPTION_AND_CREDIT}}*
```

For AI-generated images:

```markdown
![{{DESCRIPTIVE_ALT_TEXT}}](./featured-medium-16x9.png)

*Image created with AI assistance for this story; concept and selection by the author.*
```

Use the minimum truthful caption. Do not imply original photography or measured data.

## AI Assistance Disclosure Patterns

Choose a disclosure that matches the actual workflow and place it within the first two paragraphs when generated text remains:

```text
This story was developed with AI assistance for research organization and drafting, then reviewed and revised by the author. All personal experiences and final judgments are the author's own.
```

```text
I used an AI writing tool to help structure and edit this story. The reported experience, examples, and conclusions come from my own work.
```

```text
This tutorial used AI assistance during outlining and copyediting. The implementation, tests, and technical conclusions were verified by the author.
```

Do not claim author review, testing, or personal ownership unless it actually occurred. If it has not occurred, the local draft should say `Author review required before publication` in the publishing pack rather than making a false public disclosure.

## Medium Publishing Pack Template

Save as `medium-publishing-pack.md`:

```markdown
# Medium Publishing Pack

## Story identity

- Public title:
- Subtitle:
- Kicker:
- Custom preview title:
- Custom preview subtitle:
- Target reader:
- Story promise:
- Estimated read length:
- Language:

## Topics

| Topic | Role | Body support | Verified on Medium |
|---|---|---|---|
| ... | primary / field / specific / intent / adjacent | section | yes / needs check |

Topic count: 0-5

## Publication

- Recommended path: profile-first / Publication submission
- Publication:
- Fit evidence:
- Submission requirements:
- Author submission eligibility:
- Draft or published story accepted:
- Current status: research only / eligible / submitted / pending / edits requested / approved / declined

## Preview and images

- Featured image:
- Featured alt text:
- Featured credit/caption:
- Focal point:
- In-body images and credits:
- AI image labels complete: yes / no / not applicable

## Authorship and policy

- Author material supplied:
- AI assistance used:
- Required disclosure:
- Disclosure placement: first paragraph / second paragraph / not required under current policy
- Human review status: required / completed and verified
- Primarily AI-generated: yes / no / needs author verification
- Paywall eligibility: not eligible / needs author verification / eligible based on verified human authorship
- Boost status: not claimed / verified after publication

## SEO and republication

- Original publication URL:
- Canonical setting: not needed / required / set and verified
- Medium import recommended: yes / no
- Search intent phrase:
- Indexing status: not checked / checked after publication

## Publishing choices

- Paywall: off / on after eligibility verification
- Email subscribers: yes / no / decide at publish time
- Schedule:
- Excerpt/share copy:
- Friend link: create after publication if applicable / not applicable

## Trust and permissions

- Material sources:
- Affiliation/sponsorship/affiliate disclosure:
- Image rights verified:
- Time-sensitive claims checked on:

## Measurement plan

- Review presentations, views, reads, feed clickthrough, read ratio, responses, highlights, followers, subscribers, traffic sources, and reader interests when enough data exists.
- Compare with the author's own stories of similar format and audience; do not use a universal benchmark.

## State

- Local package status:
- Publication submission status:
- Medium publication status:
```

## Optional Word Handoff

Create `article-medium.docx` only when requested. Use `article-medium.md` as the source and embed images directly. The Word file is an editorial handoff, not proof that the Medium editor, preview, Topics, canonical link, or Publication submission has been configured.

## Final Copy Gate

- The author reason is visible and true.
- Title and subtitle accurately represent the story.
- The first 100-150 words create a real reading reason.
- Sections move rather than repeat.
- Personal experience and testing have provenance.
- Material claims are verified or bounded.
- The story is not primarily a sales or traffic-acquisition page.
- Topics are relevant and no more than five.
- Publication fit and state are accurate.
- AI text assistance is disclosed when required.
- AI-generated images are captioned.
- Paywall eligibility and Boost status are conservative.
- The ending feels earned.
- The operational publishing pack is outside the public story.
