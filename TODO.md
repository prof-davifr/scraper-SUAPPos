# TODO — Coletor SUAP Pós-Graduação

Coletor Selenium que loga no SUAP/IFBA, dispara a exportação XLS do changelist
`admin/edu/aluno/` para as três modalidades de pós-graduação (Mestrado id=9,
Especialização id=10, Doutorado id=16) e converte o resultado em
`output/alunos_pos_AAAAMMDD_HHMMSS.csv`, consumido pela aba Pós-Graduação do
`dashboard-prpgi`.

Onde termina a automação hoje (31/08/2026):

```
SUAP (admin/edu/aluno)  →  CSV em output/  →  dashboard-prpgi (data.json)
   MANUAL/local             MANUAL             MANUAL
   (credencial + rede)      (cópia de arquivo) (npm run build local)
```

Nenhuma etapa é automática: não há `.github/workflows/`, não há agendamento e a
entrega ao dashboard é cópia de arquivo pelo sistema de arquivos. **O repositório
está parado há 41 dias** — último commit `914fa44`, de 21/07/2026 — e tem **duas
alterações não commitadas** (`src/login.py` e `scraper.log`).

---

## 🟢 Concluído

### Coleta funcional das três modalidades
- [x] **Login via Selenium** (`src/login.py`) com 3 tentativas, campos por ID e
      verificação de sessão; credenciais só via `.env`.
- [x] **Exportação pelo sistema de tasks do SUAP** (`src/scraper.py`) — clica no
      link `export_to_xls`, faz polling da página `/djtools/process2/<id>/` até
      "Arquivo gerado com sucesso" (limite de 120 s) e baixa o XLS pelo endpoint
      `process_progress2` reaproveitando os cookies do Selenium em uma sessão
      `requests`.
- [x] **Filtro Lato Sensu na Especialização** — a modalidade 10 traz cursos que
      não são pós-graduação; `_is_lato_sensu()` mantém só os que têm "lato sensu"
      no nome do curso.
- [x] **Exportação em CSV, JSON e XLSX** (`src/exporter.py`), com nome de arquivo
      carimbado por timestamp.
- [x] **Rodada real de 21/08/2026**: 2.549 registros no total (1.813 Mestrado,
      163 Doutorado, o restante Especialização já filtrada), CSV gerado sem erro.

### Entrega ao dashboard
- [x] **O CSV de 21/08/2026 chegou ao dashboard e está em produção.** Confirmado
      em `dashboard-prpgi/data.json`: `meta.sourceFiles["scraper-SUAPPos"]`
      aponta para `alunos_pos_20260821_141147.csv` e a aba Pós-Graduação tem
      2.548 registros. (A informação de que a última exportação seria de julho
      está desatualizada — há 4 CSVs entregues: abr, 11/07, 21/07 e 21/08.)
- [x] **Exportações cumulativas, consumo do mais recente** — o build do dashboard
      usa apenas o CSV de timestamp mais novo, então os anteriores podem ficar
      onde estão sem duplicar registro.

### Higiene de segredo e de dado pessoal
- [x] **`.env` nunca foi commitado** — verificado com `git log -- .env`: nenhum
      commit. Está no `.gitignore` junto com `output/`, `__pycache__/` e os
      drivers.
- [x] **`output/` fora do versionamento** — é onde ficam os XLS crus e os CSV,
      que carregam os campos de identificação do aluno (nome, matrícula, e-mails
      acadêmico e pessoal). Nada disso está no repositório.
- [x] **`AGENTS.md`** documentando fonte, IDs de modalidade, saída e o projeto
      consumidor (`914fa44`, 21/07/2026).

---

## 📋 Backlog

- [ ] **Decidir o destino das 2 alterações não commitadas — bloqueia tudo o
      mais.** `git status` mostra `src/login.py` e `scraper.log` modificados há
      10 dias. **O diff de `src/login.py` conserta o login quebrado**: na janela
      1920x1080 do modo headless um `<ul>` da página cobre o botão "Acessar" e o
      clique nativo do Selenium é interceptado (`ElementClickInterceptedException`),
      derrubando as 3 tentativas. A correção passa a dar `scrollIntoView` no
      botão, tenta o clique nativo e, se ele for interceptado, clica via
      JavaScript; o `Enter` no campo de senha deixa de ser fallback geral e
      passa a valer só quando o botão não existe. **A correção está comprovada
      pelo log**: às 14:05 de 21/08 as 3 tentativas falharam com clique
      interceptado, e às 14:06 e 14:10 o aviso "Submit button intercepted;
      clicking via JavaScript" é seguido de "Login successful" e dos 2.549
      registros. É a mesma correção que o `scraper-DGP` já commitou. Falta só
      commitar aqui — sem ela o coletor não loga em headless.
