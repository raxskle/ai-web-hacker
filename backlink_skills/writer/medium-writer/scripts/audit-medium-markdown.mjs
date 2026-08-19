#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function usage() {
  console.log(`Usage:
  node audit-medium-markdown.mjs <article-medium.md> [options]

Options:
  --topic <topic>   Expected primary Medium Topic
  --pack <file>     Separate medium-publishing-pack.md file
  --ai-assisted    Generated prose remains and disclosure is required
  --ai-images      AI-generated or AI-assisted images are present
  --strict         Treat warnings as failures
  --json           Print machine-readable JSON
  --help           Show this help`);
}

function parseArgs(argv) {
  const options = {
    file: null,
    pack: null,
    topic: null,
    aiAssisted: false,
    aiImages: false,
    strict: false,
    json: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help") {
      usage();
      process.exit(0);
    } else if (arg === "--topic") {
      options.topic = argv[i + 1];
      if (!options.topic) throw new Error("--topic requires a value");
      i += 1;
    } else if (arg === "--pack") {
      options.pack = argv[i + 1];
      if (!options.pack) throw new Error("--pack requires a value");
      i += 1;
    } else if (arg === "--ai-assisted") {
      options.aiAssisted = true;
    } else if (arg === "--ai-images") {
      options.aiImages = true;
    } else if (arg === "--strict") {
      options.strict = true;
    } else if (arg === "--json") {
      options.json = true;
    } else if (arg.startsWith("--")) {
      throw new Error(`Unknown option: ${arg}`);
    } else if (!options.file) {
      options.file = arg;
    } else {
      throw new Error(`Unexpected argument: ${arg}`);
    }
  }

  if (!options.file) throw new Error("A Markdown file is required");
  return options;
}

function stripFrontmatter(markdown) {
  return markdown.replace(/^---\s*\n[\s\S]*?\n---\s*\n/, "");
}

function stripCode(markdown) {
  return markdown
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`[^`\n]+`/g, "");
}

function plainText(markdown) {
  return stripCode(markdown)
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[>*_~|]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function words(markdown) {
  const text = plainText(markdown);
  if (!text) return [];
  return text.match(/[\p{L}\p{N}]+(?:['’.-][\p{L}\p{N}]+)*/gu) ?? [];
}

function paragraphs(markdown) {
  return stripCode(markdown)
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter((part) => {
      if (!part) return false;
      if (/^#{1,6}\s/.test(part)) return false;
      if (/^(!?\[[^\]]*\]\([^)]*\)\s*)+$/.test(part)) return false;
      if (/^(?:[-*+] |\d+[.)] )/m.test(part)) return false;
      if (/^\|.*\|$/m.test(part)) return false;
      return true;
    });
}

function section(markdown, heading, nextHeading) {
  const start = new RegExp(`^##\\s+${heading}\\s*$`, "im").exec(markdown);
  if (!start) return "";
  const tail = markdown.slice(start.index + start[0].length);
  if (!nextHeading) {
    const end = /^##\s+/m.exec(tail);
    return end ? tail.slice(0, end.index) : tail;
  }
  const end = new RegExp(`^##\\s+${nextHeading}\\s*$`, "im").exec(tail);
  return end ? tail.slice(0, end.index) : tail;
}

function labelValue(markdown, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = new RegExp(`^-\\s*${escaped}:\\s*(.+)$`, "im").exec(markdown);
  return match?.[1]?.trim() ?? "";
}

function firstBodyParagraphs(markdown, limit = 2) {
  const withoutFrontmatter = stripFrontmatter(markdown);
  const lines = withoutFrontmatter.split("\n");
  const firstH1 = lines.findIndex((line) => /^#\s+/.test(line));
  const bodyLines = lines.slice(firstH1 >= 0 ? firstH1 + 1 : 0);
  const firstContent = bodyLines.findIndex((line) => line.trim());
  if (firstContent >= 0 && /^\s*[_*][^*_].*[_*]\s*$/.test(bodyLines[firstContent])) {
    bodyLines.splice(firstContent, 1);
  }
  const afterTitle = bodyLines.join("\n");
  return paragraphs(afterTitle).slice(0, limit);
}

function countTopicRows(pack) {
  const topics = section(pack, "Topics", "Publication");
  if (!topics) return 0;
  return topics
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => /^\|.*\|$/.test(line))
    .filter((line) => !/^\|\s*:?-+/.test(line))
    .filter((line) => !/^\|\s*Topic\s*\|/i.test(line)).length;
}

function addFinding(findings, severity, code, message) {
  findings.push({ severity, code, message });
}

function containsAiDisclosure(text) {
  return /(?:\bAI\b|artificial intelligence).{0,100}\b(?:assist(?:ance|ed)?|generat(?:ed|ion)|draft(?:ed|ing)?|edit(?:ed|ing)?|help(?:ed)?|tool)\b|\b(?:assist(?:ance|ed)?|generat(?:ed|ion)|draft(?:ed|ing)?|edit(?:ed|ing)?|help(?:ed)?|tool)\b.{0,100}(?:\bAI\b|artificial intelligence)/is.test(text);
}

