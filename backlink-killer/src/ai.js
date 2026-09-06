export async function generateBlogComment({ apiUrl, apiKey, model, article, profile }) {
  if (!apiUrl || !apiKey) throw new Error('博客评论需要配置 AI_API_URL 和 AI_API_KEY');
  const prompt = [
    '请为下面的文章写一条真实、有帮助、25-45词的博客评论。',
    '不要夸张营销、不要关键词堆砌、不要提及你是AI。只有在语境自然时提及产品。',
    `文章标题：${article.title}`,
    `文章摘要：${article.text.slice(0, 5000)}`,
    `产品信息：${profile.description || profile.short_description || ''}`,
    `产品链接：${profile.links?.homepage || ''}`
  ].join('\n');
  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({ model, messages: [{ role: 'user', content: prompt }], temperature: 0.4 })
  });
  if (!response.ok) throw new Error(`AI 请求失败: ${response.status} ${await response.text()}`);
  const data = await response.json();
  const text = data.choices?.[0]?.message?.content || data.output_text || data.text || '';
  if (!text.trim()) throw new Error('AI 没有返回评论文本');
  return text.trim();
}
