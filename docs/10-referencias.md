# 10. Referências e limites das fontes

Fontes consultadas em 13 e 14/11/2026. A documentação técnica fundamenta capacidades das ferramentas; a adequação ao KDlab é uma recomendação de engenharia desta proposta, não uma conclusão atribuída aos autores dessas fontes.

## Referências principais do trabalho

1. **Pedido de definição inicial do KDlab**, fornecido na conversa. Fonte de contexto, escopo, perfis e restrições. Não é uma entrevista nem validação institucional.
2. **Roteiro da disciplina de Arquitetura de Software**, fornecido para consulta local e não distribuído neste repositório. Fonte principal da organização acadêmica: introdução, interessados, estilos/padrões, três visões, domínio/linha de produtos, avaliação e referências. Autoria docente e enunciado adicional não foram identificados no material disponível.

O PDF não é o texto integral da ISO/IEC/IEEE 42010. A norma integral não foi consultada, e esta documentação não declara conformidade com uma edição específica. A distribuição de preocupações, visões e correspondências segue o roteiro recebido, com cobertura inicial e pendências explícitas.

## Documentação técnica oficial consultada

| Fonte | Uso na proposta |
| --- | --- |
| [Django 5.2 — notas da versão](https://docs.djangoproject.com/en/5.2/releases/5.2/) | Linha LTS e compatibilidade de Python |
| [Django — versões e suporte](https://www.djangoproject.com/download/) | Verificar janela de suporte antes de implementar; sem congelar patch nesta fase |
| [Django 5.2 — autenticação](https://docs.djangoproject.com/en/5.2/topics/auth/default/) | Usuários, sessões, grupos e permissões; alcance por laboratório é regra adicional do KDlab |
| [Django 5.2 — usuário customizado](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project) | Subclasse inicial de `AbstractUser` e decisão de identidade em BL-02 |
| [Django 5.2 — administração](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/) | Provisionamento técnico e pontos de registro de histórico |
| [Django 5.2 — proteção CSRF](https://docs.djangoproject.com/en/5.2/howto/csrf/) | Formulários de login/logout com proteção e testes de token |
| [Django 5.2 — bancos de dados](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes) | Compatibilidade PostgreSQL/psycopg |
| [Django 5.2 — transações](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) | Delimitação de operação atômica e tratamento de rollback |
| [Django 5.2 — QuerySet e `select_for_update`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update) | Bloqueio e teste transacional; não equivale a trava em memória |
| [Django 5.2 — restrições PostgreSQL](https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/constraints/) | `ExclusionConstraint`, GiST, extensão `btree_gist` e conflitos de integridade |
| [Django 5.2 — ferramentas de teste](https://docs.djangoproject.com/en/5.2/topics/testing/tools/) | Cliente HTTP, testes transacionais e limites da validação visual |
| [PostgreSQL 17 — tipos intervalo](https://www.postgresql.org/docs/17/rangetypes.html) | Intervalos, limites semiabertos e exclusão de sobreposição |
| [PostgreSQL 17 — bloqueios explícitos](https://www.postgresql.org/docs/17/explicit-locking.html) | Coordenação por linha do recurso e risco de contenção |

## Apoio técnico à prova BL-01

- [Skill Supabase Postgres Best Practices](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/SKILL.md), mantida pela Supabase; consultada como orientação para PostgreSQL genérico, sem instalar a plataforma.
- [Transações curtas](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/lock-short-transactions.md) e [ordem consistente de locks](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/lock-deadlock-prevention.md), referências da mesma skill.
- [psycopg 3 — transações](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), para conexão e delimitação transacional do ambiente de prova.

Não foram usadas fontes para supor demanda, hardware institucional disponível ou experiência da equipe. Os números de carga, tempo e recuperação em [07](07-avaliacao.md) continuam propostas de ensaio; os resultados observados estão separados em [11](11-prova-consistencia-agenda.md) e [12](12-base-identidade.md). As referências externas não substituem a validação dos processos da universidade.
