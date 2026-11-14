# 8. Backlog inicial priorizado

Status: BL-01 tem [recorte técnico concluído](11-prova-consistencia-agenda.md), com validações institucionais pendentes. **BL-02 foi implementado**, com 26 testes, migrações e inicialização HTTP verificados; revisão visual pendente por indisponibilidade do navegador. Ver [relatório BL-02](12-base-identidade.md). BL-03 em diante permanecem planejados, sem estimativas de prazo ou atribuição de integrantes.

## Meta da primeira entrega funcional — E1

Com contas de demonstração e dados fictícios, um solicitante deve consultar e solicitar um recurso; outro usuário elegível deve aprovar/rejeitar; cancelamento e manutenção devem alterar a disponibilidade corretamente. Treinamento e alcance por laboratório devem ser respeitados e as decisões devem aparecer no histórico. Retirada e devolução são E2.

| Ordem / ID | Item e dependências | Critérios de aceitação | Rastreabilidade |
| --- | --- | --- | --- |
| 1 / BL-01 | Confirmar recorte técnico e provar a agenda concorrente; antecede desenvolvimento dos fluxos | Registrar decisão sobre P-01/P-02/P-06; executar prova descartável com duas ou mais conexões PostgreSQL; demonstrar migração `btree_gist`, exclusão entre reserva/manutenção, adjacência e rollback; conferir marcador de manutenção vencida; registrar decisões nos ADRs e receita de ambiente | ADR-001/002, RNF-01, CQ-01/CQ-02/CQ-05 |
| 2 / BL-02 | Criar base executável e identidade; depende de BL-01 | Aplicação inicia por instrução reproduzível com dependências fixadas e banco de teste separado; administrador provisiona conta; login/logout funcionam; conta inativa e sessão inválida não operam; segredos ficam fora do Git; runner de testes executa | RF-01/RF-11, RNF-08 |
| 3 / BL-03 | Catálogo e vínculos de responsabilidade; depende de BL-02 | Administrador cadastra laboratório e equipamento com identificador único; define vínculo de técnico; usuário consulta sem poder alterar; técnico sem vínculo não modifica recursos alheios; inativação não apaga histórico e é recusada enquanto houver compromissos futuros não resolvidos; cadastros geram eventos mínimos | RF-02/RF-11/RF-13, RN-10, CQ-03/CQ-05 |
| 4 / BL-04 | Política de habilitação e escopo; depende de BL-03 | Administrador registra exigência e concessão com tipo/validade/concedente; ausência, expiração e revogação negam operação; validade cobre o período completo; perfil elevado não ignora exigência; definir e testar protocolo de revogação concorrente à aprovação; alterações ficam no histórico | RF-12, RNF-02, CQ-03/CQ-04 |
| 5 / BL-05 | Agenda e consulta de disponibilidade; depende de BL-03/BL-04 | Usuário informa início/fim; intervalo vazio/invertido é recusado; recurso inativo ou bloqueado é indicado; adjacentes são aceitos e sobrepostos negados; fuso aparece na tela; não exibir nomes de outros solicitantes; informar que consulta não garante vaga | RF-03, RN-01 a RN-05 |
| 6 / BL-06 | Solicitação e acompanhamento; depende de BL-05 | Solicitante cria reserva PENDENTE para um recurso e período elegíveis; conflito conhecido e falta de habilitação são recusados; duas pendências podem coexistir; usuário acompanha apenas suas solicitações; operador consulta apenas seu alcance; pendência não ocupa a agenda | RF-04/RF-07, CQ-03/CQ-04 |
| 7 / BL-07 | Aprovação/rejeição e histórico das decisões; depende de BL-06 | Operador elegível aprova ou rejeita pendência; não aprova a própria; motivo é exigido na rejeição; revalidar estado, habilitação, recurso e agenda; exatamente uma aprovação vence a disputa pelo mesmo período; perdedor permanece PENDENTE; repetição não duplica ocupação/evento; falha reverte origem, agenda e histórico | RF-05/RF-13, CQ-01/CQ-04/CQ-05 |
| 8 / BL-08 | Cancelamento e transições; depende de BL-07 | Cancelamento próprio e por operador respeita a tabela de estados; requer motivo; libera ocupação atomicamente; estado terminal não reabre; alteração de recurso/período exige nova solicitação; disputa aprovação/cancelamento termina em estado e agenda coerentes | RF-06, RN-07/RN-08, CQ-05 |
| 9 / BL-09 | Manutenção e bloqueio temporal; depende de BL-07/BL-08 | Responsável vinculado registra bloqueio com motivo e período; consulta e aprovação respeitam bloqueio; conflito com reserva já aprovada recusa manutenção sem cancelar reserva silenciosamente; disputa concorrente confirma só um lado; cancelamento pré-início e encerramento válido atualizam agenda e histórico; prazo vencido sem encerramento suspende novas aprovações e é visível | RF-08/RF-13, RN-02/RN-09, CQ-02/CQ-05 |
| 10 / BL-10 | Consolidar entrega e evidências; depende de BL-02 a BL-09 | Executar roteiro por perfil com dados fictícios de informática, audiovisual e habilitação; passar CQ-01 a CQ-05 e revisão de CQ-09; revisar pt-BR, teclado, mensagens e estados; documentar instalação, testes e limitações; alinhar requisitos/diagramas/ADRs ao código efetivo | RNF-01 a RNF-06/RNF-08, roteiro acadêmico |

