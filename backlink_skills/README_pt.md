# Skill open source para backlinks e submissões a diretórios de produtos

> Criado pela [Flaq.ai](https://flaq.ai/) para agentes de programação com IA como Codex e Claude Code.

Um fluxo recuperável e baseado em evidências para enviar produtos, software, startups, aplicativos e sites a diretórios de produtos e outros canais públicos de descoberta. O Skill verifica elegibilidade, evita duplicações, respeita autorizações, preserva verificações manuais, usa dados verdadeiros e registra resultados auditáveis.

Uma listagem pode gerar citações, tráfego de referência ou backlinks, mas o projeto **não garante** colocação do link, atributo follow, aprovação, indexação, tráfego ou melhoria de ranking.

**Idiomas:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Escopo

- Listagens de produtos, software, ferramentas de IA, startups, empresas, apps e sites
- Rotas `Request app`, recomendações, reivindicação de ficha e candidaturas de fornecedor
- Criação autorizada de contas gratuitas ou perfis públicos
- Envios por blog, artigo, notícia, comunidade, e-mail e formulário de contato
- Verificação de elegibilidade, custo, link recíproco, conta, duplicação e autenticação
- Estados com evidências e campanhas retomáveis

## Princípios de segurança

- Use somente dados verificados de produto, empresa, fundadores, preços, contato, propriedade e aspectos legais.
- Não contorne CAPTCHA, Turnstile, 2FA, passkeys ou verificação de e-mail.
- Não pague, ative renovação, adicione link recíproco, altere site/DNS, envie arquivo de verificação ou reivindique propriedade sem autorização separada.
- Não trate criação de conta, rascunho, clique ou navegação como publicação.
- Se o resultado final for ambíguo, investigue antes de tentar de novo para evitar duplicações.

## Fluxo

1. Carregue perfil, descrições, URLs, recursos, regras de autorização e registros aprovados.
2. Normalize e remova URLs de destino duplicadas.
3. Verifique disponibilidade, adequação, custo, reciprocidade, contas, termos e duplicações.
4. Reúna CAPTCHA, e-mail, telefone e 2FA em uma única fila manual.
5. Após a verificação, preencha apenas fatos e recursos aprovados.
6. Antes da ação final, revise custo, marca, URL, categoria, arquivos, acordos, risco de duplicação e autorização.
7. Registre imediatamente resposta exata, horário, URL resultante e evidências; depois execute a auditoria.

## Uso

Copie `submit-product-directories-v2-quality/` para a pasta Skills do agente ou referencie a pasta diretamente.

```text
Use $submit-product-directories-v2-quality para revisar estes URLs e preparar
uma campanha. Primeiro verifique elegibilidade e autenticação. Não publique,
crie contas, aceite acordos ou pague sem autorização. Salve um registro
auditável e uma única fila de verificações manuais.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` exige comprovante confiável de recebimento; `published`, uma página pública que não seja prévia. Clique ou redirecionamento não prova sucesso.

## Flaq.ai e licença

[Flaq.ai](https://flaq.ai/) oferece acesso unificado a modelos de imagem, vídeo, música e linguagem para agentes de IA. Consulte [LICENSE](LICENSE).
