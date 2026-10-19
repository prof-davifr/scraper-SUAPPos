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

Em 18/10/2026: as duas alterações já foram resolvidas (ver Backlog) e existe
`.github/workflows/ci.yml` com lint e testes, ainda não enviado ao GitHub. A
coleta e a entrega ao dashboard continuam manuais.

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
- [x] **Filtro Lato Sensu removido (03/09/2026)** — `_is_lato_sensu()` mantinha
      só os cursos com a expressão "lato sensu" no nome. A premissa estava
      errada: a modalidade 10 do SUAP já é a Especialização, e todo curso dela é
      pós-graduação lato sensu. O filtro descartava 2193 alunos em 45 cursos
      chamados apenas "Especialização em ...". O painel mostrava 573
      especializandos contra os 2766 do SUAP, e 13 campi sumiam da aba de
      Pós-Graduação. O mesmo filtro existia em
      `scraper-prpgi/src/scrapers/pos.py`, e saiu junto — se só um fosse
      corrigido, o outro desfaria a correção na coleta seguinte.
- [x] **Exportação em CSV, JSON e XLSX** (`src/exporter.py`), com nome de arquivo
      carimbado por timestamp.
- [x] **Rodada real de 21/08/2026**: 2.549 registros no total (1.813 Mestrado,
      163 Doutorado, o restante Especialização já filtrada), CSV gerado sem erro.
- [x] **Rodada de 03/09/2026, já sem o filtro**: 4.770 registros (1.841
      Mestrado, 2.766 Especialização, 163 Doutorado), em 20 campi.

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

- [x] **Decidir o destino das 2 alterações não commitadas — bloqueia tudo o
      mais.** Resolvido: o conserto do login entrou em `322a2c8` (03/09/2026) e o
      `scraper.log` saiu do versionamento em 20/09/2026. Registro original:
- [x] **(original) Decidir o destino das 2 alterações não commitadas — bloqueia tudo o
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
- [x] **Tirar `scraper.log` do versionamento.** Feito em 20/09/2026: o arquivo
      saiu do índice (`git rm --cached`) e `*.log` entrou no `.gitignore`. A
      cópia local continua onde estava. Registro original: O arquivo está rastreado
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
- [x] **Definir a cadência de reexportação — hoje não está definida em lugar
      nenhum.** Resolvido em 19/10/2026: coleta automática mensal pelo
      `dashboard-prpgi/scripts/atualizar-suap.sh` (timer `coleta-suap`, que
      verifica todo dia e coleta quando o CSV mais novo em `dados/` tem 30 dias).
      Ver `docs/proveniencia-dados.md` §2.1.1 do dashboard. A mesma rodada achou
      e corrigiu o clique do link de exportação, interceptado pelo `<header>` no
      modo headless (clique por JavaScript, como no login). Registro original: Nem `README.md`, nem `AGENTS.md`, nem a documentação do
      dashboard dizem de quanto em quanto tempo o coletor deve rodar; as 4
      exportações
      existentes saíram em intervalos irregulares (abr, 11/07, 21/07, 21/08) e a
      mais recente já tem 10 dias. Decidir a periodicidade (o calendário
      acadêmico sugere algo por período letivo, com uma rodada extra depois de
      cada matrícula) e registrar no `AGENTS.md`.
      **Análise (18/10/2026) — decisão do dono, segue pendente.** Fatos: em
      `dashboard-prpgi/dados/scraper-SUAPPos/` há 6 exportações (15/04, 11/07,
      21/07, 21/08, 02/09 e 03/09); a mais recente tem 45 dias. A
      `docs/proveniencia-dados.md` do dashboard registra "Manual, conforme
      exportação do SUAP. Sem periodicidade fixa estabelecida." Não há cron
      nem timer do systemd para este coletor (o único timer de usuário é o
      `grupos-dgp`). Cada rodada exige a máquina com rede que alcance o SUAP,
      Chrome e a senha no cofre, então a cadência é de pessoa, não de
      servidor. Recomendação: uma rodada por mês e uma extra logo depois do
      fim de cada período de matrícula da pós, registradas no `AGENTS.md` e na
      `proveniencia-dados.md` do dashboard; um timer como o do `grupos-dgp`
      só depois que a coleta tiver rodado algumas vezes sem intervenção.
