# 4. Proposta de arquitetura e stack

Status: **arquitetura em adoção incremental para desenvolvimento local**. O [experimento BL-01](11-prova-consistencia-agenda.md) verificou a estratégia de consistência; [BL-02](12-base-identidade.md) implementou a base de identidade/histórico. Os demais módulos e as regras institucionais continuam propostos. Registros: [ADR-001](decisoes/ADR-001-monolito-modular.md), [ADR-002](decisoes/ADR-002-consistencia-da-agenda.md) e [ADR-003](decisoes/ADR-003-identidade-e-historico.md). Diagramas e correspondências: [visões](05-visoes.md).

## Estilo recomendado e justificativa

Adotar **monólito modular**: uma aplicação implantável, um banco PostgreSQL e módulos organizados pelas responsabilidades do domínio. O navegador acessa páginas renderizadas pelo servidor. Uma operação pode envolver mais de um módulo dentro da mesma transação, sem coordenação de processos distribuídos.

Reservas, manutenção e habilitações possuem regras relacionadas, e a aprovação precisa confirmar agenda, decisão e histórico de forma atômica. A equipe pequena se beneficia de executar, testar e depurar um único sistema. Não há evidência de escala, times independentes ou requisitos de implantação isolada que justifiquem separar serviços.

Os módulos terão interfaces explícitas para consultas e comandos. Não compartilhar gravações diretas em tabelas de outro módulo, nem duplicar o cálculo de conflito em telas distintas. A agenda é a autoridade para ocupações; Reservas é a autoridade sobre decisões, e Manutenção sobre intervenções. A modularidade é uma disciplina de código e revisão, não uma garantia automática do framework.

## Alternativas consideradas

| Candidato | Vantagens para o KDlab | Custos e limites | Parecer inicial |
| --- | --- | --- | --- |
| Monólito modular com páginas no servidor | Transação local, um fluxo de entrega, ferramentas integradas; separa agenda, reservas e manutenção | Exige conter dependências e revisar fronteiras; falha da aplicação afeta todos os módulos | Recomendado para E1/E2 |
| Monólito convencional em camadas globais, com CRUD por entidade | Arranque simples e poucas convenções | Regras de agenda tendem a se espalhar por controladores/modelos; mudanças cruzadas ficam menos localizadas | Viável para protótipo pequeno, mas menos adequado às invariantes compartilhadas |
| Serviços independentes para reservas, recursos e manutenção | Implantação e escala separadas | Introduz contratos remotos, falhas parciais e coordenação entre reserva e bloqueio; maior esforço operacional | Não recomendado com as necessidades atuais |

Uma SPA com API própria é outra escolha de apresentação, independente do estilo modular. Poderia atender clientes externos no futuro, mas hoje acrescentaria dois fluxos de validação, dependências e testes de interface sem requisito confirmado. A proposta usa templates e formulários.

## Padrões e organização interna

| Padrão proposto | Aplicação e justificativa |
| --- | --- |
| Separação apresentação / casos de uso / persistência | Views tratam HTTP; operações de aplicação coordenam permissão, regra e transação; modelos e consultas usam o ORM |
| Modelo de apresentação do Django (templates, views e models) | Reutiliza formulários e renderização; as decisões de negócio não ficam nos templates |
| Operações explícitas de domínio | `solicitar`, `aprovar`, `cancelar`, `bloquear` e `retirar` tornam as transições revisáveis; não expor edição livre de status |
| Transação por operação crítica | Agrupa decisão, ocupação e evento de sucesso; rollback evita estado parcial |
| Registro de eventos de negócio | Histórico consultável no mesmo banco; sem transformar o sistema em event sourcing |
| Políticas parametrizadas | Exigência de habilitação e permissão por recurso/laboratório, sem duplicar o núcleo para cada tipo de laboratório |

Não se propõe uma camada genérica de repositórios sobre o ORM. Uma abstração adicional só se justifica quando houver variação real de persistência ou isolamento necessário a testes específicos.

## Stack candidata

