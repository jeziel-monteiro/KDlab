# 3. Requisitos, restrições e regras

Os temas funcionais e as invariantes de conflito/manutenção foram confirmados no pedido; os detalhes operacionais abaixo são **propostas**, sem validação de usuários. E1/E2 indicam o incremento recomendado, não um compromisso de prazo. As hipóteses H e pendências P estão no [registro central](09-decisoes-e-pendencias.md).

## Requisitos funcionais

| ID | Requisito inicial | Origem e detalhamento | Entrega |
| --- | --- | --- | --- |
| RF-01 | Autenticar usuário ativo e encerrar sessão | Acesso por perfil confirmado; conta local provisionada é H-04 | E1 |
| RF-02 | Cadastrar, editar, consultar e inativar laboratórios e equipamentos, com identificação única | Cadastro confirmado; unidade individual e inativação sem exclusão histórica são H-01/H-02 | E1 |
| RF-03 | Consultar disponibilidade de um recurso por intervalo válido | Confirmado; considerar reservas aprovadas, bloqueios de manutenção e inativação | E1 |
| RF-04 | Criar solicitação própria com recurso, início, fim e finalidade; iniciar em PENDENTE | Solicitação confirmada; campos mínimos e estado inicial propostos | E1 |
| RF-05 | Aprovar ou rejeitar solicitação pendente, registrando decisor, instante e justificativa de rejeição | Confirmado; revalidar regras no momento da aprovação, sem autoaprovação (H-05) | E1 |
| RF-06 | Cancelar solicitação/reserva segundo estado, propriedade e permissão, com motivo e liberação da ocupação | Cancelamento confirmado; limites de horário e papéis são H-05/H-06 | E1 |
| RF-07 | Listar solicitações próprias e, para operador elegível, as dos laboratórios sob sua responsabilidade | Acompanhamento proposto para tornar o fluxo de reservas utilizável | E1 |
| RF-08 | Registrar manutenção com recurso, motivo e intervalo; encerrar ou cancelar bloqueio de forma auditável | Manutenção confirmada; política de conflito e liberação é H-07 | E1 |
| RF-09 | Registrar retirada de equipamento referente a reserva aprovada, com recebedor, operador e instante | Retirada confirmada; empréstimo vinculado a uma reserva é H-08 | E2 |
| RF-10 | Registrar devolução, instante e condição do equipamento; impedir devolução duplicada e indicar atraso | Devolução confirmada; atraso como condição calculada é proposta | E2 |
| RF-11 | Administrar contas, perfis e vínculos de responsabilidade com laboratórios | Administração confirmada; escopo por laboratório proposto | E1 |
| RF-12 | Configurar exigências por recurso e registrar, revogar e consultar habilitações de usuários | Treinamento/autorização confirmado; registro manual e validade são H-09 | E1 |
| RF-13 | Registrar e consultar histórico autorizado de cadastros e decisões, bloqueios, habilitações e movimentações | Histórico confirmado; dados mínimos e escopo de consulta propostos | E1; movimentações em E2 |

## Requisitos não funcionais

