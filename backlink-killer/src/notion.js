const NOTION_VERSION = '2022-06-28';

function plainValue(property) {
  if (!property) return '';
  if (property.type === 'title' || property.type === 'rich_text') {
    return (property[property.type] || []).map((x) => x.plain_text || x.text?.content || '').join('');
  }
  if (property.type === 'url') return property.url || '';
  if (property.type === 'select') return property.select?.name || '';
  if (property.type === 'status') return property.status?.name || '';
  if (property.type === 'checkbox') return Boolean(property.checkbox);
  if (property.type === 'number') return property.number;
  if (property.type === 'email') return property.email || '';
  return '';
}

function pageToRecord(page) {
  const properties = Object.fromEntries(
    Object.entries(page.properties || {}).map(([name, property]) => [name, plainValue(property)])
  );
  return { id: page.id, url: page.url, properties };
}

export async function queryOneTarget({ token, databaseId, targetUrl, siteColumn, kind }) {
  if (!token || !databaseId) throw new Error('NOTION_TOKEN 和 NOTION_DATABASE_ID 必须配置');
  if (!siteColumn) throw new Error('必须通过 --site-column 指定 Notion 站点列名');

  const records = [];
  let startCursor;
  do {
    const response = await fetch(`https://api.notion.com/v1/databases/${databaseId}/query`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ page_size: 100, ...(startCursor ? { start_cursor: startCursor } : {}) })
    });
    if (!response.ok) throw new Error(`Notion 查询失败: ${response.status} ${await response.text()}`);
    const data = await response.json();
    records.push(...(data.results || []).map(pageToRecord));
    startCursor = data.has_more ? data.next_cursor : undefined;
  } while (startCursor);

  const normalizedTarget = targetUrl ? normalizeUrl(targetUrl) : '';
  const expectedConditions = kind === 'blog-comment'
    ? ['博客评论', 'blog-comment', 'blog comment', 'comment']
    : ['导航站', 'directory', 'directory listing'];
  const eligible = records.find((record) => {
    const target = normalizeUrl(findProperty(record.properties, ['原URL', 'target_url', 'url', 'URL']));
    if (normalizedTarget && target !== normalizedTarget) return false;
    const condition = String(findProperty(record.properties, ['提交条件', 'submission_condition', 'submission type', 'type', '类型']) || '')
      .trim().toLowerCase();
    if (!condition || !expectedConditions.includes(condition)) return false;
    const status = String(findProperty(record.properties, ['status', '状态']) || '').toLowerCase();
    const siteStatus = String(siteColumn ? record.properties[siteColumn] ?? '' : '').toLowerCase();
    return !['1', 'true', 'submitted', 'success', '完成', '已提交'].includes(status)
      && !['1', 'true', 'submitted', 'success', '完成', '已提交'].includes(siteStatus);
  });
  if (!eligible) throw new Error('Notion 中没有找到可处理的目标记录');
  return eligible;
}

export async function markSiteSubmitted({ token, pageId, propertyName }) {
  const response = await fetch(`https://api.notion.com/v1/pages/${pageId}`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Notion-Version': NOTION_VERSION,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ properties: { [propertyName]: { number: 1 } } })
  });
  if (!response.ok) throw new Error(`Notion 状态更新失败: ${response.status} ${await response.text()}`);
}

export function findProperty(properties, names) {
  const entry = Object.entries(properties).find(([name]) => names.includes(name));
  return entry ? entry[1] : '';
}

function normalizeUrl(value) {
  return String(value || '').replace(/#.*$/, '').replace(/\/$/, '');
}
