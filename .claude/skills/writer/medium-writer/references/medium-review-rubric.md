# Medium Long-form Review Rubric

Use this rubric after the deterministic Markdown audit and before publishing or submitting to a publication. The script checks structure and packaging; this rubric judges what requires editorial judgment.

## Pass Standard

A story passes only when all of the following are true:

- Average editorial score is at least 4.0 out of 5.
- No dimension scores below 3.
- No blocker remains open.
- The deterministic audit has been run and its findings are resolved or explicitly accepted.
- The named author has reviewed the final copy.
- AI assistance and AI-generated imagery are handled according to the current Medium policy.

Do not describe a draft as “Boost-ready,” “accepted,” or likely to achieve a particular performance result. Those are Medium or publication decisions.

## Immediate Blockers

Stop the release when any of these are present:

- Invented first-person experience, scene, customer, experiment, result, quote, or credential.
- A primarily AI-generated story is marked as eligible for the paywall or presented as human-authored.
- Material AI-generated prose remains but the required disclosure is absent from the first two paragraphs.
- AI-generated or AI-assisted images are not labeled in their captions.
- Copied, lightly rewritten, or materially derivative passages.
- A central factual claim lacks adequate support.
- The title, subtitle, preview, or cover overpromises or misrepresents the story.
- Irrelevant Topics, keyword stuffing, mass mentions, or other distribution manipulation.
- Material affiliation, sponsorship, or conflict of interest is undisclosed.
- Unsafe medical, legal, financial, security, or other high-stakes instruction is presented without appropriate care and sourcing.
- The package falsely claims publication acceptance, Boost selection, distribution, earnings, traffic, or engagement.

## Nine Editorial Dimensions

Score each dimension from 1 to 5. Add one concise reason and one specific revision when the score is below 4.

### 1. Author Reason and Authenticity

- **5:** The author has a clear, credible reason to write the story; personal material is attributable and meaningfully shapes the argument.
- **4:** The perspective is credible and specific, with only minor generic passages.
- **3:** The draft has a point of view but could have been written by almost anyone.
- **2:** First-person language is decorative, unverifiable, or disconnected from the insight.
- **1:** Experience or authority appears fabricated or misleading.

### 2. Originality and Insight

- **5:** The story offers a distinctive model, synthesis, observation, or counterintuitive conclusion and shows how it was derived.
- **4:** Familiar material is recombined into a useful, clearly owned perspective.
- **3:** Competent explanation with limited novelty.
- **2:** Mostly summarizes common advice or source material.
- **1:** Copied, derivative, or empty trend commentary.

### 3. Reader Value

- **5:** A defined reader receives a concrete change in understanding or action, with tradeoffs and next steps.
- **4:** The payoff is useful and mostly actionable.
- **3:** The lesson is present but broad or uneven.
- **2:** The piece promises value without delivering enough substance.
- **1:** No identifiable reader payoff.

### 4. Narrative Architecture

- **5:** The opening creates a real question; every section advances it; the ending resolves the argument without merely repeating it.
- **4:** The flow is clear with only minor repetition or detours.
- **3:** The structure is understandable but list-like or mechanically segmented.
- **2:** Sections can be reordered without changing meaning; momentum is weak.
- **1:** The story has no coherent progression.

### 5. Evidence and Trust

- **5:** Central claims are supported by primary or authoritative sources, observed evidence, or clearly labeled author experience; fact, inference, and opinion are distinct.
- **4:** Evidence is strong with small gaps in secondary claims.
- **3:** Most claims are plausible but sourcing or attribution is inconsistent.
- **2:** Important claims rely on weak sources, vague attribution, or unverified numbers.
- **1:** Core claims are unsupported, false, or misleading.

### 6. Prose Craft and Readability

- **5:** Voice is natural and precise; paragraphs vary in rhythm; transitions carry meaning; examples clarify rather than decorate.
- **4:** Clean, readable prose with a few generic or overlong passages.
- **3:** Serviceable but repetitive, abstract, or overly templated.
- **2:** Choppy fragments, padded sections, jargon, or obvious AI-style phrasing dominate.
- **1:** Difficult to follow or not publication-ready.