- [ ] **Tirar `scraper.log` do versionamento.** O arquivo está rastreado
      (`git ls-files`), foi commitado com 38 linhas em `89c748d` e hoje tem 396
      na árvore de trabalho — o `FileHandler` do `main.py` grava em modo append
      na raiz do repositório, então **toda execução suja a árvore** e gera um
      diff que não é mudança de código. Conteúdo auditado: não há credencial,
      nome, matrícula nem e-mail de aluno; há, porém, a lista de colunas do XLS
      (que expõe o esquema dos campos de identificação), 58 ocorrências de
      caminhos absolutos locais revelando o usuário do sistema operacional,
      versões de Chrome/chromedriver e 8 linhas de ERROR com stack trace. Ação:
      `git rm --cached scraper.log`, acrescentar `scraper.log` (ou `*.log`) ao
      `.gitignore` e, de preferência, mandar o log para `output/`, que já é
      ignorado.
- [ ] **Definir a cadência de reexportação — hoje não está definida em lugar
      nenhum.** Nem `README.md`, nem `AGENTS.md`, nem a documentação do
      dashboard dizem de quanto em quanto tempo o coletor deve rodar; as 4
      exportações
      existentes saíram em intervalos irregulares (abr, 11/07, 21/07, 21/08) e a
      mais recente já tem 10 dias. Decidir a periodicidade (o calendário
      acadêmico sugere algo por período letivo, com uma rodada extra depois de
      cada matrícula) e registrar no `AGENTS.md`.
- [ ] **Avaliar CI — o repositório não tem `.github/workflows/`.** Diferente do
      `scraper-DGP`, aqui não há nada vigiando o coletor. Um workflow completo é
      inviável pelo mesmo motivo daquele repo (o runner público do GitHub não
      alcança o SUAP e a credencial precisaria estar em segredo), mas há um
      subconjunto que roda sem rede institucional e sem credencial: lint,
      importação dos módulos e teste das funções puras (`_is_lato_sensu`,
      `_get_modalidade_name`, `Config.get_alunos_url_filtered`,
      `Config.validate`). Decidir se compensa antes de escrever o workflow.
- [ ] **Reconciliar 2.549 coletados × 2.548 publicados.** O CSV de 21/08 tem
      2.549 linhas e a aba Pós-Graduação do dashboard mostra 2.548 — falta 1
      registro. Provavelmente dedup ou descarte de linha incompleta no build do
      dashboard, mas isso não foi verificado. Confirmar de que lado some e, se
      for descarte silencioso, fazer o build reportar a contagem.
- [ ] **Não deixar o fallback do `pandas` mascarar dependência faltando.** Em
      21/08, das 14:07 às 14:08, as 3 exportações morreram com
      `Error in export: File is not a zip file`. A causa real, visível no
      traceback, é o `xlrd` ausente no ambiente: o `except Exception` do
      `_export_and_parse` cai no `openpyxl`, que não lê `.xls` BIFF e devolve
      essa mensagem enganosa. O `xlrd>=2.0.0` está no `requirements.txt`, então
      foi falha de ambiente — mas o erro precisa dizer isso. Tratar
      `ImportError` à parte do erro de parsing.
- [ ] **Parar de imprimir o primeiro registro no terminal.** O bloco final do
      `main.py` faz `print` de "First record preview" com os valores do primeiro
      aluno, campo a campo, truncados em 80 caracteres — o que inclui os campos
      de identificação. Não vai para o `scraper.log` (é `print`, não `logger`),
      mas vaza para qualquer redirecionamento de saída ou log de agendador.
      Trocar pela contagem por modalidade, ou imprimir só os nomes das colunas.
- [ ] **Atualizar o `README.md`, que descreve um projeto diferente do que
      existe.** Divergências verificadas: cita `config.py` na raiz (está em
      `src/`), `src/parser.py` (não existe) e `tests/` (não existe); a tabela
      "Estrutura de Dados" lista campos (`programa`, `nivel`, `data_ingresso`,
      `orientador`) que o XLS do SUAP não devolve — as colunas reais são outras,
      e faltam `curso`, `campus`, `polo` e `ano/período letivo`; não menciona a
      Especialização nem o filtro Lato Sensu; e a flag `--modalidade` (com o
      valor `both`, que na verdade significa "as três") não aparece.
- [ ] **Limpar dependências não usadas do `requirements.txt`.** `flask` e
      `gunicorn` estão declarados e não há servidor web algum no repositório;
      `beautifulsoup4` e `lxml` também não são importados por nenhum módulo
      (`grep` em `main.py` e `src/*.py` não retorna nada). Só instalam peso e
      superfície de atualização.
- [ ] **Substituir os `time.sleep` fixos por espera explícita.** O
      `scrape_all()` dorme 5 s após cada `driver.get()` e o
      `_wait_for_task_completion()` faz polling de 3 em 3 s até 120 s. Em rede
      institucional lenta isso vira falha silenciosa (a página ainda não
      carregou e o elemento de exportação não é encontrado); em rede rápida,
      desperdício. Migrar para `WebDriverWait`, como o `login.py` já faz.
