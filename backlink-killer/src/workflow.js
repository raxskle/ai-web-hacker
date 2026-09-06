import fs from 'node:fs/promises';
import path from 'node:path';
import { generateBlogComment } from './ai.js';
import { waitForHumanGate } from './browser.js';

const SELECTORS = {
  comment: ['textarea[name*=comment i]', 'textarea[id*=comment i]', 'textarea[placeholder*=comment i]', 'textarea'],
  name: ['input[name*=name i]', 'input[id*=name i]', 'input[autocomplete=name]'],
  email: ['input[type=email]', 'input[name*=mail i]', 'input[id*=mail i]'],
  website: ['input[name*=url i]', 'input[name*=website i]', 'input[id*=url i]', 'input[id*=website i]'],
  submit: ['button[type=submit]', 'input[type=submit]', 'button:has-text("Comment")', 'button:has-text("Submit")', 'button:has-text("Post")']
};

async function firstVisible(page, selectors) {
  for (const selector of selectors) {
    const locator = page.locator(selector).filter({ visible: true }).first();
    if (await locator.count()) return locator;
  }
  return null;
}

async function fillFirst(page, selectors, value) {
  if (!value) return false;
  const locator = await firstVisible(page, selectors);
  if (!locator) return false;
  await locator.fill(value);
  return true;
}

async function clickSubmit(page) {
  const locator = await firstVisible(page, SELECTORS.submit);
  if (!locator) return false;
  await locator.click();
  return true;
}

async function loadProfile(profileName) {
  const file = path.resolve('backlink-killer/site-profiles', profileName, 'profile.json');
  return JSON.parse(await fs.readFile(file, 'utf8'));
}

export async function runTarget({ page, record, profileName, kind, confirmSubmit, ai, notion }) {
  const profile = await loadProfile(profileName);
  const targetUrl = record.properties['原URL'] || record.properties.target_url || record.properties.url;
  if (!targetUrl) throw new Error('Notion 记录缺少目标 URL');
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });

  if (kind === 'blog-comment') {
    const commentBox = await firstVisible(page, SELECTORS.comment);
    if (!commentBox) return { status: 'skipped', reason: '未找到评论框' };
    const article = { title: await page.title(), text: await page.locator('body').innerText() };
    const comment = await generateBlogComment({ ...ai, article, profile });
    await fillFirst(page, SELECTORS.name, profile.contact?.name);
    await fillFirst(page, SELECTORS.email, profile.contact?.email);
    await fillFirst(page, SELECTORS.website, profile.links?.homepage);
    await commentBox.fill(comment);
    console.log(`博客评论已生成并填入：${comment}`);
    if (!confirmSubmit) return { status: 'needs-confirmation', comment };
    if (!(await clickSubmit(page))) return { status: 'failed', reason: '未找到提交按钮' };
    await page.waitForLoadState('domcontentloaded').catch(() => {});
    return { status: 'submitted', confirmation: page.url() };
  }

  await fillFirst(page, ['input[name*=name i]', 'input[id*=name i]'], profile.contact?.name);
  await fillFirst(page, ['input[type=email]', 'input[name*=mail i]'], profile.contact?.email);
  await fillFirst(page, ['input[name*=url i]', 'input[name*=website i]', 'input[id*=url i]'], profile.links?.homepage);
  await fillFirst(page, ['input[name*=title i]', 'input[id*=title i]'], profile.display_name);
  await fillFirst(page, ['textarea[name*=description i]', 'textarea[id*=description i]'], profile.description);
  console.log('导航站字段已由脚本填写。');
  if (!confirmSubmit) return { status: 'needs-confirmation' };
  await waitForHumanGate(page, '导航站最终提交前确认字段、免费条件和站点政策');
  if (!(await clickSubmit(page))) return { status: 'failed', reason: '未找到提交按钮' };
  await page.waitForLoadState('domcontentloaded').catch(() => {});
  return { status: 'submitted', confirmation: page.url() };
}
