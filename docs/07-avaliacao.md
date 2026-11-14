# 7. Avaliação proposta da arquitetura

Status: **plano com evidências parciais**. A [prova BL-01](11-prova-consistencia-agenda.md) registrou resultados transacionais relacionados a CQ-01/CQ-02/CQ-05. A [base BL-02](12-base-identidade.md) acrescentou 26 testes de identidade e histórico, relacionados a partes de CQ-03/CQ-05. Os cenários completos do produto seguem pendentes; não houve entrevistas ou validação com usuários, e a revisão visual de BL-02 ficou indisponível.

## Atributos prioritários

Priorizar consistência da agenda e autorização, pois uma aprovação incorreta compromete o uso do recurso. Rastreabilidade e testabilidade sustentam diagnóstico e manutenção. Desempenho, usabilidade e recuperação devem ser medidos com a infraestrutura e os usuários disponíveis. Escalabilidade permanece uma preocupação de evolução, sem demanda quantitativa confirmada.

## Cenários verificáveis

Todos os cenários explicitam fonte, estímulo, ambiente, artefato, resposta e medida. Quantidades de usuários, repetições, dados e limites de tempo são **propostas para revisão**, sem validação de carga real. Zero sobreposição indevida e zero autorização indevida são resultados exigidos pelas regras. A evidência do recorte já ensaiado está em 11; ela não demonstra os cenários completos na aplicação.

O documento 12 separa os testes da base de identidade da avaliação futura de autorização por laboratório. O tempo da suíte, executada com hasher rápido somente em testes, não deve ser usado como medida de latência de login ou carga do sistema.

### CQ-01 — Aprovações concorrentes (RNF-01; RF-05)

- Fonte e estímulo: operadores elegíveis tentam aprovar solicitações distintas para o mesmo recurso e intervalo.
- Ambiente: PostgreSQL, dados válidos, nenhuma ocupação anterior, 20 conexões independentes liberadas por barreira de início.
- Artefato: operação de aprovação, Agenda, restrição de exclusão e Histórico.
- Resposta: exatamente uma aprovação confirma; as outras informam conflito, permanecem PENDENTES e não registram sucesso.
- Medida proposta: repetir 100 rodadas; zero pares de ocupações bloqueantes sobrepostas, uma aprovação e um evento de sucesso por rodada; conclusão da rodada em até 10 s no ambiente registrado.
- Verificação: `TransactionTestCase` ou harness equivalente com conexões próprias; consultar estados, ocupações e eventos após todos os commits. Também testar intervalos adjacentes, recurso diferente e repetição da mesma aprovação.

### CQ-02 — Aprovação versus manutenção (RNF-01; RF-05/RF-08)

- Fonte e estímulo: um responsável registra manutenção enquanto outro aprova reserva do mesmo recurso e período.
- Ambiente: banco real, recurso livre e duas transações sincronizadas; depois repetir com manutenção já registrada.
- Artefato: operações de Reservas/Manutenção e Agenda comum.
- Resposta: somente uma ocupação conflitante confirma. Se a manutenção vence, a reserva permanece pendente; se a reserva vence, a manutenção não é registrada como bloqueio bem-sucedido e informa o conflito.
- Medida proposta: 100 rodadas concorrentes, zero sobreposição; em todas as tentativas após manutenção confirmada, a consulta indica indisponível e a aprovação é negada.
- Verificação: inspecionar o banco, não apenas respostas HTTP; testar prorrogação conflitante, cancelamento antes do início e encerramento antecipado válido. Manutenção vencida não encerrada deve suspender novas aprovações até resolução.

### CQ-03 — Perfil, propriedade e alcance (RNF-02/RNF-08; RF-01/RF-11)

- Fonte e estímulo: aluno tenta aprovar; técnico do laboratório A tenta alterar recurso do B; solicitante troca identificador na URL; usuário inativo reutiliza sessão.
- Ambiente: rotas acessadas diretamente, sem depender dos botões da tela; sessão autenticada quando cabível.
- Artefato: autorização das operações e consultas, inclusive telas administrativas.
- Resposta: negar sem alterar estado, agenda ou evento de sucesso; ocultar dados de terceiros nas consultas. Para recurso fora do alcance, retornar ausência ou negação sem divulgar seu conteúdo.
- Medida: zero gravações e zero exposição de campos pessoais em toda a matriz de ações/perfis/vínculos definida em [02](02-interessados.md); respostas 403/404 conforme política de consulta, ou autenticação exigida para sessão inválida.
- Verificação: cliente HTTP e chamadas das operações com ator explícito; incluir autoaprovação, falsificação de ator no formulário e acesso a histórico alheio. Proteção CSRF deve ser exercitada com sua checagem habilitada.

