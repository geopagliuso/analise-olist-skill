# analise-olist: skill de copiloto de analytics para a base Olist

**Autor:** George Pagliuso · Disciplina: IA Generativa na Prática · Lista 03

Skill para o Claude Code que transforma perguntas em linguagem natural sobre pedidos, vendas e clientes do marketplace Olist em análises **executadas por código**, com resposta verificável: métrica, filtros, arquivos usados, código executado, resultado, cobertura e limitações.

A skill fica em [`.claude/skills/analise-olist/`](.claude/skills/analise-olist/SKILL.md).

## O que a skill responde

| Pergunta | Comando do script |
| --- | --- |
| Quantos pedidos entregues foram realizados em cada mês? | `pedidos-por-mes` |
| Quais são as cinco UFs dos clientes com mais pedidos entregues? | `top-ufs` |
| Qual foi o ticket médio do preço dos itens por pedido entregue, sem frete? | `ticket-medio` |

Em qualquer uma, o usuário pode pedir na conversa uma mudança de **período** (datas inicial e final), de **UF** ou do tamanho do **ranking**; o agente interpreta, executa o código de novo e explica o novo resultado.

## Estrutura

```
.claude/skills/analise-olist/
  SKILL.md                         procedimento do agente (11 seções do template, adaptado ao Olist)
  references/regras-e-metricas.md  regras de negócio, métricas, chaves, tratamento de dados ruins
  references/limites-da-base.md    o que a base permite e não permite responder
  scripts/olist_analytics.py       código reutilizável das análises
tests/                             testes (pytest), recorte real do Olist e conferência independente em SQL
saidas/                            saídas das análises executadas nos dados completos
docs/verificacoes.md               o que passou, falhou e não foi verificado
docs/roteiro-do-print.md           passo a passo do print do copiloto em uso
docs/testes-com-agente/            transcrições dos testes da skill executados no Claude Code
requirements.txt                   dependências
```

## Entendimento do problema e decisões

Seguindo o `brainstorm.md` da aula, o que ficou definido (e por quem):

| Decisão | Origem |
| --- | --- |
| Tarefa: copiloto de analytics para a equipe de um marketplace, em conversa, com código executado e resposta verificável. | Enunciado da lista |
| Pedido entregue = `descSituacao` igual a `delivered`; data de referência = `dtPedido`; contar `idPedido` distintos. | Enunciado |
| Ranking de UFs: ligar pedido e cliente por `idCliente` e usar `descUF`. | Enunciado |
| Ticket médio = soma de `vlPreco` dos itens ÷ nº de pedidos distintos selecionados, sem `vlFrete`. | Enunciado |
| Correspondência dos nomes da lista com as colunas dos arquivos (`idPedido` = `order_id`, `dtPedido` = `order_purchase_timestamp`, `vlPreco` = `price`, `descUF` = `customer_state` etc.). | **Proposta minha, confirmada por George.** O `dicionario.xlsx` não estava disponível. |
| Datas inicial e final **inclusivas**, por dia do calendário (hora ignorada). | Proposta minha, confirmada por George. |
| Ranking de cinco UFs por padrão; sem período, toda a base; desempate pela ordem alfabética da UF. | Proposta minha, usada como padrão e informada na resposta. |
| Pedidos entregues sem itens permanecem no denominador do ticket; a cobertura é informada. | Enunciado ("dividida pelo número de pedidos distintos selecionados" e "explique a cobertura"). |
| Dados inválidos (data do pedido, preço) são tratados como ausentes e avisados; nada é "corrigido" em silêncio. | Proposta minha (ver `references/regras-e-metricas.md`). |
| Repositório próprio; dados completos **fora** do repositório (`--dados` ou `OLIST_DATA_DIR`). | Confirmada por George. |
| Print do copiloto em uso tirado por George na própria sessão. | Confirmada por George. |

## Como usar

1. Instale as dependências (Python 3; testado com 3.13, pandas 2.2.3, 3.0.5 e 3.1.0):
   ```
   pip install -r requirements.txt
   ```
2. Coloque os arquivos do Olist numa pasta **fora** do repositório. Os nomes esperados são `olist_orders_dataset`, `olist_order_items_dataset` e `olist_customers_dataset`, em `.csv` ou `.xlsx` (o script procura o `.csv` primeiro).
3. Informe a pasta de uma destas formas:
   - na conversa: "Os dados estão em C:\\caminho\\da\\pasta" (o agente passa `--dados`);
   - variável de ambiente `OLIST_DATA_DIR` (PowerShell: `$env:OLIST_DATA_DIR = "C:\caminho\da\pasta"`; Linux/macOS: `export OLIST_DATA_DIR=/caminho/da/pasta`).
4. Abra o Claude Code na raiz deste repositório e peça, por exemplo:
   ```
   /analise-olist Quantos pedidos entregues foram feitos em cada mês?
   ```
   A skill também é escolhida automaticamente quando a pergunta é sobre o Olist.
