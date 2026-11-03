# Verificações realizadas

Autor: George Pagliuso. Cada item diz o que foi **executado**, o resultado e o que ficou **não verificado**. Nada aqui é plano: o que não rodou está na última seção.

## 1. Passou

| Verificação | Como foi feita | Resultado |
| --- | --- | --- |
| Testes automatizados | `python -m pytest -q` (Python 3.13, pandas 3.0.5) | 40 testes passando |
| Outras versões do pandas | mesma suíte em ambientes virtuais com pandas 2.2.3 e 3.1.0 | 39 passam, 1 pulado (teste de `.xlsx`, sem `openpyxl` nesses ambientes) |
| Resultados esperados do recorte, calculados à parte | `tests/fixtures/conferencia_sqlite.py` (SQL em sqlite3, sem o script e sem pandas) comparado com a skill | Pedidos por mês 5, 7 e 5 (e 0 em dezembro/2017 e fevereiro/2018); ranking SP 9, MG 3 e empate de uma unidade nas demais; ticket médio do recorte, de janeiro/2018 e de janeiro/2018 em SP iguais aos do SQL (diferença menor que meio centavo, por arredondamento da saída) |
| Regras testadas de verdade | Mutação manual: contar `shipped` como entregue, denominador só com pedidos com itens, data final exclusiva, não remover pedidos repetidos | Os 4 defeitos fizeram testes falharem. Uma quinta mudança (contar linhas em vez de pedidos distintos no ranking) não falhou, e é equivalente porque os pedidos já estão distintos nesse ponto |
| Dados completos contra SQL independente | `tests/conferencia_independente.py` sobre os mesmos arquivos | Meses, ranking de UFs, soma de preços e ticket médio idênticos nos casos: toda a base, 2017, jan a jun de 2018 (UFs) e SP em jan a mar de 2018 |
| Leitura de `.xlsx` | Ticket médio de SP em jan a mar de 2018 lido direto dos `.xlsx` recebidos | Mesmo resultado que com CSV (8.578 pedidos, 9.816 itens, soma 1.053.156,63, ticket 122,77); cerca de 40 s |
| Período sem dados | jan a mar de 2019 | Contagens zero (meses listados com 0), ranking vazio, ticket "não aplicável" |
| UF inexistente | `--uf XX` | Zero pedidos, ticket "não aplicável" e aviso com as UFs existentes |
| Entradas inválidas | data 2018-02-31, pasta inexistente, pasta não informada, datas invertidas, arquivo e coluna ausentes | Mensagem de erro em português e código de saída 2 |
| Estrutura do `SKILL.md` | Script de checagem: YAML, nome igual à pasta, caminhos existentes, sem campos do template | Passou |
| Skill no Claude Code (modo headless, na raiz do repositório) | Transcrições em `docs/testes-com-agente/` | Ver tabela abaixo |

### Testes da skill executados no Claude Code

| Arquivo | Pedido | O que se observou |
| --- | --- | --- |
| `T1_ativacao_explicita` | `/analise-olist` + pedidos por mês, jan a mar de 2018 | Leu `regras-e-metricas.md`, rodou `inspecionar` e `pedidos-por-mes`; respondeu com métrica, filtros, arquivo, comando, cobertura e limitações |
| `T2_continuacao_so_SP` | "Agora só para clientes de SP" (mesma sessão) | Repetiu a execução com `--uf SP`, explicou que só a UF mudou; percentuais calculados por código |
| `T3_selecao_automatica_top_ufs` | Pergunta sem `/` sobre as cinco UFs | A skill foi escolhida sozinha (ferramenta Skill), rodou `top-ufs` |
| `T4_periodo_sem_dados` | Ticket médio de 2019 | Ticket "não aplicável" (não zero), explicou que a base vai de 2016-09 a 2018-08 |
| `T5_pergunta_sem_resposta_na_base` | Margem de lucro por categoria | Consultou `inspecionar` e `limites-da-base.md`, recusou sem inventar número, explicou que falta custo e ofereceu perguntas respondíveis |
| `T6_entrada_ausente` | "Ticket médio de ontem" sem informar a pasta | Escolheu a skill e perguntou onde estão os dados e o que "ontem" significa, sem executar com palpite |
| `T7_fora_do_escopo_dashboard` | Dashboard e previsão de vendas | A skill **não** foi escolhida (comportamento esperado para o escopo) |
| `T8_nao_relacionado` | O que é regressão linear | Nenhuma ferramenta, skill não escolhida |

## 2. Falhou (e o que foi feito)

| O que falhou | Causa | Correção |
| --- | --- | --- |
| `T5a_sem_ativacao_antes_de_ajustar_a_description`: para a pergunta de margem de lucro, a skill não foi escolhida e o agente respondeu com conhecimento público do Olist, oferecendo uma margem "estimada" | A `description` falava em pedidos, vendas e clientes, mas não em perguntas que talvez a base não suporte | `description` ampliada; o teste foi repetido (`T5`) e passou |
| `T0_impedimento_de_permissao`: execução bloqueada | A sessão de teste só permitia alguns comandos e o agente encadeou `ls; python`. Não foi defeito da skill: o agente explicou o impedimento e não inventou números | Teste repetido com a permissão de Bash liberada na caixa de testes (`T1`) |
| Cálculo de percentual feito "de cabeça" em uma versão anterior do `SKILL.md` | Faltava a regra sobre números derivados | Regra acrescentada: percentuais e diferenças também devem sair de código |
| 7 células de `freight_value` do recorte e cerca de 170 de `price` nos dados completos viraram datas | Conversão das planilhas do Google | Não corrigível; o script ignora e avisa (ver README) |

## 3. Não verificado

- Uso no **Codex** (`$analise-olist`, pasta `.agents/skills/`): nada foi executado lá.
- Execução no **Windows**: os testes e as saídas foram feitos em Linux.
- Resultados com os **CSVs originais** do Olist: os arquivos recebidos têm células corrompidas em `price`, então o ticket médio pode diferir. As contagens de pedidos não dependem dessas colunas.
- O **dicionário oficial** (`dicionario.xlsx`): não estava disponível. A correspondência de nomes foi confirmada pelo usuário.
- Pedidos entregues **sem itens**, datas inválidas, ids repetidos e clientes sem correspondência só foram testados com dados sintéticos; a base real não tem esses casos entre os pedidos entregues.
- O **print** do copiloto na sessão do usuário: ainda será tirado por ele (ver `docs/roteiro-do-print.md`).