| ID | Atributo e requisito | Evidência proposta |
| --- | --- | --- |
| RNF-01 | Consistência: nenhum par de ocupações bloqueantes pode se sobrepor para um recurso; reserva, agenda e evento de sucesso devem confirmar ou reverter juntos | CQ-01, CQ-02 e CQ-05; PostgreSQL real |
| RNF-02 | Autorização: verificar identidade, perfil, objeto, vínculo e habilitação no servidor a cada operação; negar por padrão | CQ-03, CQ-04 e CQ-10 |
| RNF-03 | Rastreabilidade: cada operação principal bem-sucedida deve gerar evento com ator, instante, ação, alvo e resultado; aplicação não oferece edição/exclusão desses eventos | CQ-05; retenção e acesso em P-10 |
| RNF-04 | Desempenho: proposta de p95 de até 2 s na consulta e 3 s nas decisões, sob a carga candidata de CQ-06 | Medição ainda não realizada; validar P-08 |
| RNF-05 | Modificabilidade e testabilidade: manter dependências sem ciclos e regras exercitáveis sem interface gráfica; testar invariantes no banco de produção escolhido | Revisão das dependências e CQ-09 |
| RNF-06 | Usabilidade: interface em pt-BR, estados e erros compreensíveis, campos rotulados e fluxo principal operável por teclado | CQ-08; não equivale a certificação de acessibilidade |
| RNF-07 | Recuperabilidade: propor perda máxima de 24 h e restauração em até 4 h para eventual piloto, condicionadas à infraestrutura e à rotina de backup | CQ-07; validar P-09; nenhum SLA contratado |
| RNF-08 | Proteção de dados: minimizar informações pessoais, restringir histórico e não registrar senhas ou segredos; senhas tratadas pelo framework e HTTPS em eventual implantação | CQ-03/CQ-05 e revisão técnica; políticas institucionais em P-10 |

Os limites de latência e recuperação são metas candidatas, sem comprovação. A ausência de conflitos e a proibição de acesso indevido são invariantes esperadas do produto; as quantidades de execuções dos ensaios são propostas de avaliação.

## Restrições

| ID | Restrição | Situação |
| --- | --- | --- |
| RES-01 | Documentar conforme o roteiro local, inspirado na ISO/IEC/IEEE 42010, sem declarar conformidade integral não verificada | Confirmada |
| RES-02 | Excluir pagamentos, compras, finanças, IoT e integrações institucionais nesta fase | Confirmada |
| RES-03 | Favorecer simplicidade de desenvolvimento, testes e operação para equipe acadêmica pequena | Diretriz confirmada; capacidade e prazos pendentes |
| RES-04 | Etapas iniciais locais e preservação de arquivos/alterações; publicação do repositório no GitHub autorizada posteriormente, sem deploy da aplicação | Pedido inicial e continuações; autorização de publicação em 14/11/2026, sem ampliar o escopo funcional |
| RES-05 | Usar um recurso exclusivo por solicitação, sem recorrência nem reservas compostas em E1 | Hipótese H-01; revisar se o domínio exigir outra unidade de reserva |

## Regras de negócio

| ID | Regra | Situação |
| --- | --- | --- |
| RN-01 | Um recurso não pode ter reservas aprovadas com intervalos sobrepostos | Confirmada |
| RN-02 | Um recurso não pode ser disponibilizado em intervalo bloqueado por manutenção | Confirmada |
| RN-03 | Início deve anteceder fim e não estar no passado ao solicitar/aprovar. Usar intervalos semiabertos `[início, fim)`; 10h–11h e 11h–12h são adjacentes e compatíveis | Proposta H-03; armazenar instantes em UTC e exibir fuso institucional |
| RN-04 | PENDENTE não ocupa a agenda. Pendências concorrentes são permitidas; uma consulta não garante vaga | Proposta H-06 |
| RN-05 | Na criação, recusar conflito já conhecido com reserva aprovada/manutenção; na aprovação, verificar novamente recurso ativo, intervalo, habilitação e agenda | Proposta; aprovação é a autoridade final |
| RN-06 | A habilitação exigida deve estar vigente e não revogada, cobrindo todo o período solicitado; verificar na solicitação, aprovação e retirada | Necessidade confirmada; vigência e momentos são H-09 |
| RN-07 | Operações devem respeitar perfil, propriedade, vínculo e transições; não permitir autoaprovação | Proposta H-05 |
| RN-08 | Aprovação e criação/alteração de manutenção usam a mesma proteção transacional da agenda | Solução proposta para RN-01/RN-02; ADR-002 |
| RN-09 | Ao tentar inserir manutenção conflitante, recusar a operação e informar o conflito ao operador autorizado. Não cancelar reserva silenciosamente | Proposta H-07; emergência requer cancelamento explícito antes do bloqueio |
| RN-10 | Não excluir registros históricos. Inativação de recurso com compromisso futuro exige resolver esses compromissos explicitamente | Proposta; inativação não é atalho para manutenção temporal |
| RN-11 | Uma retirada exige reserva de equipamento aprovada, não cancelada, dentro de seu período, sem bloqueio/inativação e sem empréstimo aberto do equipamento | Proposta H-08; um único empréstimo por reserva em E2 |
| RN-12 | Empréstimo aberto não termina ao vencer o horário. Atraso impede nova retirada e novas aprovações para o equipamento; consulta destaca indisponibilidade e compromissos existentes sob risco até a devolução | Proposta H-08; não desfazer aprovações futuras automaticamente |

