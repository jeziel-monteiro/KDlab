# 1. Visão geral

Status: proposta inicial. Base confirmada: pedido do projeto e modelo da disciplina. Hipóteses e decisões abertas: [registro central](09-decisoes-e-pendencias.md).

## Problema e objetivo

O KDlab pretende organizar o uso de laboratórios e equipamentos de uma universidade, tornando visíveis os períodos disponíveis e centralizando solicitações, análise, empréstimos e manutenção. O objetivo é evitar compromissos incompatíveis para um mesmo recurso e permitir saber quem autorizou e realizou cada operação.

Não há evidência coletada sobre o processo atual de uma universidade específica. Planilhas, papel, volume de usuários, taxas de conflito e ganhos esperados não são tratados como fatos.

## Objetivos verificáveis

- Consultar disponibilidade por recurso e intervalo, considerando reservas aprovadas e manutenção.
- Registrar solicitações e decisões com estados e responsáveis identificados.
- Impedir que duas aprovações concorrentes ocupem o mesmo recurso no mesmo período.
- Restringir ações por perfil, vínculo com o laboratório e habilitações exigidas.
- Acompanhar retirada, devolução e manutenção sem apagar o histórico.

Os [requisitos](03-requisitos.md) detalham comportamento; os [cenários de qualidade](07-avaliacao.md) propõem como avaliá-lo.

## Escopo do produto

| Capacidade confirmada no pedido | Incremento proposto |
| --- | --- |
| Cadastro de laboratórios e equipamentos | E1 |
| Consulta de disponibilidade por período | E1 |
| Solicitação, aprovação, rejeição e cancelamento de reservas | E1 |
| Manutenção e bloqueio de recursos | E1, com registro e bloqueio temporal básicos |
| Acesso por perfil e exigência de treinamento/autorização | E1, com habilitação registrada manualmente |
| Histórico de operações principais | E1 e ampliado a cada fluxo posterior |
| Retirada e devolução de equipamentos | E2 |

**E1** é a primeira entrega funcional proposta: um solicitante consulta e solicita, um responsável analisa, e a agenda permanece consistente. Ela serve à demonstração acadêmica e precisa de validação antes de uso operacional. **E2** completa o controle básico de empréstimos; E1 não deve ser apresentado como sistema completo de empréstimos.

Fora do escopo inicial confirmado: pagamentos, compras, gestão financeira, sensores IoT e integração com sistemas institucionais. Também não se propõem neste momento reservas recorrentes, listas de espera, reserva de kits ou gestão de cursos de treinamento; essas últimas exclusões são hipóteses de redução de escopo, sujeitas a revisão.

## Limites de contexto propostos

Uma instituição por instalação, múltiplos laboratórios e recursos identificáveis individualmente. Um laboratório pode ser um recurso reservável integralmente; cada equipamento é uma unidade reservável. A relação de localização não gera bloqueios automáticos entre laboratório e equipamentos. Esse recorte precisa de validação (H-01 e H-02).

A primeira versão usa contas locais provisionadas por administrador. A disponibilidade é consultada por pessoas autenticadas, sem divulgar dados pessoais de outros solicitantes. Não se pressupõem SSO, e-mail transacional ou automação externa.

## Vocabulário

| Termo | Significado inicial |
| --- | --- |
| Recurso | Unidade reservável exclusiva: laboratório inteiro ou equipamento individual |
| Laboratório | Espaço físico e unidade de responsabilidade; pode também ser reservado como recurso |
| Disponibilidade | Ausência de ocupação conflitante e impedimento operacional conhecido, com recurso ativo; não garante aprovação futura |
| Reserva | Solicitação e sua decisão para um único recurso e intervalo |
| Ocupação | Registro da agenda que bloqueia um intervalo por reserva aprovada ou manutenção |
| Empréstimo | Registro da custódia física de equipamento, vinculado a reserva aprovada |
| Manutenção | Registro de intervenção e do período de indisponibilidade do recurso |
| Habilitação | Evidência administrativa de autorização ou treinamento, com tipo, validade e concedente |
| Responsável | Técnico ou gestor vinculado aos laboratórios sobre os quais pode operar |
| Histórico | Eventos de negócio com ator, instante, ação, alvo e resultado; distinto de logs técnicos |

## Restrições e situação atual

A equipe acadêmica é pequena, mas seu tamanho, experiência, prazo e orçamento não foram informados. A proposta favorece ferramentas com recursos integrados e uma implantação simples. Não se assume infraestrutura universitária já disponível.

Na inspeção havia apenas o PDF em `docs/`, sem aplicação, stack, README ou `.gitignore`. Não foram encontrados arquivos AGENTS.md no projeto ou nos ancestrais inspecionados; aplicam-se as instruções fornecidas na conversa. Os diretórios locais foram preservados. Na ocasião, a raiz Git efetiva era a pasta pai, sem commits e com conteúdo de outros projetos. Posteriormente, a publicação solicitada em 14/11/2026 motivou a criação de um Git independente para KDlab, sem alterar o índice da pasta pai; ver P-12 no registro de decisões.