### CQ-04 — Treinamento ou autorização exigida (RNF-02; RF-12)

- Fonte e estímulo: usuário solicita recurso sem habilitação, com concessão vencida/revogada ou com validade terminando antes do fim da reserva.
- Ambiente: exigência configurada, relógio de teste controlado e demais condições válidas.
- Artefato: política de habilitação, solicitação, aprovação e retirada em E2.
- Resposta: negar a operação inválida, explicar a exigência ao próprio usuário e não criar ocupação. Habilitação válida durante todo o intervalo permite prosseguir para as demais regras.
- Medida: todas as combinações da tabela de casos produzem o resultado previsto, inclusive validade exatamente no fim do período; nenhuma concessão é inferida só pelo perfil administrador.
- Verificação: testes de regra e integração; revogar entre solicitação e aprovação e entre aprovação e retirada. O protocolo para revogação simultânea à decisão deve ser definido na implementação, com nova leitura transacional e teste específico antes do uso operacional.

### CQ-05 — Atomicidade e rastreabilidade (RNF-01/RNF-03)

- Fonte e estímulo: falha forçada após escrever a decisão/ocupação e antes de gravar ou confirmar o evento.
- Ambiente: banco de teste com transação real, sem simular sucesso; operar reserva, manutenção e habilitação.
- Artefato: dados da origem, ocupação, marcadores operacionais e eventos de negócio.
- Resposta: rollback completo; não exibir confirmação de operação incompleta. Em execução sem falha, cada operação principal gera um evento de sucesso correspondente.
- Medida: zero estados parciais em todos os pontos de falha ensaiados; nenhuma senha/segredo nos eventos; repetição não duplica evento de sucesso.
- Verificação: inspecionar tabelas antes/depois e os campos ator, instante, ação, alvo e resultado. A interface comum não permite editar/excluir histórico.

### CQ-06 — Consulta e decisão sob carga (RNF-04)

- Fonte e estímulo: usuários consultam períodos e responsáveis analisam solicitações.
- Ambiente candidato: 50 sessões ativas, 10 requisições/s por 10 minutos, 1.000 recursos e 100.000 registros de agenda; usar banco e host documentados. Distribuição proposta: 90% consultas e 10% decisões, com conflitos deliberados separados dos erros técnicos.
- Artefato: fluxo HTTP, consultas indexadas e transações.
- Resposta: retornar estado correto e resposta compreensível, inclusive para conflitos esperados.
- Medida proposta: p95 até 2 s para consultas e 3 s para decisões; erros técnicos abaixo de 1%, sem violação de invariantes. Registrar também esperas por lock e máximo observado.
- Verificação: ensaio de carga reproduzível após E1; guardar hardware, versões, massa, distribuição e relatório. Números não representam uso estimado da universidade.

### CQ-07 — Recuperação de eventual piloto (RNF-07)

- Fonte e estímulo: falha do host ou perda dos dados locais.
- Ambiente: cópia fora do host disponível e ambiente isolado de restauração.
- Artefato: PostgreSQL, backup e instrução operacional.
- Resposta: restaurar dados e verificar login, reservas, manutenção, eventos e integridade da agenda.
- Medida proposta: ponto recuperado de no máximo 24 h antes da falha e restauração em até 4 h; nenhum conflito introduzido pela recuperação.
- Verificação: exercício cronometrado antes de piloto real, registrando instante da cópia e do restabelecimento. Sem ensaio e infraestrutura definidos, não há garantia de disponibilidade ou recuperação.

### CQ-08 — Uso do fluxo principal (RNF-06)

- Fonte e estímulo: pessoa representativa do público tenta consultar, solicitar e acompanhar uma reserva; responsável tenta analisar.
- Ambiente: navegador em pt-BR, dados fictícios, teclado e tela pequena.
- Artefato: formulários, mensagens e apresentação de estados.
- Resposta: concluir a tarefa e compreender aprovação, pendência e conflito, sem ajuda da equipe.
- Medida proposta: pelo menos 4 de 5 participantes concluem cada tarefa em até 3 minutos; fluxo principal inteiramente acessível por teclado e campos rotulados.
- Verificação: ensaio de tarefas somente após recrutar participantes; até lá, revisão técnica manual. Não foram recrutadas nem avaliadas pessoas nesta fase.

