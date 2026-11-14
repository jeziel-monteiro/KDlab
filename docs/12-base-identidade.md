# 12. BL-02 — Base executável e identidade

Data: 14/11/2026. Status: **implementado e verificado no recorte de BL-02**. O KDlab agora possui uma aplicação Django executável com contas locais, login/logout, página de conta e provisionamento administrativo. A entrega E1 completa permanece em desenvolvimento; catálogo e reservas ainda não são funcionalidades da aplicação.

## Comportamento disponível

| Caminho | Comportamento |
| --- | --- |
| `/` | Página da própria conta; requer usuário ativo autenticado |
| `/conta/entrar/` | Formulário em pt-BR, sessão Django e CSRF; credenciais inválidas/inatividade recebem mensagem genérica |
| `/conta/sair/` | Logout somente por POST com CSRF; invalida a sessão |
| `/admin/` | Painel técnico restrito a superusuário ativo com acesso administrativo |
| Usuários no painel | Criar conta, editar dados, inativar e alterar credenciais; exclusão de usuários desabilitada |
| Eventos no painel | Consulta de histórico por superusuário; sem criação, edição ou exclusão pela interface |

Um usuário comum vê somente sua identificação. Não existe cadastro público, recuperação por e-mail ou tela de reserva nesta etapa. Perfis de aluno/professor/técnico/administrador e vínculos por laboratório continuam em BL-03/BL-04. Grupos e permissões técnicos do Django não comprovam implementação desses papéis do produto.

A inativação de uma conta impede novo login e bloqueia a sessão existente na próxima requisição. A página autenticada utiliza controle de cache para evitar que seus dados sejam armazenados como conteúdo público. O redirecionamento `next` só aceita destinos autorizados pelo mecanismo do Django.

## Organização implementada

| Caminho | Responsabilidade |
| --- | --- |
| `manage.py` e `kdlab/` | Entrada, configuração, rotas, WSGI e administração técnica |
| `apps/identidade/` | Usuário baseado em `AbstractUser`, formulários, views e administração de contas |
| `apps/historico/` | Eventos mínimos de negócio e consulta administrativa somente de leitura |
| `templates/` e `static/` | Apresentação HTML/CSS em pt-BR, sem dependências de frontend ou recursos externos |
| `scripts/criar_env.py` | Configuração local com segredos aleatórios e permissão 0600; preserva arquivo existente |
| `scripts/testar.py` | Validação com PostgreSQL privado, sem usar o banco de desenvolvimento configurado |
| `compose.yaml` | PostgreSQL local opcional para desenvolvimento com dados persistentes |

Os modelos da prova BL-01 não foram copiados para os módulos reais. O experimento e sua evidência permanecem em `experimentos/agenda/`.

## Identidade e histórico

A criação, edição e troca de credenciais pelo painel registram evento com identificador do ator, ação, alvo, instante e resultado. Apenas nomes de campos permitidos são registrados; senhas, hashes e valores pessoais alterados não são copiados para o evento. A troca da própria senha pelo administrador também participa desse fluxo.

Gravação da conta e evento pertencem à mesma transação. Os testes forçam falha do histórico e confirmam rollback da criação e das mudanças de senha. O histórico usa identificadores, sem importar o modelo de usuário, mantendo a dependência Identidade → Histórico.

O primeiro superusuário é criado pelo comando técnico `createsuperuser`, antes do provisionamento pelo painel. Essa operação de bootstrap e alterações diretas por shell/ORM não geram os eventos de negócio desta etapa; são acesso técnico privilegiado, fora do fluxo administrativo implementado. Não há alegação de auditoria inviolável ou completa de todas as operações possíveis no banco.

Decisão e alternativas: [ADR-003](decisoes/ADR-003-identidade-e-historico.md).

## Instalação e execução

A receita está no [README principal](../README.md). A configuração usa variáveis de ambiente; o Django não carrega `.env` automaticamente. O arquivo precisa ser exportado no shell conforme as instruções. Ausência de `DJANGO_SECRET_KEY` impede a inicialização. O arquivo gerado não é versionado.