### 7. Title, Subtitle, and Preview Integrity

- **5:** The public title and subtitle create a specific, accurate promise; the opening fulfills it immediately; the cover reinforces rather than exaggerates.
- **4:** Accurate and useful with minor sharpening needed.
- **3:** Understandable but generic, crowded, or weakly differentiated.
- **2:** Click-driven framing or a mismatch with the body.
- **1:** Deceptive or materially misleading.

### 8. Topic and Publication Fit

- **5:** One clear primary Topic, up to four genuinely relevant supporting Topics, and a publication match backed by current rules and recent story evidence.
- **4:** Topics are accurate and the publication fit is plausible, with minor positioning gaps.
- **3:** Topics are acceptable but broad; publication research is thin.
- **2:** Topic selection is opportunistic or the target publication is poorly matched.
- **1:** Topic spam, stale assumptions, or rule violations.

### 9. Policy and Publishing Completeness

- **5:** Authorship, disclosure, image labels, rights, canonical choice, publication status, Topics, preview fields, and release settings are all explicit and internally consistent.
- **4:** Complete apart from minor operational details.
- **3:** Publishable after resolving a small number of missing fields.
- **2:** Important disclosure, rights, canonical, or publication information is unresolved.
- **1:** A policy blocker or materially false publishing claim remains.

## Revision Order

Revise in this order so surface polish does not hide structural problems:

1. Resolve blockers and provenance issues.
2. Reconfirm the reader, author reason, and central promise.
3. Strengthen the argument, evidence, and original insight.
4. Repair narrative movement and section order.
5. Tighten title, subtitle, opening, and ending.
6. Improve prose rhythm, examples, links, and images.
7. Finalize Topics, publication fit, disclosure, canonical choice, and publishing pack.
8. Re-run the deterministic audit and this rubric.

## `medium-audit.md` Template

```markdown
# Medium Editorial Audit

## Verdict

- Status: PASS / REVISE / BLOCKED
- Average editorial score: X.X / 5
- Deterministic audit: PASS / REVIEW / FAIL
- Human review completed by: [name or pending]
- Reviewed at: YYYY-MM-DD

## Blockers

| Blocker | Status | Evidence or action |
|---|---|---|
| [none or exact blocker] | Open / Resolved | [note] |

## Scorecard

| Dimension | Score | Reason | Required revision |
|---|---:|---|---|
| Author reason and authenticity | /5 | | |
| Originality and insight | /5 | | |
| Reader value | /5 | | |
| Narrative architecture | /5 | | |
| Evidence and trust | /5 | | |
| Prose craft and readability | /5 | | |
| Title, subtitle, and preview integrity | /5 | | |
| Topic and publication fit | /5 | | |
| Policy and publishing completeness | /5 | | |

## Deterministic Findings

Paste or summarize the script output here. Separate errors, warnings, and accepted exceptions.

## Claim and Link Review

| Claim or link | Evidence checked | Result | Notes |
|---|---|---|---|

## Authorship and AI Review

- Named author:
- Human contribution:
- AI assistance used:
- Generated prose remains in final copy: Yes / No
- Disclosure required: Yes / No
- Disclosure text and placement:
- AI-generated or assisted images: Yes / No
- Image captions verified: Yes / No / N/A
- Paywall eligibility statement verified: Yes / No / N/A

## Final Publishing Checks

- [ ] Public title and subtitle match the story.
- [ ] Cover rights, credit, alt text, and focal point are resolved.
- [ ] No more than five relevant Topics are selected.
- [ ] Target publication rules were checked on the recorded date.
- [ ] Publication status is factual, not predicted.
- [ ] Canonical choice is explicit.
- [ ] Material affiliations are disclosed.
- [ ] No unverified performance or distribution claim remains.
```

## Deterministic Versus Editorial Boundary

The audit script can count headings, paragraphs, images, Topics, and packaging fields. It cannot determine truth, originality, lived experience, copyright ownership, publication fit, policy eligibility, or whether a story deserves distribution. Those require source review and human editorial judgment.