5. Para rodar o código sem o agente, por exemplo:
   ```
   python .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados <pasta> --inicio 2018-01 --fim 2018-03 --uf SP
   ```
   Opções: `--inicio` e `--fim` (`AAAA-MM-DD` ou `AAAA-MM`), `--uf`, `--top`, `--json`, `--saida <pasta>` (grava `.json` e `.csv`, nunca dentro da pasta dos dados), `--sobrescrever`. O comando `inspecionar` lista os arquivos e colunas da pasta.
6. Para conferir o código: `python -m pytest -q`.

Ler os arquivos `.xlsx` diretamente funciona, mas leva cerca de 40 segundos por execução; com `.csv` é bem mais rápido.

## Resultados obtidos nos dados completos

Todos os números abaixo vieram de execuções do script (saídas completas em [`saidas/`](saidas/)) e foram conferidos por uma segunda implementação em SQL (`tests/conferencia_independente.py`). Fonte: os arquivos do Olist recebidos (ver o alerta sobre qualidade dos dados abaixo).

| Análise | Resultado | Saída |
| --- | --- | --- |
| Pedidos entregues por mês (toda a base) | 96.478 pedidos entregues, de 2016-09 a 2018-08; 2017-11 é o mês de pico (7.289) | [`01`](saidas/01_pedidos_por_mes.md) |
| Cinco UFs com mais pedidos entregues | SP 40.501 · RJ 12.350 · MG 11.354 · RS 5.345 · PR 4.923 | [`02`](saidas/02_top_ufs.md) |
| Ticket médio sem frete (toda a base) | 136,94 (soma de vlPreco 13.211.395,96 ÷ 96.478 pedidos); 168 itens com preço inválido ignorados | [`03`](saidas/03_ticket_medio.md) |
| Continuação: pedidos por mês em 2017 | 43.428 pedidos em 12 meses | [`04`](saidas/04_continuacao_pedidos_2017.md) |
| Continuação: ranking de UFs, jan a jun de 2018 | SP 17.456 · RJ 4.923 · MG 4.735 · RS 2.136 · PR 2.070 | [`05`](saidas/05_continuacao_top_ufs_2018_S1.md) |
| Continuação: ticket médio, UF SP, jan a mar de 2018 | 122,77 (8.578 pedidos; 15 itens com preço inválido ignorados) | [`06`](saidas/06_continuacao_ticket_sp_2018_T1.md) |
| Período sem dados (jan a mar de 2019) | contagens = 0; ticket médio = não aplicável | [`07`](saidas/07_periodo_sem_dados_pedidos.md), [`08`](saidas/08_periodo_sem_dados_ufs.md), [`09`](saidas/09_periodo_sem_dados_ticket.md) |
| UF inexistente (XX) | 0 pedidos, ticket não aplicável, aviso com as 27 UFs existentes | [`10`](saidas/10_uf_inexistente.md) |
| Entradas inválidas (data impossível, pasta inexistente) | erro explicado, código de saída 2 | [`11`](saidas/11_erro_data_impossivel.md), [`12`](saidas/12_erro_pasta_inexistente.md) |

### Alerta sobre a qualidade dos arquivos recebidos

Nos `.xlsx` recebidos (que vieram de planilhas do Google), células numéricas de `price`, `freight_value` e `payment_value` foram convertidas em **datas** (por exemplo `2024-10-29 00:00:00`). Não é possível recuperar o valor original, então a skill não "conserta": ignora o item na soma e informa a quantidade no aviso. Por isso o ticket médio acima pode estar levemente **subestimado** (168 de cerca de 110 mil itens entregues). Com os CSVs originais do Olist o resultado exato pode diferir; as contagens de pedidos (meses e UFs) não dependem dessas colunas.

## Verificações

Resumo (detalhes em [`docs/verificacoes.md`](docs/verificacoes.md)):

- **Passou:** 40 testes automatizados; resultados esperados do recorte calculados à parte em SQL; conferência SQL nos dados completos; leitura de `.xlsx` igual à de `.csv`; testes da skill no Claude Code (ativação explícita e automática, pedido de continuação, período sem dados, pergunta que a base não permite responder, entrada ausente, pedido fora do escopo, pedido não relacionado).
- **Falhou e foi corrigido:** na primeira versão a skill não era escolhida para a pergunta de margem de lucro; a `description` foi ampliada e o teste repetido.
- **Não verificado:** uso no Codex (`$analise-olist`, `.agents/skills/`), Windows, resultados com os CSVs originais não corrompidos e o dicionário oficial do professor.

## Fluxo no GitHub

Cada parte foi feita em uma branch e integrada na `main`: `test/recorte-e-testes` (recorte e testes escritos antes do código), `feat/script-analises`, `feat/skill-md` e `docs/verificacoes`. O histórico (`git log --graph`) mostra que o commit `test:` vem antes do commit `feat:`.

## Entrega da atividade

1. `SKILL.md` (este arquivo, mantido igual na pasta da skill): [`.claude/skills/analise-olist/SKILL.md`](.claude/skills/analise-olist/SKILL.md)
2. Este repositório no GitHub, com a skill, as referências, o código, as saídas e as verificações.
3. Print do copiloto em uso: ver [`docs/roteiro-do-print.md`](docs/roteiro-do-print.md).
