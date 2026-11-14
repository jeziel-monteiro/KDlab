# ADR-002 — Agenda comum e proteção transacional

- Status: **proposto para o produto; recorte técnico de BL-01 verificado em 14/11/2026**.
- Data: 13/11/2026.
- Relacionados: RN-01, RN-02, RN-08, RNF-01 e CQ-01/CQ-02/CQ-05.

## Contexto

Consultar um período livre e depois inserir uma reserva permite que duas transações tomem a mesma decisão. Validar reservas e manutenção em tabelas distintas também pode deixar uma operação ignorar a outra. Precisamos preservar a exclusividade mesmo com múltiplas conexões e falhas entre escritas.

## Decisão proposta

Centralizar períodos bloqueantes em `Ocupacao`, no módulo Agenda. Usar intervalo temporal `[início, fim)` e restrição de exclusão PostgreSQL por recurso/intervalo ativo. Declará-la por migração Django, incluindo `btree_gist`. Confirmar recurso, origem, ocupação e evento de sucesso em uma transação curta. Coordenar comandos pelo bloqueio da linha do recurso, antes do registro da origem, com revalidação após adquirir o bloqueio.

Reserva pendente não ocupa; aprovação ocupa; cancelamento desativa a ocupação. Manutenção ocupa o mesmo conjunto de intervalos. Origem e ocupação devem corresponder sem duplicação. A tabela comum não substitui máquinas de estados e regras de acesso. A condição física atual também precisa ser verificada, conforme RN-10 a RN-12.

## Alternativas

- Somente validação antes de gravar: simples, mas insuficiente sob concorrência; descartada.
- Somente bloqueio do recurso e consultas separadas: pode funcionar se todos os escritores obedecerem ao protocolo; fica sem a barreira de exclusão comum no banco.
- Isolamento SERIALIZABLE e repetição de transações: candidato válido, mas exige política de retries e ensaios específicos; não é a primeira opção.

## Consequências e limites

O sistema assume PostgreSQL e permissões para instalar a extensão. Comandos do mesmo recurso são serializados, podendo aumentar espera em recursos disputados. Adjacência, reversão, concorrência e repetição precisam ser testadas no banco real. Testes com SQLite ou mutex em memória não demonstram essa garantia. A restrição de exclusão sozinha não assegura que o estado da reserva corresponda à agenda; essa parte depende da transação e dos contratos.

## Evidência exigida para aceitar a decisão

Prova descartável de aprovação versus aprovação e aprovação versus manutenção, com conexões independentes, barreira de início e inspeção final do banco. Também verificar cancelamento simultâneo, intervalos adjacentes, repetição de comando e falha forçada antes do commit.

## Evidência obtida em 14/11/2026

O [experimento BL-01](../../experimentos/agenda/README.md) aplicou migrações Django 5.2.19 no PostgreSQL 17.11 e passou em 17 testes. Foram 100 rodadas de aprovação com 20 conexões, 100 disputas aprovação/manutenção e 100 aprovação/cancelamento, além de repetição, adjacência, gravação direta sem lock e rollback. [Relatório e log](../11-prova-consistencia-agenda.md).

A evidência sustenta a estratégia técnica nesse recorte. Não confirma autorização, implementação modular ou regras da universidade. O ADR permanece proposto até decisão da equipe; testes de regressão serão necessários na aplicação real. BL-01 continua parcial por causa das validações P-01/P-02/P-06.

Fundamentação técnica e referências oficiais: [arquitetura](../04-arquitetura.md) e [referências](../10-referencias.md).