function audit(markdown, options, separatePack = "") {
  const marker = /^##\s+Medium Publishing Pack\s*$/im.exec(markdown);
  const body = marker ? markdown.slice(0, marker.index).trim() : markdown.trim();
  const pack = separatePack.trim() || (marker ? markdown.slice(marker.index).trim() : "");
  const findings = [];
  const cleanBody = stripFrontmatter(body);
  const h1s = [...cleanBody.matchAll(/^#\s+(.+)$/gm)];
  const h2Count = (cleanBody.match(/^##\s+/gm) ?? []).length;
  const bodyWords = words(cleanBody).length;
  const bodyParagraphs = paragraphs(cleanBody);
  const images = [...cleanBody.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g)];

  if (h1s.length !== 1) {
    addFinding(findings, "error", "H1_COUNT", `Expected exactly one H1; found ${h1s.length}.`);
  }

  const title = h1s[0]?.[1]?.trim() ?? "";
  if (title && (words(title).length < 3 || title.length > 120)) {
    addFinding(findings, "warning", "TITLE_RANGE", "The title looks unusually short or long for an accurate Medium preview; review it editorially.");
  }

  const titleLine = cleanBody.split("\n").findIndex((line) => /^#\s+/.test(line));
  const afterTitle = cleanBody.split("\n").slice(titleLine + 1, titleLine + 7);
  const subtitle = afterTitle.find((line) => /^\s*[_*][^*_].*[_*]\s*$/.test(line));
  if (!subtitle) {
    addFinding(findings, "warning", "SUBTITLE_MISSING", "No italic subtitle was found near the H1. Confirm the public subtitle in the publishing pack.");
  }

  if (h2Count < 3) {
    addFinding(findings, "warning", "SECTION_DEPTH", `Found ${h2Count} H2 sections; confirm the story has enough narrative development for its promise.`);
  }

  if (bodyWords < 700 || bodyWords > 2600) {
    addFinding(findings, "warning", "WORD_COUNT", `Body word count is ${bodyWords}. This is an editorial range check, not a Medium platform limit.`);
  }

  const longParagraphs = bodyParagraphs
    .map((paragraph, index) => ({ index: index + 1, count: words(paragraph).length }))
    .filter(({ count }) => count > 100);
  if (longParagraphs.length) {
    addFinding(findings, "warning", "LONG_PARAGRAPHS", `${longParagraphs.length} prose paragraph(s) exceed 100 words; review reading rhythm.`);
  }

  const shortParagraphs = bodyParagraphs.filter((paragraph) => words(paragraph).length > 0 && words(paragraph).length <= 5).length;
  if (bodyParagraphs.length >= 8 && shortParagraphs / bodyParagraphs.length > 0.35) {
    addFinding(findings, "warning", "FRAGMENT_CLUSTER", "More than 35% of prose paragraphs contain five words or fewer; check for artificial one-line fragmentation.");
  }

  const opening = firstBodyParagraphs(cleanBody, 3).join(" ");
  if (/^(in today['’]s|in the (?:fast-paced|ever-evolving)|have you ever|in an era where|in a world where)\b/i.test(opening)) {
    addFinding(findings, "warning", "GENERIC_OPENING", "The opening begins with a common generic pattern; replace it with a specific tension, scene, observation, or claim.");
  }

  if (/\b(revolutionary|game[- ]changing|ultimate guide|unlock the power|skyrocket|transform everything)\b/i.test(`${title} ${opening}`)) {
    addFinding(findings, "warning", "HYPE_LANGUAGE", "Title or opening contains promotional or inflated language; confirm it is specific and supportable.");
  }

  if (/\b(I|we|my|our)\s+(?:built|tested|interviewed|ran|learned|discovered|made|lost|earned|managed|shipped)\b/i.test(cleanBody)) {
    addFinding(findings, "warning", "EXPERIENCE_PROVENANCE", "First-person experience claims are present. Verify them with the named author; the script cannot establish provenance.");
  }

  const sourcesPresent = /^##\s+(?:Sources|References|Further Reading)\s*$/im.test(cleanBody);
  const timeSensitiveClaims = /(?:\b20\d{2}\b|\$\s?\d|\b\d+(?:\.\d+)?%|\b(?:today|currently|now)\b)/i.test(cleanBody);
  if (timeSensitiveClaims && !sourcesPresent) {
    addFinding(findings, "warning", "SOURCES_SECTION", "Dates, prices, percentages, or current-state language appear without a Sources, References, or Further Reading section.");
  }

  for (const image of images) {
    if (!image[1].trim()) {
      addFinding(findings, "warning", "EMPTY_IMAGE_ALT", `Image ${image[2]} has empty alt text.`);
    }
  }

  if (options.topic) {
    const topic = options.topic.toLocaleLowerCase();
    const positioning = `${title} ${opening}`.toLocaleLowerCase();
    if (!positioning.includes(topic)) {
      addFinding(findings, "warning", "PRIMARY_TOPIC_SIGNAL", `The expected primary Topic “${options.topic}” is not explicit in the title or opening. Confirm the positioning is still clear.`);
    }
  }

  if (!pack) {
    addFinding(findings, "warning", "PUBLISHING_PACK_MISSING", "No appended Medium Publishing Pack was found. A separate medium-publishing-pack.md is also acceptable but must be reviewed manually.");
  } else {
    const topicCount = countTopicRows(pack);
    if (topicCount < 1 || topicCount > 5) {
      addFinding(findings, "error", "TOPIC_COUNT", `Publishing pack contains ${topicCount} Topic table row(s); use one to five relevant Medium Topics.`);
    }

    const requiredLabels = [
      "Public title",
      "Subtitle",
      "Publication / current status",
      "Human review status",
      "AI assistance used",
      "Required disclosure",
      "Disclosure placement",
      "Paywall eligibility",
      "Boost status",
      "Canonical setting",
      "Featured image",
    ];
    for (const label of requiredLabels) {
      if (!labelValue(pack, label)) {
        addFinding(findings, "warning", "PACK_FIELD_MISSING", `Publishing pack is missing “${label}”.`);
      }
    }
  }

  if (options.aiAssisted) {
    const disclosureZone = firstBodyParagraphs(cleanBody, 2).join(" ");
    if (!containsAiDisclosure(disclosureZone)) {
      addFinding(findings, "error", "AI_DISCLOSURE", "--ai-assisted was set, but no AI disclosure was found within the first two prose paragraphs.");
    }
    if (pack && !/^-\s*Required disclosure:\s*(?!No\b).+/im.test(pack)) {
      addFinding(findings, "error", "PACK_AI_DISCLOSURE", "The publishing pack does not record a required AI disclosure.");
    }
  }

  if (options.aiImages) {
    if (!images.length) {
      addFinding(findings, "warning", "AI_IMAGE_COUNT", "--ai-images was set, but no Markdown images were found.");
    }
    const lines = cleanBody.split("\n");
    lines.forEach((line, index) => {
      if (!/!\[[^\]]*\]\([^)]+\)/.test(line)) return;
      const following = lines.slice(index + 1, index + 5).filter((item) => item.trim()).slice(0, 3).join(" ");
      if (!/\b(AI|artificial intelligence|generated|assisted)\b/i.test(following)) {
        addFinding(findings, "error", "AI_IMAGE_CAPTION", `Image near line ${index + 1} lacks a nearby AI-generated or AI-assisted caption.`);
      }
    });
  }

  const errors = findings.filter((finding) => finding.severity === "error").length;
  const warnings = findings.filter((finding) => finding.severity === "warning").length;
  const status = errors > 0 ? "FAIL" : warnings > 0 ? "REVIEW" : "PASS";

  return {
    status,
    file: path.resolve(options.file),
    packFile: options.pack ? path.resolve(options.pack) : null,
    metrics: {
      words: bodyWords,
      h1: h1s.length,
      h2: h2Count,
      paragraphs: bodyParagraphs.length,
      images: images.length,
    },
    counts: { errors, warnings },
    findings,
    limitations: [
      "This audit does not verify facts, originality, authorship, experience provenance, copyright, publication acceptance, paywall eligibility, or distribution outcomes.",
      "Word, title, paragraph, and section checks are editorial heuristics, not Medium platform limits.",
    ],
  };
}

let options;
try {
  options = parseArgs(process.argv.slice(2));
  const markdown = fs.readFileSync(options.file, "utf8");
  const separatePack = options.pack ? fs.readFileSync(options.pack, "utf8") : "";
  const result = audit(markdown, options, separatePack);

  if (options.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`Medium Markdown Audit: ${result.status}`);
    console.log(`File: ${result.file}`);
    if (result.packFile) console.log(`Pack: ${result.packFile}`);
    console.log(`Metrics: ${result.metrics.words} words, ${result.metrics.h1} H1, ${result.metrics.h2} H2, ${result.metrics.paragraphs} prose paragraphs, ${result.metrics.images} images`);
    console.log(`Findings: ${result.counts.errors} error(s), ${result.counts.warnings} warning(s)`);
    for (const finding of result.findings) {
      console.log(`- [${finding.severity.toUpperCase()}] ${finding.code}: ${finding.message}`);
    }
    console.log("Limitations:");
    result.limitations.forEach((item) => console.log(`- ${item}`));
  }

  const shouldFail = result.counts.errors > 0 || (options.strict && result.counts.warnings > 0);
  process.exitCode = shouldFail ? 1 : 0;
} catch (error) {
  console.error(`Error: ${error.message}`);
  usage();
  process.exitCode = 2;
}
