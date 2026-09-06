# Backlink Killer Runner

这是一个普通的 Playwright 脚本，不是浏览器插件。

工作流：

1. 从 Notion 数据库读取一条“提交条件”匹配当前模式、且尚未完成的外链记录。
2. 打开目标页面并复用 `backlink-killer/.playwright/<account>/` 的登录状态。
3. 博客评论：脚本读取文章，AI 只生成评论文本；脚本负责填写表单和提交。
4. 导航站：脚本根据 `site-profiles/<name>/profile.json` 填写字段，不调用 AI。
5. 只有站点返回成功后才把对应 Notion 列更新为 `1`。

安装与运行：

```bash
cd backlink-killer
npm install
npx playwright install chromium
cp .env.example .env
# 填写 NOTION_TOKEN、NOTION_DATABASE_ID；博客评论还需填写 AI_API_URL、AI_API_KEY
npm run check
npm start
```

博客评论模式默认自动提交；导航站模式默认停在最终提交前。站点列名必须通过命令行明确传入；脚本会遍历 Notion 数据库的全部分页，跳过该列已完成的记录。

```bash
BACKLINK_KIND=blog-comment npm start -- --site-column whatisthismovie.com
BACKLINK_KIND=directory npm start -- --site-column whatisthismovie.com --confirm-submit
```

`--site-column` 的值必须和 Notion 中的列名完全一致。未传入时脚本会停止，不会猜测列名。
博客评论模式要求 Notion 的“提交条件”列为“博客评论”；导航站模式要求该列为“导航站”。如需博客评论只填充不提交，使用 `--no-auto-submit`。

首次运行建议保持 `HEADLESS=false`，在浏览器中人工完成登录、验证码或评论展开。脚本不绕过 CAPTCHA，不提交付费/交换链接，也不会把凭据写入审计日志。
