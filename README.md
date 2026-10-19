# SUAPPos Scraper

Coletor que loga no SUAP do IFBA, exporta a lista de alunos de pós-graduação
(Mestrado, Especialização e Doutorado, todos os campi) e grava o resultado em
CSV, JSON ou XLSX. O CSV alimenta a aba Pós-Graduação do `dashboard-prpgi`.

## Como funciona

1. **Login** (`src/login.py`): abre o Chrome pelo Selenium, preenche
   `id_username` e `id_password` e clica em "Acessar". No modo headless um
   elemento da página cobre o botão e o clique nativo é interceptado; nesse
   caso o clique vai por JavaScript. Até `MAX_RETRIES` tentativas.
2. **Exportação** (`src/scraper.py`): para cada modalidade, abre o changelist
   `admin/edu/aluno/` filtrado por `curso_campus__modalidade__id__exact`, clica
   no link `export_to_xls` e acompanha a task em `/djtools/process2/<id>/` até
   "Arquivo gerado com sucesso" (limite de 120 s).
3. **Download**: baixa o XLS pelo endpoint `/djtools/process_progress2/1/<id>/`
   numa sessão `requests` que reaproveita os cookies do Selenium. O arquivo cru
   fica em `output/raw_export_<epoch>.xls`.
4. **Leitura**: o XLS do SUAP é BIFF (`.xls` antigo) e só o `xlrd` o lê. Sem o
   `xlrd` a coleta para com a instrução de instalação, em vez de repetir a falha
   nas três modalidades.
5. **Exportação final** (`src/exporter.py`): junta as modalidades, acrescenta a
   coluna `modalidade` e grava `output/alunos_pos_AAAAMMDD_HHMMSS.<formato>`.

| Modalidade     | ID no SUAP |
|----------------|------------|
| Mestrado       | 9          |
| Especialização | 10         |
| Doutorado      | 16         |

Não há filtro por nome de curso. A modalidade 10 já é a Especialização, e todo
curso dela é pós-graduação lato sensu. O filtro "lato sensu", que existia até
setembro de 2026, descartava os cursos chamados apenas "Especialização em ...".

## Pré-requisitos

- Python 3.10+
- Google Chrome (o `webdriver-manager` baixa o chromedriver correspondente; sem
  ele, o Selenium procura o driver por conta própria)
- Usuário do SUAP com acesso ao admin de alunos
- Rede que alcance `suap.ifba.edu.br`

## Configuração

```bash
pip install -r requirements.txt
cp .env.example .env
```

No `.env`, preencha ao menos `SUAP_USERNAME`. A senha pode ficar no cofre do
sistema (serviço `suap`), fora de qualquer arquivo:

```bash
keyring set suap seu_usuario
```

`SUAP_PASSWORD` no `.env` também funciona, e tem precedência sobre o cofre.

| Variável        | Padrão                      | Uso                                |
|-----------------|-----------------------------|------------------------------------|
| `SUAP_USERNAME` | (obrigatória)               | usuário do SUAP                    |
| `SUAP_PASSWORD` | cofre do sistema            | senha, se não estiver no cofre     |
| `SUAP_BASE_URL` | `https://suap.ifba.edu.br`  | endereço do SUAP                   |
| `OUTPUT_DIR`    | `./output`                  | pasta de saída                     |
| `OUTPUT_FORMAT` | `csv`                       | `csv`, `json` ou `xlsx`            |
| `HEADLESS`      | `true`                      | navegador sem janela               |
| `TIMEOUT`       | `30`                        | espera dos campos de login (s)     |
| `MAX_RETRIES`   | `3`                         | tentativas de login                |

## Uso

```bash
python main.py                              # as três modalidades, em CSV
python main.py --modalidade mestrado        # só uma: mestrado, doutorado ou especializacao
python main.py --format json                # ou xlsx; sobrepõe OUTPUT_FORMAT
python main.py --output-dir /outra/pasta    # sobrepõe OUTPUT_DIR
python main.py --headless                   # força headless (o padrão já vem do .env)
python main.py --debug                      # log em nível DEBUG
```

`--modalidade both` é o padrão e, apesar do nome, coleta as três modalidades.

Ao final, o terminal mostra o total, o arquivo gerado, a contagem por modalidade
e os nomes das colunas, nunca os valores de um registro. O log vai para o
terminal e para `scraper.log`, na pasta de onde o comando foi chamado (fora do
versionamento).

## Dados de saída

Uma linha por aluno, com as colunas da exportação do SUAP (nomes em minúsculas,
espaços trocados por `_`) mais a modalidade:

| Coluna               | Conteúdo                                  |
|----------------------|-------------------------------------------|
| `#`                  | número da linha na planilha do SUAP       |
| `nome`               | nome do aluno                             |
| `matrícula`          | matrícula                                 |
| `curso`              | curso, como cadastrado pelo campus        |
| `campus`             | campus                                    |
| `polo`               | polo, quando houver                       |
| `situação`           | situação da matrícula                     |
| `e-mail_acadêmico`   | e-mail institucional                      |
| `e-mail_pessoal`     | e-mail pessoal                            |
| `ano/periodo_letivo` | ano e período de ingresso, `AAAA.P`       |
| `modalidade`         | Mestrado, Especialização ou Doutorado     |

Uma célula pode trazer quebra de linha dentro (vem assim do SUAP); quem lê o
CSV precisa respeitar as aspas.

## Entrega ao dashboard

O CSV é copiado para `dashboard-prpgi/dados/scraper-SUAPPos/`. Cada exportação
traz todos os alunos, então o build do dashboard usa só o arquivo de timestamp
mais novo; os anteriores podem ficar na pasta sem duplicar registro. O
`data.json` público não leva nome, matrícula nem e-mail: o build pseudonimiza a
matrícula.

## Estrutura do projeto

```
scraper-SUAPPos/
├── main.py              # ponto de entrada (argumentos, navegador, resumo)
├── requirements.txt
├── .env.example
├── src/
│   ├── config.py        # .env, cofre do sistema, URLs, IDs de modalidade
│   ├── login.py         # login no SUAP
│   ├── scraper.py       # exportação XLS pela task do SUAP e leitura
│   └── exporter.py      # CSV, JSON e XLSX
├── tests/               # testes sem rede e sem credencial
├── .github/workflows/   # lint e testes
└── output/              # XLS crus e arquivos gerados (fora do versionamento)
```

## Testes

```bash
pip install pytest ruff
ruff check --select E4,E7,E9,F .
pytest -q
```

Os testes não abrem navegador, não acessam a rede e não leem credencial. A
coleta de verdade só roda numa máquina com acesso ao SUAP.

## Segurança e LGPD

- Credenciais ficam no cofre do sistema ou no `.env`, que está no
  `.gitignore`. Nunca no repositório.
- `output/` também está no `.gitignore`: os XLS e CSV trazem nome, matrícula e
  e-mails dos alunos.
- O uso deve seguir as políticas do SUAP/IFBA, a LGPD (Lei 13.709/2018) e as
  normas internas do IFBA para acesso a dados acadêmicos.

## Licença

Uso interno e restrito do IFBA.
