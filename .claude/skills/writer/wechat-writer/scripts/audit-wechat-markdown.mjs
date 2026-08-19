#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function usage() {
  console.error(
    "Usage: node audit-wechat-markdown.mjs <article.md> [--keyword <topic>] [--json] [--strict]"
  );
}

function parseArgs(argv) {
  const options = {
    file: "",
    keyword: "",
    json: false,
    strict: false,
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

function stripMarkdown(value) {
  return value
    .replace(/!\[[^\]]*]\([^)]+\)/g, " ")
    .replace(/\[([^\]]+)]\([^)]+\)/g, "$1")
    .replace(/`{1,3}[^`]*`{1,3}/g, " ")
    .replace(/[*_>#~-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function collectParagraphs(lines) {
  const paragraphs = [];
  let buffer = [];
  let inFence = false;

  const flush = () => {
    const text = stripMarkdown(buffer.join(" "));
    if (text) {
      paragraphs.push({
        text,
        line: Math.max(1, currentStart),
        length: unicodeLength(text),
      });
    }
    buffer = [];
  };

  let currentStart = 1;

  lines.forEach((line, index) => {
    if (/^(```|~~~)/.test(line.trim())) {
      flush();
      inFence = !inFence;
      return;
    }
    if (inFence) return;

    const trimmed = line.trim();
    const structural =
      !trimmed ||
      /^#{1,6}\s/.test(trimmed) ||
      /^([-*+]|\d+\.)\s/.test(trimmed) ||
      /^>/.test(trimmed) ||
      /^\|/.test(trimmed) ||
      /^---+$/.test(trimmed) ||
      /^!\[/.test(trimmed);

    if (structural) {
      flush();
      return;
    }

    if (buffer.length === 0) currentStart = index + 1;
    buffer.push(trimmed);
  });

  flush();
  return paragraphs;
}

