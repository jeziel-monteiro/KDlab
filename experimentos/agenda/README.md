# BL-01 — Prova de consistência da agenda

Experimento isolado para verificar a proposta do [ADR-002](../../docs/decisoes/ADR-002-consistencia-da-agenda.md). Não é o scaffold da aplicação KDlab: todos os modelos ficam juntos somente para o ensaio e não representam a organização final dos módulos.

## O que verifica

- Migração Django que instala `btree_gist` antes da restrição de exclusão.
- Reserva e manutenção ocupando a mesma relação, sem sobreposição de períodos ativos por recurso.
- Transação e bloqueio da linha do recurso antes da origem, inclusive aprovação versus cancelamento.
- Repetição de aprovação sem ocupação/evento de sucesso duplicado.
- Rollback de decisão, ocupação, marcador operacional e evento em falhas forçadas.
- Intervalos adjacentes e recursos diferentes; rejeição de períodos vazios, infinitos ou com limites diferentes de `[início, fim)`.
- Manutenção vencida sem encerramento suspendendo novas aprovações, até encerramento registrado.

Não há usuários, autorização, HTTP, catálogo completo, empréstimos nem migração de dados reais. Os eventos do experimento não têm ator porque a identidade não faz parte do ensaio; não satisfazem isoladamente RF-13/RNF-03. As operações também não implementam todas as políticas de prazo e cancelamento do produto. São chamadas apenas pelos testes sobre dados fictícios.

## Reproduzir no Linux

Pré-requisitos: Python com `venv`, Docker local acessível por socket Unix e uma imagem PostgreSQL 17 compatível já presente. A execução registrada usou Python 3.14.4; Python 3.13 continua como candidato do produto, sem teste específico nesta prova.

A partir da raiz do KDlab:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r experimentos/agenda/requirements.txt
docker pull postgres:17
.venv/bin/python experimentos/agenda/executar.py
```

O download da imagem é feito explicitamente; o executor usa `--pull=never`. O banco nasce em um container exclusivo de nome aleatório, sem rede, portas publicadas ou volume de dados persistente. Somente um diretório temporário de socket é montado. A autenticação `trust` pertence a esse ambiente descartável, sem rede; não é configuração de implantação. O diretório pai do socket é privado ao usuário local.

O runner Django cria e remove `kdlab_bl01_test` dentro desse PostgreSQL efêmero. Ao terminar, inclusive em falha dos testes, o executor remove somente o container que criou. Não usa `DATABASE_URL`, não conecta a banco externo e não remove outros containers/volumes. Contextos Docker remotos são recusados. Não é necessário instalar PostgreSQL na estação.

Por padrão são 100 rodadas de cada disputa principal e 20 concorrentes no ensaio de aprovação. Para um ensaio curto de desenvolvimento:

```bash
.venv/bin/python experimentos/agenda/executar.py --rodadas 3 --concorrentes 4
```

É possível usar uma imagem local equivalente com `--imagem`. A execução de 14/11/2026 aproveitou a imagem já disponível `public.ecr.aws/supabase/postgres:17.11.0.006`, iniciando diretamente `initdb` e `postgres`; não ativou serviços Supabase nem criou dependência do produto nesse serviço.

Comando registrado, usando o Python do ambiente virtual temporário:

```bash
python experimentos/agenda/executar.py \
  --imagem public.ecr.aws/supabase/postgres:17.11.0.006 \
  --rodadas 100 --concorrentes 20
```

O processo precisa de acesso ao Docker local. Um erro de permissão no socket deve ser resolvido pela configuração do ambiente; não alterar permissões do socket global para executar a prova.

## Resultados e limites

Consulte o [relatório](../../docs/11-prova-consistencia-agenda.md). O log bruto da execução é mantido localmente em `docs/evidencias/bl01-2026-11-14.txt`, fora do Git. Não interpretar os tempos observados como SLA, ensaio HTTP ou validação de escala. A arquitetura completa ainda depende de implementação modular, autorização e validação das regras do domínio.
