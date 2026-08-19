# Skill de código abierto para backlinks y envíos a directorios de productos

> Creado por [Flaq.ai](https://flaq.ai/) para agentes de programación con IA como Codex y Claude Code.

Un flujo recuperable y respaldado por evidencias para enviar productos, software, startups, aplicaciones y sitios web a directorios de productos y otros canales públicos de descubrimiento. Ayuda a comprobar la elegibilidad, evitar duplicados, respetar autorizaciones, conservar verificaciones manuales, usar datos veraces y registrar resultados auditables.

Un directorio puede generar menciones, tráfico de referencia o backlinks, pero este proyecto **no garantiza** enlaces, atributos follow, aprobación, indexación, tráfico ni mejoras de posicionamiento.

**Idiomas:** [English](README_en.md) · [简体中文](README.md) · [繁體中文](README_tw.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [ไทย](README_th.md) · [Tiếng Việt](README_vi.md) · [Bahasa Indonesia](README_id.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Italiano](README_it.md) · [Português](README_pt.md) · [Русский](README_ru.md) · [العربية](README_ar.md) · [हिन्दी](README_hi.md) · [Türkçe](README_tr.md) · [Nederlands](README_nl.md) · [Polski](README_pl.md)

## Alcance

- Listados de productos, software, herramientas de IA, startups, empresas, apps y sitios web
- Rutas `Request app`, recomendaciones, reclamación de fichas y solicitudes de proveedor
- Creación autorizada de cuentas gratuitas o perfiles públicos
- Envíos por blog, artículo, noticia, comunidad, correo y formulario de contacto
- Comprobaciones de elegibilidad, coste, enlace recíproco, cuenta, duplicados y verificación
- Estados respaldados por evidencias y campañas reanudables

## Principios de seguridad

- Usa solo datos verificados del producto, empresa, fundadores, precios, contacto, propiedad y aspectos legales.
- No eludas CAPTCHA, Turnstile, 2FA, passkeys ni verificaciones de correo.
- No pagues, actives renovaciones, añadas enlaces recíprocos, modifiques web/DNS, subas archivos de verificación ni reclames propiedad sin autorización específica.
- No confundas crear una cuenta, guardar un borrador, hacer clic o navegar con una publicación.
- Si el resultado final es ambiguo, investiga antes de reintentar para evitar duplicados.

## Flujo

1. Carga el perfil, textos, URL, recursos, reglas de autorización y registros aprobados.
2. Normaliza y elimina URL duplicadas.
3. Comprueba disponibilidad, ajuste, coste, reciprocidad, cuentas, términos y duplicados.
4. Reúne CAPTCHA, correo, teléfono y 2FA en una sola cola manual.
5. Tras verificar, completa formularios solo con datos y recursos aprobados.
6. Antes de la acción final, revisa coste, marca, URL, categoría, archivos, acuerdos, riesgo de duplicado y autorización.
7. Registra enseguida la respuesta exacta, hora, URL resultante y evidencias; luego audita.

## Uso

Copia `submit-product-directories-v2-quality/` al directorio Skills del agente o referencia la carpeta directamente.

```text
Usa $submit-product-directories-v2-quality para revisar estas URL y preparar
una campaña de envío. Comprueba primero elegibilidad y verificación. No publiques,
crees cuentas, aceptes acuerdos ni pagues sin autorización. Guarda un registro
auditable y una sola cola de verificaciones manuales.
```

```bash
python3 submit-product-directories-v2-quality/scripts/audit_submission_record.py path/to/record.md
python3 -m unittest discover -s submit-product-directories-v2-quality/tests
```

`submitted` exige un acuse fiable; `published`, una página pública que no sea de vista previa. Nunca deduzcas el éxito solo por un clic o una redirección.

## Flaq.ai y licencia

[Flaq.ai](https://flaq.ai/) ofrece acceso unificado a modelos de imagen, vídeo, música y lenguaje para agentes de IA. Consulta [LICENSE](LICENSE).
