# ADR-003 — Identidade local e histórico administrativo

- Status: **implementado para desenvolvimento local em BL-02; políticas institucionais pendentes**.
- Data: 14/11/2026.
- Relacionados: RF-01, parte de RF-11/RF-13, RNF-02/RNF-03/RNF-08.

## Contexto

A prova de concorrência BL-01 sustentou a estratégia de banco. A continuação solicitada avança a base executável sem integrar sistemas institucionais nem implementar todo o domínio. Precisamos provisionar contas, impedir uso por inativos e estabelecer o registro administrativo desde o início.

## Decisão

Usar autenticação e sessões de banco do Django, com `Usuario(AbstractUser)` definido antes da primeira migração da aplicação. Manter login por nome de usuário, sem cadastro público. O primeiro superusuário é provisionado pelo comando técnico do framework; novas contas são administradas pelo painel.

O painel inicial é restrito a superusuário técnico ativo com `is_staff`. Esse usuário não define o perfil administrador do produto: papéis e alcance por laboratório serão implementados nos próximos incrementos, sem dispensar as regras de domínio.

Registrar criação, edição e alterações de credenciais realizadas pelo painel no módulo Histórico. Gravação e evento compartilham a transação; os eventos guardam identificadores e nomes de campos, sem copiar senhas, hashes ou valores pessoais. Identificadores simples mantêm o Histórico independente do modelo de Identidade. O painel permite consultar eventos, sem editá-los ou removê-los.

## Alternativas

- Usuário padrão do Django: atende à autenticação básica, mas a substituição após migrações e relações do domínio seria mais custosa. A subclasse inicial preserva uma extensão simples.
- API de tokens/JWT e frontend separado: acrescenta gestão de tokens e duas aplicações sem cliente externo confirmado. Sessões e templates atendem à base atual.
- SSO institucional: exigiria integração expressamente fora do escopo inicial.
- Apenas o log interno do admin: registra ações técnicas, mas não estabelece a interface de histórico de negócio para os próximos módulos. Por isso, os eventos mínimos próprios são gravados junto à operação.

## Consequências e limites

A base usa as dependências fixadas já verificadas: Django 5.2.19 e psycopg 3.3.9, com PostgreSQL 17. O ambiente executou Python 3.14.4; Python 3.13 ainda não foi ensaiado. A experiência da equipe não foi inferida nem validada.

Bootstrap por CLI e alterações diretas no ORM não passam pelo histórico administrativo. O banco e o shell continuam sendo acessos privilegiados. Perfis de domínio, retenção de histórico e operação de piloto ainda precisam de definição. A configuração local não é um deploy de produção.

## Evidência

26 testes em PostgreSQL real, sem divergência de migrações; inicialização HTTP e bootstrap ensaiados em ambiente descartável. Ver [relatório BL-02](../12-base-identidade.md). A revisão visual ficou pendente por indisponibilidade do navegador.

Fundamentação: [personalização de autenticação](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project), [autenticação do Django](https://docs.djangoproject.com/en/5.2/topics/auth/default/), [admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/) e [CSRF](https://docs.djangoproject.com/en/5.2/howto/csrf/). As escolhas de domínio são decisões do KDlab, não conclusões dessas fontes.
