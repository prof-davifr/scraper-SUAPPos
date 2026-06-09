# SUAPPos Scraper

Sistema automatizado para login no SUAP do IFBA e extração da lista de alunos da pós-graduação.

## Descrição

O SUAPPos é um scraper (robô de extração de dados) projetado para acessar o Sistema Unificado de Administração Pública (SUAP) do Instituto Federal da Bahia (IFBA), realizar autenticação e baixar a lista completa de alunos dos programas de pós-graduação.

## Funcionalidades

- **Autenticação automática**: Realiza login no SUAP com credenciais fornecidas
- **Extração de dados**: Navega até a seção de pós-graduação e coleta a lista de alunos
- **Exportação**: Salva os dados extraídos em formatos utilizáveis (CSV, JSON, Excel)
- **Tratamento de erros**: Mecanismos de retry e logging de falhas
- **Sessão persistente**: Mantém a sessão ativa durante a extração

## Arquitetura

```
┌─────────────────────────────────────────┐
│           SUAPPos Scraper               │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────┐  │
│  │   Login      │→ │  Navegação       │  │
│  │   Module     │  │  SUAP            │  │
│  └─────────────┘  └──────────────────┘  │
│         ↓                ↓              │
│  ┌──────────────────────────────────┐   │
│  │       Parser de Dados            │   │
│  └──────────────────────────────────┘   │
│                  ↓                      │
│  ┌──────────────────────────────────┐   │
│  │       Export Module              │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Fluxo de Execução

1. **Inicialização**: Carregamento de configurações e credenciais
2. **Login**: Acesso ao SUAP com autenticação
3. **Navegação**: Acesso à página de alunos da pós-graduação
4. **Extração**: Coleta dos dados da tabela de alunos
5. **Processamento**: Limpeza e estruturação dos dados
6. **Exportação**: Salvamento dos dados no formato especificado

## Tecnologias

| Tecnologia   | Finalidade                              |
|-------------|-----------------------------------------|
| Python 3.x  | Linguagem principal                     |
| Selenium    | Automação de navegador                  |
| BeautifulSoup | Parsing de HTML                      |
| Pandas      | Manipulação e exportação de dados       |
| Requests    | Requisições HTTP (opcional)             |

## Pré-requisitos

- Python 3.9+
- Google Chrome ou Firefox instalado
- Credenciais válidas do SUAP

## Configuração

### 1. Clone o repositório

```bash
git clone <repository-url>
cd scraper-SUAPPos
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais

Crie um arquivo `.env` na raiz do projeto:

```env
SUAP_USERNAME=seu_usuario
SUAP_PASSWORD=sua_senha
OUTPUT_DIR=./output
OUTPUT_FORMAT=csv
```

## Uso

### Execução básica

```bash
python main.py
```

### Opções disponíveis

```bash
python main.py --format json        # Exporta em JSON
python main.py --format xlsx        # Exporta em Excel
python main.py --headless           # Executa sem interface gráfica
python main.py --debug              # Modo de depuração
```

## Estrutura de Dados

Os dados extraídos incluem:

| Campo             | Descrição                          |
|-------------------|------------------------------------|
| nome              | Nome completo do aluno             |
| matricula         | Número de matrícula                |
| programa          | Programa de pós-graduação          |
| nivel             | Mestrado ou Doutorado              |
| situacao          | Situação atual (ativo, trancado)   |
| data_ingresso     | Data de ingresso no programa       |
| email             | Email institucional                |
| orientador        | Nome do orientador                 |

## Estrutura do Projeto

```
scraper-SUAPPos/
├── main.py              # Ponto de entrada
├── config.py            # Configurações
├── requirements.txt     # Dependências
├── .env.example         # Exemplo de configuração
├── src/
│   ├── login.py         # Módulo de autenticação
│   ├── scraper.py       # Lógica de extração
│   ├── parser.py        # Processamento de dados
│   └── exporter.py      # Exportação de dados
├── output/              # Diretório de saída
└── tests/               # Testes
```

## Tratamento de Erros

- **Falha de login**: Retry automático (3 tentativas)
- **Timeout de página**: Espera explícita com tempo configurável
- **Dados ausentes**: Logs de advertência e continuação
- **Bloqueio de sessão**: Detecção e notificação

## Segurança

- ⚠️ **Nunca** commitar credenciais no repositório
- Credenciais devem ser armazenadas apenas em `.env`
- O arquivo `.env` está listado no `.gitignore`
- Dados extraídos devem ser tratados conforme LGPD

## Conformidade

Este scraper deve ser utilizado em conformidade com:
- Políticas de uso do SUAP/IFBA
- Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018)
- Normas internas do IFBA para acesso a dados acadêmicos

## Licença

Este projeto é de uso interno e restrito do IFBA.