- [x] **Avaliar CI — o repositório não tem `.github/workflows/`.** Feito em
      18/10/2026, só no repositório local: `.github/workflows/ci.yml` roda, em
      push para `main` e em pull request, `ruff check --select E4,E7,E9,F` e
      `pytest -q`, sem rede institucional e sem credencial (`SUAP_USERNAME` e
      `SUAP_PASSWORD` vazios, então o `Config` nem consulta o cofre). Os testes
      novos em `tests/test_config.py` cobrem `_get_modalidade_name`,
      `Config.get_alunos_url_filtered` e `Config.validate`; o
      `_is_lato_sensu` não existe mais (saiu em 03/09). O `main.py` não é
      importado nos testes, porque a importação abre o `scraper.log` na pasta
      corrente. Antes, o lint acusava 4 avisos triviais (`os` sem uso e três
      f-strings sem campo), corrigidos em `59982e8`. Localmente: 13 testes
      passam e o lint fica limpo. **Falta o push** para o workflow começar a
      rodar no GitHub. Registro original:
- [x] **(original) Avaliar CI — o repositório não tem `.github/workflows/`.** Diferente do
      `scraper-DGP`, aqui não há nada vigiando o coletor. Um workflow completo é
      inviável pelo mesmo motivo daquele repo (o runner público do GitHub não
      alcança o SUAP e a credencial precisaria estar em segredo), mas há um
      subconjunto que roda sem rede institucional e sem credencial: lint,
      importação dos módulos e teste das funções puras (`_is_lato_sensu`,
      `_get_modalidade_name`, `Config.get_alunos_url_filtered`,
      `Config.validate`). Decidir se compensa antes de escrever o workflow.
- [x] **Reconciliar 2.549 coletados × 2.548 publicados.** Feito em
      18/10/2026: o registro sumia no build do dashboard, e já não some. O CSV
      de 21/08 (idêntico em `output/` e em `dashboard-prpgi/dados/`) tem 2.549
      registros e 2.550 linhas físicas, porque um aluno do Mestrado tem uma
      quebra de linha dentro de uma célula entre aspas. O `parseCSV` antigo do
      dashboard fazia `split('\n')` antes de olhar as aspas: o registro virava
      dois, ambos sem `ano/periodo_letivo` válido, e os dois eram descartados
      pelo `return null` do mapeamento da pós — 2.548. Reproduzido lendo o
      mesmo CSV com o parser antigo (2.550 registros, 2.548 mantidos) e com o
      `parseCSV` atual (2.549 e 2.549). O conserto é o `d1ffa53` do
      `dashboard-prpgi` (02/09/2026, `splitCsvRecords()`). No CSV de 03/09, para
      onde aponta hoje o `meta.sourceFiles` do `data.json`, são 4.770 registros
      (2 com quebra de linha dentro) e o `data.json` tem 4.770 em
      `posgraduacao`; nenhum registro sem matrícula, sem ano válido ou com
      matrícula repetida. Fica para o `dashboard-prpgi`:
      o build ainda descarta em silêncio as linhas sem matrícula ou sem ano;
      reportar essa contagem ao lado do total da pós é mudança lá, não aqui.
      Registro original:
- [x] **(original) Reconciliar 2.549 coletados × 2.548 publicados.** O CSV de 21/08 tem
      2.549 linhas e a aba Pós-Graduação do dashboard mostra 2.548 — falta 1
      registro. Provavelmente dedup ou descarte de linha incompleta no build do
      dashboard, mas isso não foi verificado. Confirmar de que lado some e, se
      for descarte silencioso, fazer o build reportar a contagem.
- [x] **Não deixar o fallback do `pandas` mascarar dependência faltando.**
      Feito em 04/10/2026: a leitura do XLS foi para `AlunosScraper._read_xls`.
      Sem o `xlrd`, ela levanta `ImportError` dizendo que falta o `xlrd` e que
      se instala com `pip install -r requirements.txt`; o erro sobe até o
      `main.py`, que encerra a coleta em vez de repetir a falha nas três
      modalidades e terminar em "No students found". O `openpyxl` só é tentado
      quando o `xlrd` existe mas não lê o arquivo, e o erro do `xlrd` é
      registrado e encadeado. Teste sem rede em `tests/test_scraper.py`.
      Registro original:
- [x] **(original) Não deixar o fallback do `pandas` mascarar dependência faltando.** Em
      21/08, das 14:07 às 14:08, as 3 exportações morreram com
      `Error in export: File is not a zip file`. A causa real, visível no
      traceback, é o `xlrd` ausente no ambiente: o `except Exception` do
      `_export_and_parse` cai no `openpyxl`, que não lê `.xls` BIFF e devolve
      essa mensagem enganosa. O `xlrd>=2.0.0` está no `requirements.txt`, então
      foi falha de ambiente — mas o erro precisa dizer isso. Tratar
      `ImportError` à parte do erro de parsing.
- [x] **Parar de imprimir o primeiro registro no terminal.** Feito em
      04/10/2026: o resumo final do `main.py` (`format_summary`) mostra a
      contagem por modalidade e os nomes das colunas, nunca os valores de um
      registro. Registro original:
- [x] **(original) Parar de imprimir o primeiro registro no terminal.** O bloco final do
      `main.py` faz `print` de "First record preview" com os valores do primeiro
      aluno, campo a campo, truncados em 80 caracteres — o que inclui os campos
      de identificação. Não vai para o `scraper.log` (é `print`, não `logger`),
      mas vaza para qualquer redirecionamento de saída ou log de agendador.
      Trocar pela contagem por modalidade, ou imprimir só os nomes das colunas.
- [x] **Atualizar o `README.md`, que descreve um projeto diferente do que
      existe.** Feito em 18/10/2026: o README foi reescrito a partir do código.
      Descreve o fluxo real (login, task de exportação, download com os cookies
      do Selenium, leitura pelo `xlrd`), os IDs das três modalidades, a saída
      do filtro Lato Sensu, as variáveis do `.env` e o cofre do sistema, todas
      as flags (inclusive `--modalidade` e o `both` que coleta as três), as 11
      colunas reais do CSV (conferidas no cabeçalho do CSV de 03/09), a entrega
      ao dashboard, a estrutura de pastas que existe e como rodar os testes.
      Saíram o BeautifulSoup, o Firefox, o `config.py` na raiz e o
      `src/parser.py`. Registro original:
- [x] **(original) Atualizar o `README.md`, que descreve um projeto diferente do que
      existe.** Divergências verificadas: cita `config.py` na raiz (está em
      `src/`), `src/parser.py` (não existe) e `tests/` (não existe); a tabela
      "Estrutura de Dados" lista campos (`programa`, `nivel`, `data_ingresso`,
      `orientador`) que o XLS do SUAP não devolve — as colunas reais são outras,
      e faltam `curso`, `campus`, `polo` e `ano/período letivo`; não menciona a
      Especialização nem o filtro Lato Sensu; e a flag `--modalidade` (com o
      valor `both`, que na verdade significa "as três") não aparece.
- [x] **Limpar dependências não usadas do `requirements.txt`.** Feito em
      18/10/2026: `beautifulsoup4`, `lxml`, `flask` e `gunicorn` saíram. Antes,
      `grep` por `bs4`, `BeautifulSoup`, `lxml`, `read_html`, `read_xml`,
      `flask` e `gunicorn` em todos os `.py` do repositório: nenhum uso. O
      `pandas` só lê `.xls` (xlrd) e grava `.xlsx` (openpyxl), sem precisar do
      `lxml`. Registro original:
- [x] **(original) Limpar dependências não usadas do `requirements.txt`.** `flask` e
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
      **Bloqueado em 18/10/2026: falta como verificar.** A troca é pequena,
      mas só se comprova numa coleta de verdade (Chrome + rede do SUAP + login),
      e nesta sessão não se abriu navegador nem se acessou o SUAP. A última
      coleta boa (03/09, 4.770 registros) rodou com os `sleep` atuais, então
      mexer sem uma rodada de conferência troca um risco conhecido por um
      desconhecido. Plano para quando houver uma rodada acompanhada: no
      `scrape_all()`, trocar o `time.sleep(5)` por
      `WebDriverWait(driver, Config.TIMEOUT).until(...)` que aceite a URL de
      login (sessão expirada) ou a presença de `a[href*='export_to_xls']`; no
      `_wait_for_task_completion()`, `WebDriverWait(driver, 120,
      poll_frequency=1)` com uma condição que extraia o id de `/process2/<id>/`
      da URL e devolva o id quando o `body` tiver "Arquivo gerado com
      sucesso". Os mesmos `time.sleep(3)` existem no `login.py`
      (`_navigate_to_login` e `_is_logged_in`). Testar com um driver falso,
      como em `tests/test_scraper.py`, e depois numa coleta real.
