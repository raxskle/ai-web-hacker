import 'dotenv/config';
import { queryOneTarget, markSiteSubmitted } from './notion.js';
import { openBrowser } from './browser.js';
import { runTarget } from './workflow.js';

const args = new Set(process.argv.slice(2));
const kind = process.env.BACKLINK_KIND || (args.has('--directory') ? 'directory' : 'blog-comment');
const profileName = process.env.PROFILE || 'example-site';
const account = process.env.BACKLINK_ACCOUNT || 'default';
const autoSubmit = kind === 'blog-comment' && !args.has('--no-auto-submit');
const siteColumnIndex = process.argv.indexOf('--site-column');
const siteColumn = siteColumnIndex >= 0 ? process.argv[siteColumnIndex + 1] : '';
if (!siteColumn || siteColumn.startsWith('--')) {
  throw new Error('请告诉脚本 Notion 站点列名，例如：--site-column whatisthismovie.com');
}

const record = await queryOneTarget({
  token: process.env.NOTION_TOKEN,
  databaseId: process.env.NOTION_DATABASE_ID,
  targetUrl: process.env.TARGET_URL,
  siteColumn,
  kind
});
const context = await openBrowser({ account, headless: process.env.HEADLESS === 'true' });
try {
  const page = context.pages()[0] || await context.newPage();
  const result = await runTarget({
    page,
    record,
    profileName,
    kind,
    confirmSubmit: autoSubmit || args.has('--confirm-submit'),
    ai: { apiUrl: process.env.AI_API_URL, apiKey: process.env.AI_API_KEY, model: process.env.AI_MODEL || 'default' }
  });
  console.log(JSON.stringify({ target: record.properties, result }, null, 2));
  if (result.status === 'submitted') {
    await markSiteSubmitted({ token: process.env.NOTION_TOKEN, pageId: record.id, propertyName: siteColumn });
    console.log(`Notion 已将 ${siteColumn} 更新为 1`);
  }
} finally {
  await context.close();
}
