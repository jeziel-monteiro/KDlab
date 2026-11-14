# 11. Prova técnica da consistência da agenda

Data: 14/11/2026. Situação: **recorte técnico de BL-01 executado com sucesso**. A validação de stack pela equipe e das hipóteses de negócio permanece pendente. O [experimento](../experimentos/agenda/README.md) é descartável e não constitui a entrega E1.

## Objetivo e recorte

Verificar se a estratégia do [ADR-002](decisoes/ADR-002-consistencia-da-agenda.md) funciona com migrações Django e conexões independentes no PostgreSQL: agenda comum, exclusão temporal, lock do recurso e atomicidade de origem/ocupação/evento. Exercitar também a política candidata de marcador de manutenção em atraso.

H-01/H-02/H-07 foram usadas como hipóteses para o experimento: recurso exclusivo, ausência de bloqueio hierárquico e resolução explícita de manutenção conflitante. O sucesso técnico não confirma essas regras com a universidade. P-01/P-02/P-06 continuam abertas.

## Ambiente e procedimento

| Elemento | Execução registrada |
| --- | --- |
| Python | 3.14.4, ambiente virtual temporário; não foi ensaiado Python 3.13 |
| Django | 5.2.19 |
| Driver | psycopg e psycopg-binary 3.3.9 |
| Dependências complementares | asgiref 3.13.0 e sqlparse 0.6.1 |
| PostgreSQL | 17.11, x86_64, conforme `SELECT version()` |
| Imagem local | `public.ecr.aws/supabase/postgres:17.11.0.006`; usada somente para executar o motor PostgreSQL |
| Isolamento | Container próprio sem rede; socket em diretório temporário privado; banco de teste criado pelo Django |
| Limites do container | 1 CPU e 512 MiB de memória; não representam dimensionamento do produto |
| Concorrência | `TransactionTestCase`, threads com conexões próprias, PIDs de backend distintos e barreira antes das operações |
| Configuração | READ COMMITTED padrão, `select_for_update`, exclusão GiST por recurso/período ativo; timeout de statement de 15 s e de lock de 10 s |

Foi executado primeiro um ensaio curto para verificar a montagem do ambiente. Em seguida, executou-se a suíte completa com 100 rodadas e 20 concorrentes no cenário de aprovação. A instrução reproduzível está no [README do experimento](../experimentos/agenda/README.md).

## Resultados observados

**17 testes passaram em 23,309 s**, segundo o runner Django, na execução final do experimento. A saída original é mantida localmente em `docs/evidencias/bl01-2026-11-14.txt`, fora do versionamento. O código e as instruções para repetir o ensaio estão no experimento.

| Verificação | Resultado observado | Relação com o plano |
| --- | --- | --- |
| Migrações e extensão | `btree_gist` instalada antes da criação da exclusão; catálogo PostgreSQL confirmou a restrição | Pré-condição do ADR-002 |
| Aprovações distintas | 100 rodadas × 20 conexões: exatamente uma aprovação e um evento de sucesso por rodada; demais solicitações permaneceram pendentes | Parte transacional de CQ-01 |
| Duração dessas disputas | Maior duração observada: 0,189 s, incluindo conexão/sincronização da disputa; abaixo da meta candidata de 10 s nesse ensaio | Evidência local, sem generalização de desempenho |
| Aprovação versus manutenção | 100 disputas com duas conexões; uma única ocupação conflitante confirmada por rodada | Parte transacional de CQ-02 |
| Aprovação versus cancelamento | 100 disputas com duas conexões; reserva final cancelada e nenhuma ocupação ativa correspondente | Estados e agenda coerentes |
| Mesma aprovação repetida | 20 chamadas concorrentes; uma gravação e demais respostas de já aprovada, sem duplicação de evento | Idempotência do comando ensaiado |
| Gravação sem lock da aplicação | Duas conexões gravando ocupações diretamente: uma aceita, outra recusada pela exclusão do banco | Barreira de integridade independente da checagem prévia |
| Adjacência e recursos diferentes | Períodos adjacentes e períodos iguais de recursos distintos aceitos | RN-03 e limites da exclusividade |
| Manutenção já registrada / reserva já aprovada | Comando conflitante recusado; decisão existente preservada | Não há cancelamento silencioso |
| Cancelamento | Ocupação desativada sem exclusão; outra reserva pode ocupar o período; repetição não duplica evento | RN-08 e histórico do experimento |
| Falha forçada em aprovação | Três pontos de falha; reserva continuou pendente, sem ocupação ou evento parcial | Parte de CQ-05 |
| Falha forçada em manutenção | Três pontos de falha; origem, ocupação, marcador e evento revertidos juntos | Parte de CQ-05 |
| Manutenção vencida | Nova aprovação suspensa até encerramento; marcador fechado com a origem | Hipótese H-07, sem validar o processo institucional |
| Encerramento | Antecipado reduz período; encerramento antes do início recusado; repetição não gera novo evento | Recorte da máquina de manutenção |
| Limites inválidos e recurso inativo | Intervalos vazios, infinitos e limites incorretos recusados pelo banco; recurso inativo não aprova | Integridade dos dados e checagem da operação |

Além das respostas dos comandos, os testes consultaram os dados finais e verificaram ausência de pares de ocupações ativas sobrepostas e coerência entre aprovação/cancelamento e ocupação. Nenhum timeout ou erro técnico foi registrado nessa execução. O container foi removido ao final; os outros serviços locais não foram alterados.

## Conclusão técnica e próximos passos

A evidência sustenta manter a estratégia candidata do ADR-002 no PostgreSQL. Ela não demonstra ausência de todos os interleavings possíveis, nem substitui regressão após implementar os módulos reais. Os eventos mínimos e o modelo conjunto pertencem à prova, sem identidade/autorização do produto.

BL-01 fica **parcialmente concluído**: prova de banco e receita de execução disponíveis; aceitação das decisões de stack e processo ainda depende dos papéis listados nas pendências. A arquitetura permanece proposta, com evidência técnica anexada.

O encaminhamento da prova foi BL-02, base executável e identidade, mantendo o experimento como referência. Essa base foi implementada posteriormente no mesmo dia, conforme [relatório BL-02](12-base-identidade.md), usando a stack provisoriamente. P-01/P-02/P-06 continuam como validações institucionais. As operações do experimento não foram reaproveitadas como endpoints.

## O que esta execução não avalia

CQ-03/CQ-04 (autorização e habilitação), auditoria completa de RNF-03, interfaces HTTP, desempenho de CQ-06, restauração de CQ-07, usabilidade, empréstimos e integração modular não foram avaliados. A prorrogação/cancelamento de manutenção e a revogação concorrente de habilitação ainda requerem implementação e ensaios próprios. Os cenários de CQ-01/CQ-02/CQ-05 foram cobertos apenas no recorte descrito acima.
