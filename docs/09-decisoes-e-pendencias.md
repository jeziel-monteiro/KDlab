# 9. Informações confirmadas, hipóteses e decisões pendentes

Este registro distingue origem de informação de recomendação. Não foram realizadas entrevistas nem validações com usuários. Os validadores abaixo são papéis a envolver, sem designação nominal.

## Informações confirmadas

| ID | Informação | Evidência |
| --- | --- | --- |
| F-01 | KDlab é um projeto acadêmico de gestão de laboratórios/equipamentos com possibilidade de uso universitário real | Pedido do projeto |
| F-02 | Há três grupos de uso: solicitantes, técnicos/responsáveis e administradores; escopo inclui reservas, empréstimos, manutenção, acesso e histórico | Pedido do projeto |
| F-03 | Reservas aprovadas não podem conflitar; manutenção bloqueia recurso; há recursos com exigência de treinamento/autorização; concorrência precisa preservar consistência | Pedido do projeto |
| F-04 | Pagamentos, compras, finanças, IoT e integração institucional ficam fora do escopo inicial | Pedido do projeto |
| F-05 | A documentação deve seguir o roteiro; nomes, entrevistas e resultados não podem ser inventados | Pedido e PDF local |
| F-06 | Antes desta organização, o projeto continha somente `docs/Documento_Arquitetura_Software_ISO_42010.pdf` como arquivo de produto, sem stack ou código | Inspeção em 13/11/2026; diretórios locais vazios preservados |
| F-07 | Na inspeção inicial, o Git efetivo estava na pasta pai, sem commits, incluindo outros projetos e alterações locais externas ao KDlab | Estado inicial preservado até a definição de um repositório independente; ver F-10 |
| F-08 | Um experimento isolado da agenda passou em 17 testes no PostgreSQL 17.11, incluindo 100 rodadas com 20 conexões de aprovação | [Execução de 14/11/2026](11-prova-consistencia-agenda.md); não valida perfis nem processo institucional |
| F-09 | A base BL-02 implementa contas locais, sessão e histórico administrativo; 26 testes passaram e a inicialização HTTP foi verificada | [Relatório BL-02](12-base-identidade.md); revisão visual pendente e regras institucionais sem validação |
| F-10 | KDlab possui repositório Git independente em `main`, com remoto `git@github.com:jeziel-monteiro/KDlab.git` | Preparação da publicação solicitada em 14/11/2026; índice da pasta pai preservado |

O PDF traz UFAM/ICET na capa e exemplos de desenvolvedores/datas. Isso identifica o modelo recebido, sem confirmar instituição de implantação, composição da equipe ou histórico do KDlab.

## Hipóteses de trabalho

| ID | Hipótese adotada para avançar | Efeito se mudar |
| --- | --- | --- |
| H-01 | Um recurso exclusivo e um intervalo por reserva, sem recorrência, kits ou compartilhamento por capacidade em E1 | Muda o algoritmo e a unidade de conflito |
| H-02 | Laboratório pode ser reservado inteiro; equipamento é individual; associação física não bloqueia recursos filhos automaticamente | Pode exigir política hierárquica e bloqueio de múltiplos recursos |
| H-03 | Usar `[início, fim)`, UTC na persistência e `America/Manaus` como fuso candidato da instituição; não reservar com início no passado | Muda validação, apresentação e testes de limite; fuso do cliente não prova o da instituição |
| H-04 | Uma instituição por instalação, contas locais provisionadas por administrador e consulta autenticada | Muda identidade, onboarding e isolamento de dados |
| H-05 | Escopo de operação por laboratório; solicitantes veem dados próprios; sem autoaprovação; administrador não ignora invariantes | Muda matriz de acesso e organização de operadores |
| H-06 | Pendências não ocupam; solicitante cancela aprovada só antes do início; alteração de período exige nova solicitação | Muda estados, disponibilidade e experiência de uso |
| H-07 | Manutenção conflitante é recusada, sem cancelamento automático; prazo vencido sem encerramento suspende novas aprovações até resolução humana | Muda política de emergência e marcadores operacionais |
| H-08 | Empréstimo exige reserva aprovada de equipamento; não há retirada parcial; atraso mantém custódia aberta e bloqueia nova retirada/novas aprovações | Muda máquina de custódia e disponibilidade operacional |
| H-09 | Habilitações manuais por tipo, com concedente, validade e revogação; devem cobrir todo o intervalo e ser revalidadas | Muda autorização e pode exigir componente de treinamento |
| H-10 | E1 entrega reservas com bloqueios; E2 acrescenta movimentações; prazos e esforço ainda não estimados | Muda priorização, sem remover empréstimos do escopo do produto |
| H-11 | O painel inicial usa superusuário técnico para provisionar contas, sem equivalência automática com o perfil administrador do produto | A implementação dos papéis de domínio ainda precisa da política de P-04 |

## Decisões técnicas propostas