Não havia stack de aplicação na inspeção inicial. A escolha abaixo prioriza um fluxo único de desenvolvimento; a experiência da equipe permanece desconhecida (P-01). O experimento e a base BL-02 executaram com Python 3.14.4, Django 5.2.19 e psycopg 3.3.9. Python 3.13 foi o candidato inicial e continua sem ensaio específico; a versão efetivamente verificada está registrada para reprodução.

| Camada | Recomendação | Vantagem e testes | Limitação/compromisso |
| --- | --- | --- | --- |
| Linguagem e framework | Python 3.14.4 + Django 5.2.19 na base validada; Python 3.13 continua alternativa compatível ainda não ensaiada | Autenticação, sessões, formulários, ORM, migrações e administração integrados; runner de testes incluído | Requer conhecer Python e particularidades do ORM; estrutura modular depende da equipe |
| Interface | Templates Django, HTML semântico, CSS e JavaScript apenas quando necessário | Um projeto, formulários no servidor e fluxo principal testável sem compilação de frontend | Interações complexas exigiriam trabalho adicional; calendário interativo não é pré-requisito de E1 |
| Persistência | PostgreSQL 17 + psycopg 3 | Banco relacional, intervalos temporais e restrições; mesmo motor em desenvolvimento e testes de integração | Instalação local e extensão `btree_gist`; dependência deliberada de recursos do PostgreSQL |
| Testes | Runner Django, `TestCase`, `TransactionTestCase` e cliente HTTP do framework | Regras/rotas e banco reais; conexões independentes para concorrência | Cliente HTTP não valida renderização visual; complementar com ensaio manual no navegador |
| Ambiente local | `venv` e `pip`; PostgreSQL local ou container apenas se facilitar a instalação | Poucas ferramentas; versões fixadas quando houver código | Equipe precisa combinar uma receita reproduzível; nenhum manifesto foi criado nesta etapa |