### CQ-09 — Alteração localizada (RNF-05)

- Fonte e estímulo: equipe adiciona uma exigência de habilitação a um recurso existente.
- Ambiente: base modular de E1 e testes de regressão disponíveis.
- Artefato: configuração e política de acesso.
- Resposta: usar a mesma política sem alterar o algoritmo de conflito nem duplicar Reservas por tipo de laboratório.
- Medida: habilitação cadastrável como dado; nenhum novo módulo para um simples código de exigência, nenhum ciclo de dependência e regressão de CQ-01 a CQ-05 aprovada.
- Verificação: revisão de diff e dependências; não usar contagem arbitrária de arquivos como substituto de análise de acoplamento.

### CQ-10 — Custódia e indisponibilidade física (E2; RF-09/RF-10)

- Fonte e estímulo: dois operadores tentam retirar o mesmo equipamento; depois uma nova retirada é tentada com empréstimo anterior em atraso ou manutenção vencida não encerrada.
- Ambiente: reserva aprovada, duas conexões para retirada; relógio controlado para atraso.
- Artefato: Empréstimos, Agenda, marcadores operacionais e Catálogo.
- Resposta: uma única custódia aberta; operação incompatível negada; compromisso futuro existente é sinalizado sob risco, sem cancelamento automático. Devolução continua permitida ao operador autorizado.
- Medida proposta: 100 disputas sem duplicação; zero retirada inválida e zero marcador aberto após uma devolução confirmada; devolução duplicada não altera o registro.
- Verificação: regra, integração e inspeção de estado final, incluindo habilitação revogada após aprovação e condição defeituosa na devolução.

## Riscos e trade-offs

| Risco/compromisso | Efeito | Mitigação e validação |
| --- | --- | --- |
| Fronteiras virarem apenas pastas | Gravações cruzadas contornam regras | Operações explícitas, revisão do grafo e admin sem edição livre; CQ-03/CQ-09 |
| Agenda e origem divergirem, inclusive marcadores | Período liberado ou bloqueado incorretamente | Um commit, correspondência única e testes de rollback; CQ-05 |
| `btree_gist` indisponível no ambiente | Estratégia de exclusão não pode ser instalada | Provar migração em BL-01; rever ADR-002 se houver restrição real |
| Lock por recurso causar espera | Redução de vazão em recurso disputado | Transação curta, ordem de locks e medição; aceitar serialização local para preservar consistência |
| Um host/aplicação/banco falhar | Interrupção geral | Simplicidade operacional aceita para protótipo; backup externo e ensaio antes de piloto |
| PostgreSQL específico | Menor portabilidade | Aceitar em troca de integridade; não prometer substituição transparente por SQLite |
| Stack pouco conhecida pela equipe | Aprendizado compromete entrega | Validar P-01 com pequena prova; não assumir experiência |
| Política incorreta de sala, treinamento ou manutenção | Implementação consistente, mas inadequada ao processo real | Validar P-02 a P-07; registrar alteração de requisito e novos casos |
| Revogação de habilitação e aprovação simultâneas | Janela de autorização desatualizada | Definir ordem de bloqueio de concessões e revalidação em BL-01/BL-04; não depender de cache de sessão |
| Reserva aprovada não refletir condição física | Usuário chega e não pode usar recurso | Marcadores de atraso, bloqueio de retirada e resolução humana; não prometer automação IoT |

## Método de avaliação

Usar revisão técnica guiada por cenários, inspirada em análise de atributos e trade-offs, sem afirmar execução formal de ATAM ou certificação pela norma. Primeiro revisar preocupações e diagramas com a equipe; depois executar a prova de concorrência do ADR-002, os testes de integração de E1 e a demonstração por perfil. Carga e recuperação dependem do ambiente; usabilidade depende de participantes ainda não identificados.

Para cada CQ registrar versão do código, ambiente, dados, procedimento, resultado, evidência e decisão de aceite ou revisão. Manter os resultados separados deste plano, quando existirem. A proposta é aceita para implementação somente após revisar as pendências; a qualidade implementada depende dos ensaios e de suas evidências.