Histórico e autorização são transversais desde BL-02/BL-03; BL-07 não é autorização para acrescentá-los somente ao final. O bloqueio temporal de manutenção participa da prova inicial, mesmo que sua tela completa venha em BL-09.

Em BL-02, a stack candidata foi adotada provisoriamente para desenvolvimento local, conforme a continuação solicitada. O provisionamento usa superusuário técnico, e o histórico cobre alterações de contas pelo painel. Isso não encerra P-01 nem implementa os perfis/vínculos de domínio de BL-03/BL-04. A próxima implementação é BL-03.

## Critério de conclusão de E1

Uma demonstração deve mostrar: usuário solicita, responsável aprova, outro pedido conflitante não aprova, manutenção impede o período, cancelamento libera, pessoa sem autorização não altera nada e histórico explica a decisão. O banco não pode conter ocupações bloqueantes conflitantes. Manter evidências dos cenários e instruções reproduzíveis.

Não apresentar metas RNF-04/RNF-07 como cumpridas sem ensaio. Antes de uso real, concluir também avaliação de carga, recuperação e políticas de dados, além da validação do processo com responsáveis. Esses pontos não impedem organizar E1 como entrega acadêmica.

## Continuação do escopo — E2 e avaliação para piloto

| Ordem / ID | Item | Critérios de aceitação |
| --- | --- | --- |
| 11 / BL-11 | Retirada de equipamento | Reserva aprovada elegível; recebedor e operador identificados; uma única custódia aberta por equipamento e uma por reserva; revalidar habilitação, período e manutenção; evento e marcador confirmam juntos; CQ-10 |
| 12 / BL-12 | Devolução e atraso | Registrar instante e condição; manter custódia aberta até devolução real; atraso visível; devolver duas vezes não duplica movimentação; cancelar reserva com custódia aberta é negado; defeito encaminha para manutenção com resolução explícita dos compromissos |
| 13 / BL-13 | Ensaio de carga e ajuste de consultas | Ambiente e massa registrados; executar CQ-06 e comparar metas propostas; revisar índices/locks somente segundo evidência |
| 14 / BL-14 | Preparação de eventual piloto | Definir operação, privacidade, backup e restauração; executar CQ-07; recrutar avaliação CQ-08 se autorizado; confirmar responsáveis, regras e aceite antes de uso operacional |

Kits, capacidade compartilhada, cursos, integrações, notificações e recorrência não entram automaticamente nesse backlog de implementação. Dependem de novos requisitos e priorização.