Django 5.2 é uma linha LTS compatível com Python 3.13; sua janela de suporte estendido deve ser reavaliada antes da implementação. Consulte as [notas da versão](https://docs.djangoproject.com/en/5.2/releases/5.2/) e a [tabela de suporte](https://www.djangoproject.com/download/). A escolha não se baseia em ser a versão mais recente.

O [backend PostgreSQL do Django](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes) suporta essa combinação. A autenticação integrada oferece usuários, grupos e permissões, mas o alcance por laboratório e as habilitações de domínio devem ser implementados explicitamente ([documentação de autenticação](https://docs.djangoproject.com/en/5.2/topics/auth/default/)).

O [cliente de testes do Django](https://docs.djangoproject.com/en/5.2/topics/testing/tools/) permite exercitar HTTP e templates; verificações de CSRF devem habilitar `enforce_csrf_checks`, pois o cliente as desativa por padrão. Testes de concorrência não serão substituídos por SQLite, mocks ou uma única transação de teste.

Alternativa tecnológica: TypeScript com framework de servidor e PostgreSQL, caso a equipe já domine esse ecossistema. Pode ser adequada, mas exigirá selecionar e integrar autenticação, persistência e testes equivalentes. A escolha deve ser revista pela familiaridade demonstrada, não por preferência abstrata de linguagem. Containers, servidor WSGI e terminação HTTPS para eventual piloto serão definidos quando a infraestrutura for conhecida; não são entregáveis desta fase.

## Consistência da agenda proposta

Manter uma relação `Ocupacao` no módulo Agenda, com recurso, intervalo, tipo, indicador de bloqueio ativo e identificador. Reserva e manutenção referenciam suas ocupações. Pendências não geram ocupação. A origem continua no respectivo módulo; a agenda não depende dos modelos de Reservas ou Manutenção. A Agenda também mantém marcadores de manutenção não encerrada e, em E2, custódia aberta, com prazo e origem identificados. As operações da origem atualizam esses marcadores na mesma transação; eles permitem detectar atraso sem importar módulos de volta nem depender de uma tarefa agendada.

O [PostgreSQL oferece intervalos e operadores de sobreposição](https://www.postgresql.org/docs/17/rangetypes.html). A proposta usa `tstzrange`, limites `[início, fim)`, intervalo não vazio e finito, e recurso obrigatório. A restrição de exclusão compara igualdade do recurso e sobreposição do período, apenas para ocupações bloqueantes. Assim, reservas e manutenção são protegidas na **mesma relação**, evitando uma checagem incompleta entre duas tabelas independentes. Validar a correspondência de cada origem com sua ocupação e sua unicidade dentro da transação.

A [restrição `ExclusionConstraint` do Django](https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/constraints/) permite declarar essa proteção e exige a extensão `btree_gist` nessa combinação. Ela é uma barreira de integridade; a aplicação ainda deve produzir erros compreensíveis e validar seus estados.

Fluxo proposto para aprovar ou alterar um bloqueio:

1. Abrir uma transação explícita e curta; obter a identidade da sessão, sem aceitar ator informado pelo formulário.
2. Bloquear a linha do recurso e depois a da solicitação/manutenção com `select_for_update`; reconsultar estado e condições. Operações sobre o mesmo recurso seguem essa ordem, inclusive cancelamento, inativação e, em E2, movimentações.
3. Verificar perfil, vínculo, ausência de autoaprovação, habilitação e condições operacionais atuais. Conferir intervalo e conflito na agenda para oferecer uma resposta útil.
4. Alterar a origem, criar/alterar/desativar a ocupação e gravar o evento de negócio na mesma transação.
5. Confirmar e retornar sucesso. Se a restrição detectar conflito ou houver falha, reverter o conjunto; fora do bloco transacional, tratar o conflito e informar que a operação não foi concluída.

Bloquear somente reservas existentes não resolve a disputa por um período vazio. A linha estável do recurso permite coordenar essa disputa. O [bloqueio de linhas no PostgreSQL](https://www.postgresql.org/docs/17/explicit-locking.html) fundamenta a coordenação, e [`atomic()`](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) delimita a operação no Django. O isolamento inicial proposto é o padrão READ COMMITTED com esses bloqueios e a restrição de exclusão; ele deve ser exercitado na prova técnica.

Aprovações distintas para o mesmo intervalo: com dados válidos e sem outra ocupação, uma vence, a outra recebe conflito e permanece PENDENTE. Repetição da mesma aprovação não cria segunda ocupação nem segundo evento de sucesso. Aprovação versus cancelamento e manutenção versus aprovação também revalidam o estado após obter o bloqueio.

A auditoria de sucesso participa do commit. Logs de tentativas negadas ou falhas técnicas são separados, sem registrar falsos sucessos nem informações pessoais excessivas. Não há garantia de inviolabilidade contra um administrador do próprio banco; retenção e privilégios operacionais precisam ser definidos antes de uso real.

## Limites operacionais

Agenda representa compromissos planejados e os marcadores operacionais necessários à consulta. Recurso inativo, manutenção vencida não encerrada e empréstimo atrasado podem impedir uso físico mesmo quando um intervalo futuro está livre. A política conservadora proposta suspende novas aprovações até resolver o atraso, indica o motivo na consulta e impede retirada. Antes do vencimento, um empréstimo aberto não impede aprovação futura após o prazo previsto. Não cancelar compromissos existentes automaticamente nem inferir devolução ou reparo pelo relógio. Essa política é proposta em RN-10 a RN-12 e P-06.

O admin do Django poderá auxiliar cadastros simples, mas não deve permitir edição livre de status, ocupações, bloqueios ou eventos que contorne as operações de negócio. Nas telas administrativas, desabilitar essas gravações ou chamar as mesmas operações transacionais. Isso também se aplica a comandos de manutenção de dados da aplicação.

Em BL-02, o admin já é usado para contas e consulta do histórico, com acesso técnico restrito e eventos somente de leitura. A identidade utiliza sessões do Django e modelo de usuário próprio desde a primeira migração; sua decisão está no ADR-003. O Compose atual oferece apenas o PostgreSQL local opcional, sem representar a implantação de piloto proposta na visão de deployment.