| Decisão | Recomendação | Situação |
| --- | --- | --- |
| Estilo e apresentação | Monólito modular, páginas no servidor, um banco | [ADR-001](decisoes/ADR-001-monolito-modular.md), em adoção incremental local por BL-02 |
| Stack | Base validada em Python 3.14.4, Django 5.2.19, PostgreSQL 17, psycopg 3.3.9 e HTML/CSS; Python 3.13 ainda não ensaiado | [04](04-arquitetura.md), adoção técnica provisória; experiência da equipe e infraestrutura institucional pendentes |
| Concorrência | Agenda comum, exclusão temporal, transação e lock do recurso | [ADR-002](decisoes/ADR-002-consistencia-da-agenda.md), com evidência técnica de BL-01; adoção no produto segue proposta |
| Variação do domínio | Uma base comum configurável, sem forks por laboratório | [06](06-dominio-variabilidade.md), revisar casos reais |
| Avaliação | Revisão guiada por cenários e testes no banco real | [07](07-avaliacao.md), com recorte transacional registrado em [11](11-prova-consistencia-agenda.md) |
| Identidade e histórico | Usuário próprio, sessões Django e eventos transacionais das alterações pelo painel | [ADR-003](decisoes/ADR-003-identidade-e-historico.md), implementado em BL-02 |

## Pendências e encaminhamento

| ID | O que validar | Quem pode validar | Encaminhamento e impacto |
| --- | --- | --- | --- |
| P-01 | Experiência técnica da equipe, restrições da disciplina, prazo e confirmação da stack | Equipe e docência | A stack foi adotada provisoriamente em BL-02 para desenvolvimento local reversível; revisar adequação com a equipe antes de expandir o produto |
| P-02 | Reserva da sala inteira ou de estações? Equipamento pode ser reservado independentemente da sala? Há kits? | Técnicos e responsáveis | Antes do modelo de recursos e da prova; manter H-01/H-02 até revisão |
| P-03 | Fuso institucional, horários, antecedência, duração e margens entre reservas | Responsáveis e solicitantes | Antes do formulário definitivo; usar H-03, sem inventar limites quantitativos |
| P-04 | Perfis, vínculos, autoaprovação e disponibilidade de segundo operador | Administradores e responsáveis | Antes de BL-03/BL-07; seguir matriz conservadora proposta |
| P-05 | Cancelamento após início, pendências vencidas, edição/reenvio e justificativas obrigatórias | Responsáveis e solicitantes | Antes de BL-06/BL-08; revisar máquina de estados |
| P-06 | Procedimento para manutenção urgente, prorrogação, prazo vencido, atrasos e compromissos já aprovados | Técnicos e responsáveis | Antes de BL-01/BL-09/BL-11; validar política conservadora e modelo de marcadores |
| P-07 | Quem comprova treinamento, quais tipos e validades e como ocorre revogação | Administradores e responsáveis | Antes de BL-04; começar com registro manual, sem curso/certificação |
| P-08 | Volume de recursos/usuários e metas de resposta | Responsáveis e equipe | Antes de CQ-06; valores atuais são carga sintética e metas propostas |
| P-09 | Host, instalação de extensões, orçamento, responsável operacional, backup, HTTPS e recuperação | Equipe e infraestrutura | Extensão antes da prova; operação antes do piloto; nenhuma implantação autorizada nesta etapa |
| P-10 | Dados pessoais necessários, visibilidade, retenção e acesso ao histórico | Instituição, administração e responsáveis | Minimizar dados em E1; validar política antes do uso real, sem afirmar conformidade legal |
| P-11 | Nomes dos integrantes, autoria e regras de entrega/licença | Equipe e docência | Atualizar ficha técnica quando informados; não copiar exemplos nem escolher licença sem decisão |
| P-12 | Limite do repositório Git e forma de versionar o KDlab | Responsável pelo workspace/equipe | Resolvida em 14/11/2026: Git independente em KDlab, branch `main` e remoto informado pelo usuário; sem alterar o índice da pasta pai |
| P-13 | Revisão visual e navegação manual das páginas de identidade em desktop/mobile | Equipe | A conexão do navegador estava indisponível em BL-02; retomar quando o ambiente estiver disponível, sem tratar testes HTTP como revisão visual |

As pendências permitem planejar e documentar agora. As que alteram o modelo e a autorização devem ser revisadas antes da implementação correspondente. Uma hipótese não se torna confirmada apenas por ter sido repetida em um requisito ou diagrama.

A prova BL-01 confirmou disponibilidade de `btree_gist` no ambiente temporário local. Isso não resolve P-09 para a infraestrutura de um eventual piloto, nem confirma as hipóteses H usadas pelos testes.

A continuação para BL-02 autorizou desenvolver a base, sem confirmar experiência da equipe ou processos da universidade. Por isso, P-01/P-02/P-06 continuam abertas e não foram usadas como bloqueio para a identidade local, que não implementa a alocação de recursos.
