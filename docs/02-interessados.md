# 2. Interessados e preocupações arquiteturais

Os perfis de usuários vêm do pedido. Os representantes individuais e suas prioridades ainda não foram consultados. Equipe, docência e operação são interessados propostos pelo contexto acadêmico e pela possibilidade de implantação.

| ID | Interessado | Preocupação arquitetural | Requisitos e avaliação relacionados |
| --- | --- | --- | --- |
| INT-01 | Alunos e professores | Encontrar recurso, compreender estado e resultado da solicitação, proteger dados pessoais | RF-03 a RF-07; RNF-04 e RNF-06; CQ-06 e CQ-08 |
| INT-02 | Técnicos e responsáveis | Não aprovar conflitos, atuar apenas nos próprios laboratórios, controlar manutenção e custódia | RF-05, RF-08 a RF-10; RNF-01 e RNF-02; CQ-01 a CQ-05 e CQ-10 |
| INT-03 | Administradores | Gerenciar contas, perfis, recursos, vínculos e habilitações; rastrear alterações | RF-01, RF-02, RF-11 a RF-13; RNF-02 e RNF-03; CQ-03 a CQ-05 |
| INT-04 | Equipe de desenvolvimento | Entender regras, testar concorrência e alterar módulos sem propagar mudanças desnecessárias | RNF-05; CQ-09; visões de módulos e execução |
| INT-05 | Docência e avaliadores da disciplina | Examinar justificativas, alternativas, rastreabilidade e resultados de avaliação | RES-01; índice do roteiro, ADRs e plano de avaliação |
| INT-06 | Responsáveis pela infraestrutura, caso haja implantação | Operar, recuperar dados e diagnosticar falhas com recursos disponíveis | RNF-03 e RNF-07; CQ-07; visão de implantação; P-09 |

## Política inicial de acesso — hipótese H-05

Perfis concedem capacidades; vínculo com laboratório restringe o alcance dessas capacidades. A autorização também depende do objeto: propriedade da solicitação, recurso associado e habilitação. Ocultar um botão não substitui a verificação no servidor.

| Ação | Aluno/professor | Técnico/responsável | Administrador |
| --- | --- | --- | --- |
| Consultar catálogo e disponibilidade | Sim, autenticado | Sim | Sim |
| Solicitar e acompanhar reserva própria | Sim | Sim | Sim |
| Cancelar solicitação própria pendente | Sim | Sim | Sim |
| Cancelar reserva própria aprovada antes do início | Proposto: sim | Proposto: sim | Proposto: sim |
| Analisar ou cancelar reservas de terceiros | Não | Apenas em laboratório vinculado, com justificativa | Sim, com justificativa |
| Registrar manutenção, retirada e devolução | Não | Apenas em laboratório vinculado | Sim |
| Cadastrar/alterar recursos | Não | Proposto: apenas consultar; edição a validar | Sim |
| Gerenciar contas, perfis, vínculos e habilitações | Não | Não | Sim |
| Consultar histórico | Apenas eventos das próprias solicitações, com dados mínimos | Eventos dos laboratórios vinculados | Histórico administrativo global |

Um técnico pode ter múltiplos vínculos, e um usuário pode acumular perfis. O administrador não recebe permissão para violar as regras de conflito, manutenção ou treinamento. O perfil administrador do produto não deve ser confundido com uma conta técnica de superusuário do framework.

Proposta conservadora: ninguém aprova a própria solicitação, inclusive administrador. É necessário outro operador elegível; a disponibilidade de ao menos dois operadores é uma pendência organizacional (P-04). Contas inativas não podem realizar operações.

## Questões para validação futura

As permissões de cadastro dos técnicos, a separação entre técnico e responsável e a visibilidade do histórico precisam ser revistas com representantes dos perfis. Também é preciso definir quem pode atestar treinamentos, a validade exigida e o procedimento para emergências de manutenção. O [registro de pendências](09-decisoes-e-pendencias.md) centraliza essas decisões.

Na implementação BL-02, o acesso administrativo é exclusivo do superusuário técnico usado no bootstrap e no provisionamento de contas. Ele não implementa o perfil administrador da tabela acima. A matriz permanece proposta para os próximos fluxos; a base atual só disponibiliza contas, sessão e histórico administrativo. Ver [limites de BL-02](12-base-identidade.md).
