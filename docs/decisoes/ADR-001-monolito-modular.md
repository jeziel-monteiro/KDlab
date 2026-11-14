# ADR-001 — Monólito modular com apresentação no servidor

- Status: **em adoção incremental para desenvolvimento local; validação institucional pendente**.
- Data: 13/11/2026.
- Validação: equipe do projeto; docente pode revisar aderência acadêmica. Nomes não informados.

## Contexto

O KDlab precisa coordenar aprovação de reservas, manutenção, autorização e histórico. A equipe acadêmica é pequena e não há código ou stack existente. Escala e infraestrutura ainda não foram medidas. RNF-01 exige consistência entre dados que atravessam essas responsabilidades.

## Decisão proposta

Uma aplicação web com módulos de Identidade, Catálogo, Agenda, Reservas, Manutenção, Empréstimos e Histórico; um PostgreSQL compartilhado; templates e formulários no servidor. Começar com Empréstimos apenas em E2. Cada módulo mantém suas operações e dados sob responsabilidade explícita. Diagramas em [05](../05-visoes.md).

## Alternativas

Monólito convencional em camadas globais oferece arranque simples, mas facilita espalhar regras entre CRUDs. Serviços independentes permitem evolução/escala separadas, porém complicam a atomicidade da agenda e a operação. SPA com API adiciona flexibilidade de interface, com mais ferramentas e testes sem demanda atual por outros clientes. A comparação completa e a stack candidata estão em [04](../04-arquitetura.md).

## Consequências

Transações locais e um fluxo de execução reduzem esforço inicial. Testes de casos de uso podem dispensar a tela. Em contrapartida, módulos compartilham banco, versão e falhas da aplicação; fronteiras podem se degradar se a equipe gravar diretamente dados de outro módulo. Revisões de dependências e testes de contratos são necessários.

## Reavaliação

Reabrir a decisão se medições mostrarem gargalo localizado que não possa ser resolvido no monólito, surgirem equipes com ciclos independentes ou clientes externos exigirem contratos próprios. Esses gatilhos são condições de revisão, não previsão de migração.

## Realização inicial em 14/11/2026

A continuação pelo BL-02 implementou a base Django com Identidade, Histórico e apresentação no servidor. Isso inicia a adoção do estilo, sem representar o monólito completo ou uma aprovação institucional. Ver [ADR-003](ADR-003-identidade-e-historico.md) e [evidências](../12-base-identidade.md).