function collectHeadings(lines) {
  const headings = [];
  let inFence = false;

  lines.forEach((line, index) => {
    if (/^(```|~~~)/.test(line.trim())) {
      inFence = !inFence;
      return;
    }
    if (inFence) return;

    const match = line.match(/^(#{1,6})\s+(.+?)\s*$/);
    if (match) {
      headings.push({
        level: match[1].length,
        line: index + 1,
        text: match[2],
      });
    }
  });

  return headings;
}

function removeFencedCode(lines) {
  const visibleLines = [];
  let inFence = false;

  for (const line of lines) {
    if (/^(```|~~~)/.test(line.trim())) {
      inFence = !inFence;
      continue;
    }
    if (!inFence) visibleLines.push(line);
  }

  return visibleLines.join("\n");
}

function addFinding(target, severity, code, message, details = {}) {
  target.push({ severity, code, message, ...details });
}

let options;
try {
  options = parseArgs(process.argv.slice(2));
} catch (error) {
  usage();
  console.error(error.message);
  process.exit(2);
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

const markdown = fs.readFileSync(absoluteFile, "utf8");
const lines = markdown.split(/\r?\n/);
const analysisMarkdown = removeFencedCode(lines).replace(/`[^`\n]+`/g, "");
const findings = [];
const headings = collectHeadings(lines);
const h1s = headings.filter((heading) => heading.level === 1);
const h2s = headings.filter((heading) => heading.level === 2).length;
const paragraphs = collectParagraphs(lines);
const longParagraphs = paragraphs.filter((item) => item.length > 180);
const veryShortParagraphs = paragraphs.filter(
  (item) => item.length > 0 && item.length < 8
);
const bodyText = stripMarkdown(analysisMarkdown);
const bodyLength = unicodeLength(bodyText);

if (h1s.length !== 1) {
  addFinding(
    findings,
    "error",
    "H1_COUNT",
    `Expected exactly one H1, found ${h1s.length}.`
  );
}

if (h1s.length === 1) {
  const titleLength = unicodeLength(stripMarkdown(h1s[0].text));
  if (titleLength < 12 || titleLength > 30) {
    addFinding(
      findings,
      "warning",
      "TITLE_LENGTH",
      `Title has ${titleLength} characters; 12-30 is a common editorial range, not a platform limit.`,
      { line: h1s[0].line }
    );
  }
}

if (h2s < 2) {
  addFinding(
    findings,
    "warning",
    "H2_COUNT",
    `Found ${h2s} H2 headings; most long-form WeChat articles need at least 2 useful sections.`
  );
}

if (bodyLength < 600) {
  addFinding(
    findings,
    "warning",
    "BODY_SHORT",
    `Article has about ${bodyLength} visible characters; confirm that the topic is intentionally concise.`
  );
}

if (longParagraphs.length > 0) {
  addFinding(
    findings,
    "warning",
    "LONG_PARAGRAPHS",
    `${longParagraphs.length} paragraph(s) exceed 180 characters and may be dense on mobile.`,
    { lines: longParagraphs.slice(0, 8).map((item) => item.line) }
  );
}

if (veryShortParagraphs.length >= 6) {
  addFinding(
    findings,
    "warning",
    "FRAGMENT_CLUSTER",
    `${veryShortParagraphs.length} very short paragraph(s) may create a choppy, performative rhythm.`,
    { lines: veryShortParagraphs.slice(0, 10).map((item) => item.line) }
  );
}

const digestMatch = analysisMarkdown.match(
  /(?:^|\n)(?:>\s*)?(?:\*\*)?(?:摘要|Digest)(?:\*\*)?[：:]\s*(.+)/i
);
if (!digestMatch) {
  addFinding(
    findings,
    "warning",
    "DIGEST_MISSING",
    "No 摘要/Digest line was found for the WeChat publishing pack."
  );
} else {
  const digestLength = unicodeLength(stripMarkdown(digestMatch[1]));
  if (digestLength < 40 || digestLength > 120) {
    addFinding(
      findings,
      "warning",
      "DIGEST_LENGTH",
      `Digest has ${digestLength} characters; 60-100 is the default editorial target.`
    );
  }
}

if (options.keyword) {
  const normalizedKeyword = options.keyword.toLocaleLowerCase();
  const titleAndLead = `${h1s[0]?.text ?? ""}\n${bodyText.slice(0, 220)}`.toLocaleLowerCase();
  if (!titleAndLead.includes(normalizedKeyword)) {
    addFinding(
      findings,
      "warning",
      "TOPIC_NOT_EARLY",
      `Core topic "${options.keyword}" does not appear in the H1 or early article text.`
    );
  }
}

const referenceHeading = headings.some(
  (heading) =>
    heading.level === 2 &&
    /^(参考资料|来源|References|Sources)$/i.test(heading.text.trim())
);
const containsCheckableSignals =
  /\b(19|20)\d{2}\b/.test(analysisMarkdown) ||
  /\d+(?:\.\d+)?%/.test(analysisMarkdown) ||
  /[¥￥$€£]\s?\d/.test(analysisMarkdown) ||
  /“[^”]{8,}”/.test(analysisMarkdown);

if (containsCheckableSignals && !referenceHeading) {
  addFinding(
    findings,
    "warning",
    "SOURCES_SECTION_MISSING",
    "The article contains dates, numbers, prices, percentages, or quotations but no reference section was found."
  );
}

const markdownLinks = Array.from(
  analysisMarkdown.matchAll(/(?<!!)\[[^\]]+]\((https?:\/\/[^)]+)\)/g)
);
if (markdownLinks.length > 5) {
  addFinding(
    findings,
    "warning",
    "MANY_EXTERNAL_LINKS",
    `${markdownLinks.length} external inline links were found; WeChat copy should remain understandable without them.`
  );
}

const imageMatches = Array.from(
  analysisMarkdown.matchAll(/!\[[^\]]*]\(([^)]+)\)/g)
);
const missingImages = [];
for (const match of imageMatches) {
  const imagePath = match[1].trim().replace(/^<|>$/g, "");
  if (/^(https?:|data:)/i.test(imagePath)) continue;
  const resolved = path.resolve(path.dirname(absoluteFile), imagePath);
  if (!fs.existsSync(resolved)) missingImages.push(imagePath);
}
if (missingImages.length > 0) {
  addFinding(
    findings,
    "error",
    "MISSING_IMAGES",
    `${missingImages.length} local image reference(s) do not exist.`,
    { paths: missingImages }
  );
}

const clichePatterns = [
  ["CLICHE_FAST_WORLD", /在这个[^。\n]{0,16}(时代|世界)/g],
  ["CLICHE_WITH_RISE", /随着[^。\n]{0,24}(发展|兴起|普及|进步)/g],
  ["CLICHE_WORTH_NOTING", /值得注意的是/g],
  ["CLICHE_EASY_TO_SEE", /不难(看出|发现)/g],
  ["CLICHE_LETS", /让我们(一起|来)/g],
  ["CLICHE_SUMMARY", /(综上所述|总而言之|未来可期|拭目以待)/g],
];

for (const [code, pattern] of clichePatterns) {
  const matches = analysisMarkdown.match(pattern) ?? [];
  if (matches.length > 0) {
    addFinding(
      findings,
      "warning",
      code,
      `Found ${matches.length} possible generic phrase(s): ${[...new Set(matches)].join("、")}.`
    );
  }
}

const personalEventPatterns = [
  /我有一个朋友/g,
  /我的(朋友|同事|客户)曾/g,
  /那天我/g,
  /去年我/g,
  /我亲自(测试|体验|采访|见证)/g,
];
const personalSignals = personalEventPatterns.flatMap(
  (pattern) => analysisMarkdown.match(pattern) ?? []
);
if (personalSignals.length > 0) {
  addFinding(
    findings,
    "warning",
    "PERSONAL_PROVENANCE",
    "Possible first-person event material was found; verify it is explicitly supplied for this task.",
    { samples: [...new Set(personalSignals)].slice(0, 6) }
  );
}

const result = {
  file: absoluteFile,
  summary: {
    h1Count: h1s.length,
    h2Count: h2s,
    visibleCharacters: bodyLength,
    paragraphCount: paragraphs.length,
    imageCount: imageMatches.length,
    externalLinkCount: markdownLinks.length,
    errors: findings.filter((item) => item.severity === "error").length,
    warnings: findings.filter((item) => item.severity === "warning").length,
  },
  findings,
  note:
    "This script checks deterministic Markdown and readability signals only. It cannot verify facts, authorship, originality, or editorial quality.",
};

if (options.json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`WeChat Markdown audit: ${absoluteFile}`);
  console.log(
    `H1 ${result.summary.h1Count} | H2 ${result.summary.h2Count} | ` +
      `${result.summary.visibleCharacters} visible chars | ` +
      `${result.summary.errors} error(s) | ${result.summary.warnings} warning(s)`
  );
  if (findings.length === 0) {
    console.log("No deterministic issues found.");
  } else {
    for (const finding of findings) {
      const location = finding.line
        ? ` line ${finding.line}`
        : finding.lines
          ? ` lines ${finding.lines.join(",")}`
          : "";
      console.log(
        `[${finding.severity.toUpperCase()}] ${finding.code}${location}: ${finding.message}`
      );
    }
  }
  console.log(result.note);
}

const hasErrors = result.summary.errors > 0;
const hasWarnings = result.summary.warnings > 0;
process.exit(hasErrors || (options.strict && hasWarnings) ? 1 : 0);
