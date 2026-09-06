import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

export async function openBrowser({ account = 'default', headless = false }) {
  const stateDir = path.resolve('backlink-killer/.playwright', account);
  await fs.mkdir(stateDir, { recursive: true });
  return chromium.launchPersistentContext(stateDir, {
    headless,
    viewport: { width: 1440, height: 1000 },
    userAgent: undefined
  });
}

export async function waitForHumanGate(page, reason) {
  console.log(`\n[需要人工] ${reason}`);
  console.log('请在打开的浏览器中完成登录/验证码/必要操作，然后回到终端按 Enter 继续。');
  process.stdin.setEncoding('utf8');
  await new Promise((resolve) => process.stdin.once('data', resolve));
}
