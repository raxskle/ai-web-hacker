#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function usage() {
  console.log(
    "Usage: node audit-linkedin-markdown.mjs <article-linkedin.md> [--keyword <topic>] [--json] [--strict] [--help]"
  );
}

function parseArgs(argv) {
  const options = {
    file: "",
    keyword: "",
    json: false,
    strict: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--keyword") {
      options.keyword = argv[index + 1] ?? "";
      index += 1;
    } else if (value === "--json") {
      options.json = true;
    } else if (value === "--strict") {
      options.strict = true;
    } else if (value === "--help") {
      options.help = true;
    } else if (!options.file) {
      options.file = value;
    } else {
      throw new Error(`Unknown argument: ${value}`);
    }
  }

  return options;
}

function unicodeLength(value) {
  return Array.from(value).length;
}

function wordCount(value) {
  const normalized = value
    .replace(/[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/g, " $& ")
    .replace(/[^\p{L}\p{N}'’-]+/gu, " ")
    .trim();
  return normalized ? normalized.split(/\s+/).length : 0;
}

function stripMarkdown(value) {
  return value
    .replace(/<!--[^]*?-->/g, " ")
    .replace(/!\[[^\]]*]\([^)]+\)/g, " ")
    .replace(/\[([^\]]+)]\([^)]+\)/g, "$1")
    .replace(/`{1,3}[^`]*`{1,3}/g, " ")
    .replace(/[*_>#~|-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function removeFencedCode(markdown) {
  const visible = [];
  let inFence = false;

  for (const line of markdown.split(/\r?\n/)) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (!inFence) visible.push(line);
  }

  return visible.join("\n");
}

function splitPublishingPack(markdown) {
  const match = markdown.match(
    /(?:^|\n)##\s+(?:LinkedIn\s+)?Publishing Pack\s*$/im
  );
  if (!match || match.index === undefined) {
    return { body: markdown, pack: "", found: false };
  }

  return {
    body: markdown.slice(0, match.index),
    pack: markdown.slice(match.index).trim(),
    found: true,
  };
}

function collectHeadings(markdown) {
  const headings = [];
  const lines = markdown.split(/\r?\n/);
  let inFence = false;

  lines.forEach((line, index) => {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      return;
    }
    if (inFence) return;

    const match = line.match(/^(#{1,6})\s+(.+?)\s*$/);
    if (match) {
      headings.push({
        level: match[1].length,
        text: stripMarkdown(match[2]),
        line: index + 1,
      });
    }
  });

  return headings;
}

function collectParagraphs(markdown) {
  const paragraphs = [];
  const lines = markdown.split(/\r?\n/);
  let buffer = [];
  let startLine = 1;
  let inFence = false;

  const flush = () => {
    const text = stripMarkdown(buffer.join(" "));
    if (text) {
      paragraphs.push({
        text,
        line: startLine,
        words: wordCount(text),
        characters: unicodeLength(text),
      });
    }
    buffer = [];
  };

  lines.forEach((line, index) => {
    if (/^\s*(```|~~~)/.test(line)) {
      flush();
      inFence = !inFence;
      return;
    }
    if (inFence) return;

    const trimmed = line.trim();
    const structural =
      !trimmed ||
      /^#{1,6}\s/.test(trimmed) ||
      /^([-*+]\s|\d+\.\s)/.test(trimmed) ||
      /^>/.test(trimmed) ||
      /^\|/.test(trimmed) ||
      /^---+$/.test(trimmed) ||
      /^!\[/.test(trimmed) ||
      /^<!--/.test(trimmed);

    if (structural) {
      flush();
      return;
    }

    if (buffer.length === 0) startLine = index + 1;
    buffer.push(trimmed);
  });

  flush();
  return paragraphs;
}

function extractLabeledValue(markdown, labels) {
  for (const label of labels) {
    const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(
      `(?:^|\\n)\\s*(?:[-*]\\s*)?(?:\\*\\*)?${escaped}(?:\\*\\*)?\\s*[:：]\\s*(.+)`,
      "i"
    );
    const match = markdown.match(pattern);
    if (match) return stripMarkdown(match[1]);
  }
  return "";
}

