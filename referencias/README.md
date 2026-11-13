# Referencias

Cada fuente enlaza al original público. «Verificado» = se abrió el original y se confirmó lo que se cita.

## Experimento 03 · Esfuerzo de razonamiento en agentes de código

| Clave | Fuente | Qué tomamos | Estado |
|---|---|---|---|
| `chen2024overthinking` | Chen et al., *Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs* (2024). [arXiv:2412.21187](https://arxiv.org/abs/2412.21187) | Primer estudio sistemático sobre *overthinking* en modelos con CoT extendido: en problemas fáciles destinan cómputo excesivo con beneficio mínimo. Medido en matemática, no en agentes de código. | Verificado en arXiv |
| `cherny2026hn` | Boris Cherny (`bcherny`), comentario en Hacker News (2026). [item 47664442](https://news.ycombinator.com/item?id=47664442) | El creador de Claude Code explica el cambio a `medium` (`effort=85`) como valor predeterminado el 3 de marzo por ser el *sweet spot* entre inteligencia, latencia y costo para la mayoría de los usuarios. | Verificado en Hacker News |
| `anthropic2026effort` | Anthropic, *Effort - Claude Platform Docs* (consultado 15/11/2026). [Documentación](https://platform.claude.com/docs/en/build-with-claude/effort) | Define `low`, `medium`, `high`, `xhigh` y `max` («no constraints on token spending») y advierte que esfuerzos altos en tareas estructuradas o simples pueden provocar *overthinking*, mientras que esfuerzos bajos acotan el trabajo y reducen llamadas a herramientas. | Verificado en docs oficiales |
| `anthropic2026fable52` | Anthropic, *Introducing Claude Fable 5.2 and Claude Mythos 5.2* (2026). [Anuncio](https://www.anthropic.com/claude-fable-and-mythos-5-2) | Declara `medium` como predeterminado en Claude Apps y Claude Code y compara FrontierCode 2.0 en `high` y `xhigh`. | Verificado en web oficial |
| `openai2026reasoning` | OpenAI, *Reasoning models \| OpenAI API* (consultado 15/11/2026). [Guía API](https://developers.openai.com/api/docs/guides/reasoning) | Documenta `none`–`max`, indica que los valores por defecto dependen del modelo (`gpt-6.1-sol` usa `medium`) y recomienda reservar `xhigh` para corridas largas donde la evaluación demuestre beneficio neto. | Verificado en docs oficiales |
| `reischl2026effort` | Pascal Reischl, *Claude effort levels: which one you actually need* (27/09/2026). [Blog](https://pascalreischl.com/en/blog/claude-effort-levels/) | Reúne métricas de Artificial Analysis en Opus 5.5 (`low` 0,4×, `medium` 1×, `high` 1,4×, `xhigh` 2,6×, `max` 4,5× de uso por tarea: 11× entre `low` y `max`) y cita pruebas de CodeRabbit donde `max` dio resultados mixtos frente al nivel por defecto. | Verificado en artículo original |

El archivo `referencias.bib` contiene las mismas entradas en formato BibTeX.