Para A e B, há sobreposição quando `A.início < B.fim` e `B.início < A.fim`. Limites adjacentes não se sobrepõem. Margens para preparação/limpeza e horário de funcionamento não foram definidos (P-03).

## Estados e transições propostos

### Reserva

| Origem | Ação e condição | Destino | Efeito na agenda |
| --- | --- | --- | --- |
| Nova | Solicitar conforme RF-04/RN-05/RN-06 | PENDENTE | Nenhum |
| PENDENTE | Aprovar por operador elegível, passando todas as regras | APROVADA | Criar ocupação no mesmo commit |
| PENDENTE | Rejeitar por operador elegível, com motivo | REJEITADA | Nenhum |
| PENDENTE | Cancelar pelo solicitante ou operador elegível | CANCELADA | Nenhum |
| APROVADA | Cancelar antes do início pelo solicitante; operador elegível pode cancelar depois do início se não houver empréstimo aberto, com motivo | CANCELADA | Desativar ocupação no mesmo commit |

REJEITADA e CANCELADA são terminais. Edição de recurso/período após envio requer cancelar e criar nova solicitação; não há reabertura. Uma APROVADA passada permanece como registro da decisão; seu intervalo encerrado deixa de bloquear naturalmente. Solicitação PENDENTE cujo início já passou não pode ser aprovada; pode ser rejeitada/cancelada. Retirada/devolução pertencem ao estado do empréstimo, não ao estado de decisão da reserva.

### Manutenção

Criar manutenção gera estado REGISTRADA e ocupação bloqueante no intervalo. O estado pode passar a ENCERRADA mediante término real, após o início, ou a CANCELADA se ainda não iniciada. Antes do início ela está programada; dentro do período, em andamento, como condições calculadas. Encerrar antes do fim previsto reduz o fim da ocupação ao instante de encerramento; encerrar depois preserva o intervalo passado. Prorrogar exige nova checagem transacional; o vencimento do intervalo não comprova reparo físico. Se o prazo vencer sem encerramento, suspender novas aprovações e retiradas para o recurso até resolução pelo responsável, sem cancelar compromissos existentes automaticamente (H-07). A consulta deve informar essa incerteza operacional, inclusive em períodos futuros. A Agenda mantém o marcador necessário a essa verificação, atualizado na mesma transação da origem.

### Empréstimo (E2)

Retirada válida cria ABERTO; devolução válida produz DEVOLVIDO. Atrasado significa ABERTO com prazo previsto vencido, sem uma transição automática. Tentativas duplicadas não criam nova movimentação nem novo evento de sucesso. Se houver defeito na devolução, registrar a condição e encaminhar ao fluxo de manutenção; a resolução de conflitos continua explícita.

Essas máquinas de estados são propostas a validar em P-05/P-06. As condições operacionais de manutenção vencida e empréstimo atrasado complementam a agenda planejada; a agenda não prova disponibilidade física.

## Situação de implementação em BL-02

RF-01 está implementado para contas locais. RF-11 tem provisionamento/inativação técnicos pelo painel; perfis do produto e vínculos ainda estão pendentes. RF-13 registra alterações de contas realizadas no painel, sem representar o histórico dos módulos futuros. Os demais RF continuam planejados. As evidências de identidade, proteção de sessão e atomicidade estão em [12](12-base-identidade.md); a revisão visual não foi concluída.