function addFinding(findings, severity, code, message, details = {}) {
  findings.push({ severity, code, message, ...details });
}

let options;
try {
  options = parseArgs(process.argv.slice(2));
} catch (error) {
  usage();
  console.error(error.message);
  process.exit(2);
}

if (options.help) {
  usage();
  process.exit(0);
}

if (!options.file) {
  usage();
  process.exit(2);
}

const absoluteFile = path.resolve(options.file);
if (!fs.existsSync(absoluteFile)) {
  console.error(`Article not found: ${absoluteFile}`);
  process.exit(2);
}

const rawMarkdown = fs.readFileSync(absoluteFile, "utf8");
const visibleMarkdown = removeFencedCode(rawMarkdown);
const { body, pack, found: packFound } = splitPublishingPack(visibleMarkdown);
const bodyText = stripMarkdown(body);
const headings = collectHeadings(body);
const paragraphs = collectParagraphs(body);
const h1s = headings.filter((heading) => heading.level === 1);
const h2s = headings.filter((heading) => heading.level === 2);
const images = [...body.matchAll(/!\[([^\]]*)]\(([^)]+)\)/g)].map((match) => ({
  alt: match[1].trim(),
  path: match[2].trim(),
}));
const findings = [];
const metrics = {
  words: wordCount(bodyText),
  characters: unicodeLength(bodyText),
  h1Count: h1s.length,
  h2Count: h2s.length,
  paragraphCount: paragraphs.length,
  imageCount: images.length,
};

if (h1s.length !== 1) {
  addFinding(
    findings,
    "error",
    "H1_COUNT",
    `Expected exactly one public-article H1, found ${h1s.length}.`
  );
}

if (h1s.length === 1) {
  const titleLength = unicodeLength(h1s[0].text);
  metrics.headlineLength = titleLength;
  if (titleLength < 20 || titleLength > 120) {
    addFinding(
      findings,
      "warning",
      "HEADLINE_LENGTH",
      `Headline has ${titleLength} characters; confirm that it is clear and scannable. This is an editorial range, not a LinkedIn platform limit.`,
      { line: h1s[0].line }
    );
  }
}

if (h2s.length < 3) {
  addFinding(
    findings,
    "warning",
    "H2_COUNT",
    `Found ${h2s.length} H2 headings; most LinkedIn long-form articles need at least 3 useful sections.`
  );
}

if (metrics.words < 700) {
  addFinding(
    findings,
    "warning",
    "ARTICLE_SHORT",
    `Public article has about ${metrics.words} words; confirm that it has enough depth for a long-form Article.`
  );
} else if (metrics.words > 2400) {
  addFinding(
    findings,
    "warning",
    "ARTICLE_LONG",
    `Public article has about ${metrics.words} words; review whether every section earns its place.`
  );
}

const denseParagraphs = paragraphs.filter((paragraph) => paragraph.words > 90);
if (denseParagraphs.length > 0) {
  addFinding(
    findings,
    "warning",
    "DENSE_PARAGRAPHS",
    `${denseParagraphs.length} paragraph(s) exceed 90 words and may be difficult to scan on LinkedIn.`,
    { lines: denseParagraphs.slice(0, 10).map((paragraph) => paragraph.line) }
  );
}

const fragmentParagraphs = paragraphs.filter(
  (paragraph) => paragraph.words > 0 && paragraph.words <= 3
);
if (fragmentParagraphs.length >= 6) {
  addFinding(
    findings,
    "warning",
    "FRAGMENT_CLUSTER",
    `${fragmentParagraphs.length} very short paragraphs may create a performative or choppy rhythm.`,
    { lines: fragmentParagraphs.slice(0, 12).map((paragraph) => paragraph.line) }
  );
}

if (options.keyword) {
  const keyword = options.keyword.toLocaleLowerCase();
  const titleText = h1s[0]?.text.toLocaleLowerCase() ?? "";
  const firstWords = bodyText.split(/\s+/).slice(0, 140).join(" ").toLocaleLowerCase();

  if (!titleText.includes(keyword) && !firstWords.includes(keyword)) {
    addFinding(
      findings,
      "warning",
      "TOPIC_PHRASE_EARLY",
      `Primary topic phrase “${options.keyword}” was not found in the H1 or opening passage.`
    );
  }
}