A base foi executada com Python 3.14.4, Django 5.2.19, psycopg 3.3.9 e PostgreSQL 17.11. As dependências estão fixadas em [requirements.txt](../requirements.txt). Python 3.13 permanece compatível segundo o framework, mas não foi ensaiado neste ambiente.

Em desenvolvimento, `DJANGO_DEBUG=1` permite HTTP em loopback. Fora desse modo, cookies seguros e redirecionamento HTTPS ficam habilitados. Isso não constitui configuração completa nem implantação de produção.

## Verificação realizada

O comando abaixo cria um PostgreSQL exclusivo sem rede ou portas publicadas, aplica/verifica migrações, confere configuração, coleta estáticos em pasta temporária e roda a suíte em `test_kdlab`. O container é removido ao terminar.

```bash
.venv/bin/python scripts/testar.py
```

Na máquina de execução, utilizou-se a imagem PostgreSQL 17 já disponível:

```bash
python scripts/testar.py --imagem public.ecr.aws/supabase/postgres:17.11.0.006
```

Resultado: **26 testes passaram**. A saída completa é mantida localmente em `docs/evidencias/bl02-2026-11-14.txt`, fora do versionamento. O script e o código dos testes permitem repetir a execução.

| Verificação | Resultado |
| --- | --- |
| Migrações | Sem divergência entre modelos e arquivos; aplicação das migrações desde banco vazio concluída |
| Configuração e arquivos estáticos | `check` sem problemas e `collectstatic` concluído |
| Sessão | Login correto, logout, cookie inválido e identificador de usuário inexistente cobertos |
| Conta inativa | Login recusado e sessão anterior bloqueada na requisição seguinte |
| CSRF | POST sem token recusado no login/logout; token válido permite o fluxo |
| Redirecionamento e HTML | `next` externo recusado; destino local preservado; nome pessoal escapado no HTML |
| Provisionamento | Superusuário cria conta com senha processada pelo framework; usuário comum/staff não obtém esse acesso |
| Histórico | Eventos administrativos com ator; sem senha/hash; interface somente de leitura |
| Atomicidade | Falha de histórico reverte criação, troca de senha de terceiro e troca de senha própria |

O módulo `kdlab.settings_test` utiliza hash rápido exclusivamente para os testes. A aplicação normal mantém os hashers padrão do Django. O tempo de execução da suíte não é evidência de desempenho da autenticação em produção.

Uma verificação adicional iniciou o `runserver` real em loopback, aplicou migrações no banco descartável, executou `createsuperuser` com senha aleatória em memória e confirmou respostas HTTP: entrada 200 com CSRF, início protegido redirecionado, CSS 200 e login administrativo 200. O servidor foi encerrado ao final. O registro bruto é mantido localmente em `docs/evidencias/bl02-inicializacao-2026-11-14.txt`, fora do versionamento.

Também se verificou, em diretório temporário, que o gerador de configuração cria `.env` com modo 0600 e não sobrescreve um arquivo existente. A configuração do Compose foi validada sem iniciar serviços persistentes.

## Limites de verificação e continuidade

O acesso ao navegador retornou `The browser access host is unavailable`. Portanto, a revisão visual e a navegação manual em desktop/mobile não foram concluídas. Os testes HTTP validam comportamento e HTML; não comprovam renderização, usabilidade ou acessibilidade integral. O CSS contém adaptação para telas menores e estados de foco, ainda sujeitos à revisão visual.

Os cenários CQ-03/CQ-05 têm evidência parcial para identidade; autorização por laboratório, habilitações e reservas seguem pendentes. A experiência da equipe e as regras institucionais continuam sem validação. A adoção da stack nesta base é uma decisão técnica provisória para avançar o desenvolvimento local.

Próximo incremento: **BL-03, catálogo de laboratórios/equipamentos e vínculos de responsabilidade**, mantendo H-01/H-02 explícitas até revisão com os responsáveis. A revisão visual pendente pode ser feita quando a conexão do navegador estiver disponível.
