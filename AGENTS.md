# AGENTS.md — Scraper SUAP Pós-Graduação

## Fonte de Dados

- **Sistema**: SUAP/IFBA (admin de alunos)
- **URL**: `https://suap.ifba.edu.br/admin/edu/aluno/`
- **Autenticação**: SUAP_USERNAME + SUAP_PASSWORD (via `.env`)
- **Tecnologia**: Selenium WebDriver

## Filtros de Modalidade

| Modalidade | ID |
|------------|-----|
| Mestrado | 9 |
| Especialização | 10 |
| Doutorado | 16 |

## Dados Coletados

Exportação XLS do SUAP com dados de alunos de pós-graduação (todos os campi).

## Saída

- `output/` → `alunos_pos_[timestamp].csv` (também suporta JSON e XLSX)

## Projetos Consumidores

- **dashboard-prpgi** → `dados/scraper-SUAPPos/alunos_pos_*.csv` → `data.json`

## Fluxo

```
SUAP (admin/edu/aluno) → [Selenium login + export] → .xls → pandas → .csv
                                                                      ↓
                                                     dashboard-prpgi/build.js → data.json
```

## TODO.md

Este projeto mantém um `TODO.md` na raiz com o planejamento e acompanhamento das tarefas.
O agente é responsável por criar e manter este arquivo atualizado.

O arquivo `TODO.md` da raiz de `/home/davi/projetos/` consolida automaticamente os TODOs de todos os subprojetos.
Execute `python3 /home/davi/projetos/_gen_sumula.py` para regenerar a súmula consolidada após alterações neste TODO.md.