const genericOpeningPatterns = [
  /in today['’]s (?:fast-paced|rapidly changing|digital) world/i,
  /nowadays,? more and more/i,
  /with the rise of/i,
  /it is (?:important|worth) (?:to note|noting) that/i,
  /(?:is|are) changing everything/i,
];

const openingText = paragraphs.slice(0, 3).map((paragraph) => paragraph.text).join(" ");
const genericOpening = genericOpeningPatterns.find((pattern) => pattern.test(openingText));
if (genericOpening) {
  addFinding(
    findings,
    "warning",
    "GENERIC_OPENING",
    "The opening contains a generic setup phrase; replace it with a concrete professional tension, evidence point, or decision."
  );
}

const hypePatterns = [
  /\bgame[- ]changer\b/gi,
  /\brevolutionary\b/gi,
  /\bgroundbreaking\b/gi,
  /\btransform everything\b/gi,
  /\bmust[- ]read\b/gi,
  /\bguaranteed\b/gi,
  /\bsecret weapon\b/gi,
  /\bunprecedented\b/gi,
];

const hypeMatches = hypePatterns.flatMap((pattern) => bodyText.match(pattern) ?? []);
if (hypeMatches.length >= 2) {
  addFinding(
    findings,
    "warning",
    "HYPE_CLUSTER",
    `Found ${hypeMatches.length} hype-style phrase occurrence(s); verify that the article remains evidence-led and professional.`
  );
}

const mechanicalStyleCategories = [
  {
    name: "ceremonial transitions",
    pattern: /\b(?:moreover|furthermore|in conclusion|to summarize|it is important to note)\b/gi,
  },
  {
    name: "synthetic business vocabulary",
    pattern: /\b(?:delve|ever-evolving landscape|pivotal|unlock(?:ing)? the power|navigate the complexities|seamlessly|paradigm shift)\b/gi,
  },
  {
    name: "performative LinkedIn prompts",
    pattern: /\b(?:here['’]s the truth|let that sink in|read that again|agree\?|thoughts\?)\b/gi,
  },
  {
    name: "repeated contrast templates",
    pattern: /\b(?:not just .{1,80} but|isn['’]t about .{1,80} it['’]s about|the question is not .{1,80} it is)\b/gi,
  },
  {
    name: "generic future claims",
    pattern: /\b(?:the future belongs to|leaders must adapt|embrace (?:the )?change|shape the future|future of work)\b/gi,
  },
];

const mechanicalStyleSignals = mechanicalStyleCategories
  .map(({ name, pattern }) => ({ name, count: (bodyText.match(pattern) ?? []).length }))
  .filter(({ count }) => count > 0);
const mechanicalStyleTotal = mechanicalStyleSignals.reduce(
  (sum, signal) => sum + signal.count,
  0
);
metrics.mechanicalStyleCategories = mechanicalStyleSignals.length;
metrics.mechanicalStyleSignals = mechanicalStyleTotal;

if (mechanicalStyleSignals.length >= 3 || mechanicalStyleTotal >= 6) {
  addFinding(
    findings,
    "warning",
    "MECHANICAL_STYLE_CLUSTER",
    `Found ${mechanicalStyleTotal} signal(s) across ${mechanicalStyleSignals.length} templated or synthetic-style categories (${mechanicalStyleSignals.map((signal) => signal.name).join(", ")}). Review the cluster during final LinkedIn humanization; no phrase alone proves AI authorship.`
  );
}

const businessDepthPatterns = [
  {
    name: "economics",
    pattern: /\b(?:ROI|return on investment|cost|budget|margin|revenue|payback|total cost of ownership)\b|成本|预算|回报|利润|收入/iu,
  },
  {
    name: "ownership and stakeholders",
    pattern: /\b(?:owner|stakeholder|decision[- ]maker|buyer|procurement|legal|finance|sponsor|approver)\b|负责人|利益相关者|决策者|采购|法务|财务|审批/iu,
  },
  {
    name: "implementation",
    pattern: /\b(?:workflow|integration|rollout|adoption|change management|operating model|deployment)\b|流程|集成|上线|采用|变革管理|运营模式|部署/iu,
  },
  {
    name: "risk and trade-offs",
    pattern: /\b(?:risk|compliance|security|failure|trade[- ]off|downside|guardrail)\b|风险|合规|安全|失败|权衡|护栏/iu,
  },
  {
    name: "measurement",
    pattern: /\b(?:metric|KPI|baseline|measure|success criteria|leading indicator|outcome)\b|指标|基线|衡量|成功标准|领先指标|结果/iu,
  },
  {
    name: "scenario or proof",
    pattern: /\b(?:case study|example|scenario|pilot|experiment|before and after)\b|案例|例子|场景|试点|实验|前后对比/iu,
  },
];

const businessDepthSignals = businessDepthPatterns
  .filter(({ pattern }) => pattern.test(bodyText))
  .map(({ name }) => name);
metrics.businessDepthCategories = businessDepthSignals.length;

if (metrics.words >= 700 && businessDepthSignals.length < 3) {
  addFinding(
    findings,
    "warning",
    "BUSINESS_DEPTH_SIGNALS",
    `Only ${businessDepthSignals.length} of 6 common business-depth signal categories were detected. Confirm that the article names the relevant economics, stakeholders, implementation, risk, measurement, and scenario context; this lexical check cannot judge true business depth.`
  );
}

const experiencePatterns = [
  /\bI (?:tested|reviewed|interviewed|spoke with|worked with|implemented|deployed)\b/gi,
  /\bin my experience\b/gi,
  /\bmy (?:clients|customers|team)\b/gi,
  /\bwe (?:achieved|increased|reduced|saved|tested|deployed)\b/gi,
  /\bour (?:clients|customers|users)\b/gi,
];

const experienceMatches = experiencePatterns.flatMap(
  (pattern) => bodyText.match(pattern) ?? []
);
if (experienceMatches.length > 0) {
  addFinding(
    findings,
    "warning",
    "EXPERIENCE_PROVENANCE",
    `Found ${experienceMatches.length} first-person experience signal(s); confirm each one is user-provided or otherwise authorized. The script cannot verify provenance.`
  );
}

const timeSensitive = /\b20\d{2}\b|\bcurrently\b|\btoday\b|\bthis (?:week|month|year)\b|[$€£]\s?\d|\b\d+(?:\.\d+)?%/i.test(
  bodyText
);
const sourceSection = /^##\s+(?:Sources|References|Sources and Disclosure|参考资料)/im.test(
  body
);
if (timeSensitive && !sourceSection) {
  addFinding(
    findings,
    "warning",
    "CURRENT_CLAIMS_WITHOUT_SOURCE_SECTION",
    "The article contains dates, current-language, prices, or percentages but no Sources/References section was detected."
  );
}

const closingWords = bodyText.split(/\s+/).slice(-180).join(" ");
if (!/[?？]/.test(closingWords)) {
  addFinding(
    findings,
    "warning",
    "DISCUSSION_QUESTION",
    "No question mark was found near the end of the public article; confirm that the close includes one specific professional discussion question."
  );
}

if (images.some((image) => !image.alt)) {
  addFinding(
    findings,
    "warning",
    "IMAGE_ALT_MISSING",
    "One or more Markdown images have empty alt text."
  );
}

const remoteImages = images.filter((image) => /^https?:\/\//i.test(image.path));
metrics.remoteImageCount = remoteImages.length;

if (!packFound) {
  addFinding(
    findings,
    "warning",
    "PUBLISHING_PACK_MISSING",
    "No LinkedIn Publishing Pack section was found. Keep operational settings separate from the public body."
  );
} else {
  const seoTitle = extractLabeledValue(pack, ["SEO title", "SEO Title"]);
  const seoDescription = extractLabeledValue(pack, [
    "SEO description",
    "SEO Description",
  ]);
  const urlSlug = extractLabeledValue(pack, [
    "Article URL slug",
    "URL slug",
    "Article URL",
  ]);
  const cover = extractLabeledValue(pack, ["Cover image", "Cover file"]);

  metrics.seoTitleLength = unicodeLength(seoTitle);
  metrics.seoDescriptionLength = unicodeLength(seoDescription);

  if (!seoTitle) {
    addFinding(
      findings,
      "warning",
      "SEO_TITLE_MISSING",
      "LinkedIn SEO title was not found in the publishing pack."
    );
  } else if (unicodeLength(seoTitle) > 60) {
    addFinding(
      findings,
      "error",
      "SEO_TITLE_LONG",
      `LinkedIn SEO title has ${unicodeLength(seoTitle)} characters; LinkedIn says titles over 60 characters are truncated.`
    );
  }

  if (!seoDescription) {
    addFinding(
      findings,
      "warning",
      "SEO_DESCRIPTION_MISSING",
      "LinkedIn SEO description was not found in the publishing pack."
    );
  } else if (
    unicodeLength(seoDescription) < 140 ||
    unicodeLength(seoDescription) > 160
  ) {
    addFinding(
      findings,
      "warning",
      "SEO_DESCRIPTION_LENGTH",
      `LinkedIn SEO description has ${unicodeLength(seoDescription)} characters; LinkedIn recommends 140-160.`
    );
  }

  if (!urlSlug) {
    addFinding(
      findings,
      "warning",
      "URL_SLUG_MISSING",
      "No suggested LinkedIn Article URL slug was found in the publishing pack."
    );
  }

  if (!cover) {
    addFinding(
      findings,
      "warning",
      "COVER_MISSING",
      "No cover image filename or direction was found in the publishing pack."
    );
  }

  const hashtagMatches = pack.match(/#[\p{L}\p{N}_]+/gu) ?? [];
  metrics.hashtagCount = hashtagMatches.length;
  if (hashtagMatches.length > 5) {
    addFinding(
      findings,
      "warning",
      "HASHTAG_COUNT",
      `Publishing pack contains ${hashtagMatches.length} hashtags; keep only labels that improve topic clarity.`
    );
  }
}

const bodyHashtags = body.match(/#[\p{L}\p{N}_]+/gu) ?? [];
if (bodyHashtags.length > 0) {
  addFinding(
    findings,
    "warning",
    "HASHTAGS_IN_ARTICLE_BODY",
    `Found ${bodyHashtags.length} hashtag(s) in the public article body; operational hashtags usually belong in the sharing commentary.`
  );
}

const result = {
  file: absoluteFile,
  verdict: findings.some((finding) => finding.severity === "error")
    ? "FAIL"
    : findings.some((finding) => finding.severity === "warning")
      ? "REVIEW"
      : "PASS",
  metrics,
  findings,
  limits: [
    "This audit does not verify facts, originality, professional authority, or publication state.",
    "Editorial word, headline, paragraph, image, and hashtag ranges are guidance rather than LinkedIn hard limits unless explicitly stated.",
    "Mechanical-style and business-depth checks are lexical heuristics. They cannot determine human or AI authorship, voice quality, or decision usefulness.",
    "A clean result does not predict reach, engagement, or business impact.",
  ],
};

if (options.json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`LinkedIn Markdown audit: ${result.verdict}`);
  console.log(`File: ${result.file}`);
  console.log(
    `Metrics: ${metrics.words} words, ${metrics.h1Count} H1, ${metrics.h2Count} H2, ${metrics.paragraphCount} paragraphs, ${metrics.imageCount} in-body images`
  );

  if (findings.length === 0) {
    console.log("No deterministic findings.");
  } else {
    for (const finding of findings) {
      const location = finding.line
        ? ` line ${finding.line}`
        : finding.lines
          ? ` lines ${finding.lines.join(", ")}`
          : "";
      console.log(`[${finding.severity.toUpperCase()}] ${finding.code}${location}: ${finding.message}`);
    }
  }

  console.log("Limit: deterministic checks only; no performance prediction or factual verification.");
}

const hasError = findings.some((finding) => finding.severity === "error");
const hasWarning = findings.some((finding) => finding.severity === "warning");
if (hasError || (options.strict && hasWarning)) {
  process.exit(1);
}
