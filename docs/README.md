# Documentação do KDlab

Versão 0.3.1 — 14/11/2026. Os documentos continuam em revisão e não houve validação com usuários. Há uma prova técnica isolada da agenda e uma base executável de identidade, com testes registrados. A entrega funcional E1 completa ainda não foi concluída.

O roteiro fornecido pela disciplina é a referência principal da organização acadêmica. Trata-se de material para consulta local, não distribuído neste repositório. Os campos de exemplo desse material não identificam integrantes, cliente ou histórico do KDlab. O arquivo de referência e os logs brutos de execução são mantidos localmente e ignorados pelo Git.

## Leitura e situação das informações

1. [Visão geral](01-visao-geral.md).
2. [Interessados e preocupações](02-interessados.md).
3. [Requisitos, regras e estados](03-requisitos.md).
4. [Arquitetura, alternativas e stack](04-arquitetura.md).
5. [Visões arquiteturais e correspondências](05-visoes.md).
6. [Domínio, variabilidade e reutilização](06-dominio-variabilidade.md).
7. [Avaliação proposta](07-avaliacao.md).
8. [Backlog priorizado](08-backlog.md).
9. [Informações confirmadas, hipóteses e pendências](09-decisoes-e-pendencias.md).
10. [Referências](10-referencias.md).
11. [Prova de consistência da agenda e evidências](11-prova-consistencia-agenda.md).
12. [Base executável, identidade e evidências](12-base-identidade.md).

**Confirmado** significa informado no pedido ou observado nos arquivos, sem implicar pesquisa de campo. **Hipótese** é uma regra provisória para permitir o planejamento. **Decisão proposta** é uma recomendação técnica ainda não aprovada pela equipe. **Pendente** identifica o que precisa de definição e quem pode validá-lo, sem atribuir responsáveis nominais.

Os códigos RF, RNF, RN, CQ e BL identificam requisitos funcionais, não funcionais, regras de negócio, cenários de qualidade e itens de backlog. F, H e P identificam fatos, hipóteses e pendências no documento 09. O [ADR-001](decisoes/ADR-001-monolito-modular.md) está em adoção incremental; o [ADR-002](decisoes/ADR-002-consistencia-da-agenda.md) continua proposto para os módulos de reservas/manutenção. O [ADR-003](decisoes/ADR-003-identidade-e-historico.md) registra a identidade implementada para desenvolvimento local, com validação institucional pendente.

## Correspondência com o roteiro da disciplina

| Seção do PDF | Documento e cobertura inicial |
| --- | --- |
| Ficha técnica e registro de alterações | Versão e data neste índice; integrantes ainda não informados; nenhum histórico de exemplo foi copiado |
| 1.1–1.3: descrição, objetivos e escopo | [01](01-visao-geral.md) |
| 1.4 e 5.1–5.4: domínio/linha de produtos, comuns, variáveis, reutilização e representação | [06](06-dominio-variabilidade.md), inclusive diagrama |
| 2.1–2.2: interessados e preocupações | [02](02-interessados.md) |
| 2.3: requisitos e restrições | [03](03-requisitos.md) |
| 3.1–3.5: estilo, padrões, justificativas e alternativas | [04](04-arquitetura.md) e ADRs |
| 4.1–4.4: módulos, componentes/conectores, implantação e relação | [05](05-visoes.md) |
| 6.1–6.5: atributos, cenários, riscos, trade-offs e método | [07](07-avaliacao.md); evidências por recorte em [11](11-prova-consistencia-agenda.md) e [12](12-base-identidade.md) |
| 8: referências | [10](10-referencias.md) |

A numeração 8 para referências pertence ao PDF, que não apresenta seção 7. Os números dos arquivos servem à navegação e não renumeram o roteiro. A distribuição em vários arquivos não implica uma declaração de conformidade com a ISO/IEC/IEEE 42010; o texto integral da norma não foi consultado.

## Manutenção da documentação

Ao alterar uma regra, revisar seus RF/RN, estados, diagramas, cenários CQ e critérios BL relacionados. Uma proposta aceita deve receber registro de aprovação e justificativa no ADR correspondente. Metas de desempenho, recuperação e usabilidade permanecem propostas até avaliação em ambiente definido.

| Versão | Data | Mudança |
| --- | --- | --- |
| 0.1 | 13/11/2026 | Organização inicial a partir do pedido e do modelo local; sem resultados de implementação |
| 0.2 | 14/11/2026 | Prova isolada de BL-01 com PostgreSQL e migrações Django; evidência técnica registrada, sem validação do processo institucional |
| 0.3 | 14/11/2026 | BL-02: aplicação, identidade, histórico administrativo e 26 testes; verificação HTTP concluída e revisão visual pendente |
| 0.3.1 | 14/11/2026 | Git independente para KDlab e remoto GitHub definido, preservando o repositório da pasta pai |
