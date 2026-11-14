# KDlab

Sistema de gestão de laboratórios e equipamentos universitários. A proposta é facilitar a consulta de disponibilidade, organizar reservas e empréstimos e acompanhar manutenções, com controle de acesso e histórico das operações.

Projeto acadêmico de Arquitetura de Software, com possibilidade de evolução para uso real. A equipe e a instituição de implantação ainda não foram definidas nesta documentação.

Repositório: [jeziel-monteiro/KDlab](https://github.com/jeziel-monteiro/KDlab).

## Status

**Base executável BL-02 — versão documental 0.3.1, de 14/11/2026.** Login, logout, página da própria conta e provisionamento administrativo estão implementados. A suíte da aplicação passou em 26 testes com PostgreSQL real. Catálogo, reservas, manutenção e empréstimos ainda não foram implementados na aplicação; E1 permanece em desenvolvimento.

O roteiro da disciplina, consultado localmente e não distribuído neste repositório, orienta a organização dos documentos. O trabalho é inspirado na ISO/IEC/IEEE 42010; não foi verificada conformidade integral com a norma.

## Proposta e escopo

- Alunos e professores consultam recursos e solicitam reservas e empréstimos.
- Técnicos e responsáveis analisam solicitações, registram retiradas e devoluções e acompanham manutenções.
- Administradores gerenciam usuários, recursos e regras de acesso.
- O sistema impede reservas aprovadas conflitantes e bloqueia períodos de manutenção, inclusive diante de operações concorrentes.
- Equipamentos podem exigir habilitação ou autorização, e as operações relevantes ficam registradas.

Pagamentos, compras, gestão financeira, sensores IoT e integração com sistemas institucionais ficam fora do escopo inicial.

O primeiro incremento funcional proposto (**E1**) cobre acesso, catálogo, disponibilidade, solicitação e análise de reservas, cancelamento, bloqueios de manutenção, habilitações básicas e histórico. O segundo (**E2**) acrescenta retirada e devolução de equipamentos. Essa divisão é uma proposta de execução; empréstimos continuam no escopo do produto.

## Arquitetura proposta

Monólito modular, com uma aplicação web e um banco relacional. A base usa **Django 5.2.19, templates HTML/CSS, PostgreSQL 17 e psycopg 3.3.9**, com dependências fixadas em `requirements.txt`. O ambiente foi validado com **Python 3.14.4**; Python 3.13, candidato inicial, ainda não foi ensaiado. A recomendação e suas alternativas estão na [proposta de arquitetura](docs/04-arquitetura.md).

A estratégia de agenda comum, transações e exclusão temporal foi verificada no experimento BL-01. Ela será incorporada aos módulos reais de reservas/manutenção. A identidade atual verifica o acesso no servidor e mantém histórico das alterações de contas realizadas no painel.

## Documentação

Comece pelo [índice e pela correspondência com o roteiro](docs/README.md).

| Documento | Conteúdo |
| --- | --- |
| [Visão geral](docs/01-visao-geral.md) | Problema, objetivos, limites e vocabulário |
| [Interessados](docs/02-interessados.md) | Públicos, preocupações e política inicial de acesso |
| [Requisitos](docs/03-requisitos.md) | RF, RNF, restrições, regras e estados |
| [Arquitetura](docs/04-arquitetura.md) | Recomendação, alternativas, stack e consistência |
| [Visões](docs/05-visoes.md) | Diagramas Mermaid de módulos, execução e implantação |
| [Domínio e variabilidade](docs/06-dominio-variabilidade.md) | Núcleo comum, configurações e extensões |
| [Avaliação](docs/07-avaliacao.md) | Cenários verificáveis, riscos e trade-offs |
| [Backlog](docs/08-backlog.md) | Prioridades, critérios de aceitação e primeira entrega |
| [Confirmações e pendências](docs/09-decisoes-e-pendencias.md) | Fatos, hipóteses e decisões a validar |
| [Referências](docs/10-referencias.md) | Material efetivamente consultado |
| [Prova técnica BL-01](docs/11-prova-consistencia-agenda.md) | Procedimento, resultados e limites dos testes da agenda |
| [Base executável BL-02](docs/12-base-identidade.md) | Identidade, histórico, execução e evidências da aplicação |

## Executar a aplicação localmente

Pré-requisitos: Python com `venv` (testado com 3.14.4) e PostgreSQL 17. O Compose abaixo é uma opção para o banco local e requer Docker Compose com suporte a `--wait`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/criar_env.py

set -a
source .env
set +a

docker compose up -d --wait db
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Abra `http://127.0.0.1:8000/`. O painel técnico está em `/admin/`; use o superusuário criado para cadastrar outras contas. Não há senha de administrador predefinida nem cadastro público.

O gerador cria segredos aleatórios em `.env` com permissão 0600, sem exibi-los ou sobrescrever um arquivo existente. O Django recebe variáveis exportadas pelo shell; não lê `.env` automaticamente. `.env.example` documenta as opções. Com PostgreSQL já instalado, configure `POSTGRES_*` e pule o Compose. O Compose mantém os dados em volume local; `docker compose stop db` interrompe o banco preservando seus dados.

## Testar a aplicação

No Linux, com dependências instaladas e imagem local `postgres:17` disponível:

```bash
.venv/bin/python scripts/testar.py
```

O script cria um PostgreSQL exclusivo sem rede, verifica migrações e configuração, coleta estáticos em pasta temporária e executa testes em `test_kdlab`. O container é removido ao final; o banco de desenvolvimento não é usado. A opção `--imagem` permite usar uma imagem PostgreSQL 17 equivalente já disponível. Os [resultados e limites](docs/12-base-identidade.md) incluem a revisão visual ainda pendente por indisponibilidade do navegador.

## Executar a prova técnica

As instruções e dependências estão em [experimentos/agenda](experimentos/agenda/README.md). A execução cria seu próprio PostgreSQL temporário no Docker local, sem rede, e o remove ao final. O ensaio de 14/11/2026 passou em 17 testes, incluindo 100 rodadas de aprovação com 20 conexões concorrentes. Consulte o relatório para o ambiente e os limites desse resultado.

## Organização e próximo passo

O repositório contém a aplicação em `kdlab/` e `apps/`, apresentação em `templates/` e `static/`, utilitários em `scripts/`, documentação em `docs/` e o experimento preservado em `experimentos/agenda/`. Não houve implantação ou publicação.

O material de referência da disciplina e os logs brutos de execução ficam somente no ambiente local, protegidos pelo `.gitignore`. Os relatórios Markdown e o código dos testes são versionados para descrever e reproduzir as verificações.

Na inspeção inicial, o Git pertencia à pasta pai `github/`, abrangendo outros projetos. Em 14/11/2026, por solicitação de publicação no GitHub, o KDlab passou a ter repositório independente, branch `main` e remoto `git@github.com:jeziel-monteiro/KDlab.git`. O índice da pasta pai e os demais projetos foram preservados. Configuração local, ambientes virtuais e caches não integram o versionamento.

O recorte técnico de BL-01 e a base BL-02 estão disponíveis. O próximo trabalho é **BL-03: catálogo de laboratórios/equipamentos e vínculos de responsabilidade**. Permanecem as [hipóteses e validações institucionais](docs/09-decisoes-e-pendencias.md), sem impedir o desenvolvimento local reversível da base.
