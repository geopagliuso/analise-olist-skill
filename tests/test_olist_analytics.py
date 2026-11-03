"""Testes do script da skill analise-olist (autor: George Pagliuso).

Duas famílias de teste:
1. RECORTE REAL (tests/fixtures/olist_recorte): linhas reais do Olist. Os valores esperados
   foram calculados de forma independente com SQL (tests/fixtures/conferencia_sqlite.py).
2. CASOS SINTÉTICOS (pasta temporária): montam, linha a linha, situações raras que o recorte
   real não contém (pedido sem item, data inválida, preço corrompido, id repetido...).
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / ".claude" / "skills" / "analise-olist" / "scripts"))
import olist_analytics as oa  # noqa: E402

RECORTE = RAIZ / "tests" / "fixtures" / "olist_recorte"


# ----------------------------------------------------------------------------- utilitários
def monta_pasta(destino: Path, pedidos=(), itens=(), clientes=()):
    """Cria uma pasta de dados sintética com as 3 tabelas usadas pelas análises."""
    destino.mkdir(parents=True, exist_ok=True)

    def grava(nome, cab, linhas):
        with open(destino / f"{nome}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cab)
            w.writerows(linhas)

    grava("olist_orders_dataset",
          ["order_id", "customer_id", "order_status", "order_purchase_timestamp"], pedidos)
    grava("olist_order_items_dataset", ["order_id", "price"], itens)
    grava("olist_customers_dataset", ["customer_id", "customer_state"], clientes)
    return destino


def linhas_mes(res):
    return {r["mes"]: r["pedidos"] for r in res["resultado"]["linhas"]}


# ----------------------------------------------------------------------------- recorte real
def test_pedidos_por_mes_recorte_sem_periodo():
    res = oa.pedidos_por_mes(RECORTE)
    # esperado (SQL): 2017-11=5, 2018-01=7, 2018-03=5; meses sem pedido entram com zero
    assert linhas_mes(res) == {"2017-11": 5, "2017-12": 0, "2018-01": 7, "2018-02": 0, "2018-03": 5}
    assert res["resultado"]["total"] == 17


def test_so_pedidos_entregues_contam():
    # o recorte tem 23 pedidos; só 17 são delivered
    res = oa.pedidos_por_mes(RECORTE)
    assert res["cobertura"]["linhas_pedidos"] == 23
    assert res["cobertura"]["selecionados"] == 17


def test_continuacao_muda_o_periodo():
    res = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 3, 31))
    assert linhas_mes(res) == {"2018-01": 7, "2018-02": 0, "2018-03": 5}
    assert res["resultado"]["total"] == 12


def test_datas_inicial_e_final_sao_inclusivas_por_dia():
    # dois pedidos de 2018-01-31, um deles às 22h ou mais: a data final inclui o dia inteiro
    res = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 1, 31), fim=date(2018, 1, 31))
    assert res["resultado"]["total"] == 2
    # terminar em 30/01 deixa os dois de fora (restam 5 em janeiro)
    res = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 1, 30))
    assert res["resultado"]["total"] == 5
    # pedido às 00:00:00 de 01/03 entra quando a inicial é 01/03
    res = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 3, 1), fim=date(2018, 3, 31))
    assert res["resultado"]["total"] == 5


def test_mes_parcial_e_sinalizado():
    res = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 1, 10), fim=date(2018, 1, 31))
    linha = res["resultado"]["linhas"][0]
    assert linha["mes"] == "2018-01" and linha["pedidos"] == 4 and linha["mes_parcial"] is True
    cheio = oa.pedidos_por_mes(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 1, 31))
    assert cheio["resultado"]["linhas"][0]["mes_parcial"] is False


def test_top_ufs_recorte_com_empate_no_corte():
    res = oa.top_ufs(RECORTE, top=5)
    ranking = [(r["uf"], r["pedidos"]) for r in res["resultado"]["linhas"]]
    # esperado (SQL): SP=9, MG=3 e cinco UFs com 1 pedido; desempate por UF (ordem alfabética)
    assert ranking == [("SP", 9), ("MG", 3), ("AL", 1), ("BA", 1), ("PR", 1)]
    assert res["resultado"]["total_com_uf"] == 17
    assert any("empate" in a.lower() for a in res["avisos"])


def test_top_ufs_com_filtro_de_periodo():
    res = oa.top_ufs(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 1, 31), top=2)
    soma = sum(r["pedidos"] for r in res["resultado"]["linhas"])
    assert res["resultado"]["total_com_uf"] == 7 and soma <= 7


def test_ticket_medio_recorte_todo_periodo():
    res = oa.ticket_medio(RECORTE)
    r = res["resultado"]
    # esperado (SQL): 141.441765 = soma(price) / 17 pedidos distintos, sem frete
    assert r["pedidos"] == 17
    assert r["ticket_medio"] == pytest.approx(141.441765, abs=0.005)  # saída arredondada a 2 casas
    assert r["cobertura_itens_pct"] == 100.0
    assert r["itens"] > r["pedidos"]  # há pedidos com vários itens: não se divide por itens


def test_ticket_medio_continuacao_periodo_e_uf():
    jan = oa.ticket_medio(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 1, 31))["resultado"]
    assert jan["pedidos"] == 7 and jan["ticket_medio"] == pytest.approx(216.227143, abs=0.005)
    sp = oa.ticket_medio(RECORTE, inicio=date(2018, 1, 1), fim=date(2018, 1, 31), uf="SP")["resultado"]
    assert sp["pedidos"] == 3 and sp["ticket_medio"] == pytest.approx(219.963333, abs=0.005)


def test_frete_corrompido_nao_afeta_o_ticket():
    # no recorte há células de freight_value viradas em data; o ticket não usa frete
    res = oa.ticket_medio(RECORTE)
    assert not any("freight" in a for a in res["avisos"])


def test_periodo_sem_dados():
    meses = oa.pedidos_por_mes(RECORTE, inicio=date(2019, 1, 1), fim=date(2019, 2, 28))
    assert linhas_mes(meses) == {"2019-01": 0, "2019-02": 0} and meses["resultado"]["total"] == 0
    ufs = oa.top_ufs(RECORTE, inicio=date(2019, 1, 1), fim=date(2019, 1, 31))
    assert ufs["resultado"]["linhas"] == [] and ufs["resultado"]["total_com_uf"] == 0
    tk = oa.ticket_medio(RECORTE, inicio=date(2019, 1, 1), fim=date(2019, 1, 31))["resultado"]
    assert tk["pedidos"] == 0 and tk["ticket_medio"] is None  # média sem pedidos = não aplicável


def test_uf_inexistente_gera_zero_e_aviso():
    res = oa.ticket_medio(RECORTE, uf="XX")
    assert res["resultado"]["pedidos"] == 0 and res["resultado"]["ticket_medio"] is None
    assert any("XX" in a for a in res["avisos"])


# ----------------------------------------------------------------------------- inspeção
def test_inspecionar_lista_arquivos_e_colunas():
    res = oa.inspecionar(RECORTE)
    nomes = {t["tabela"] for t in res["resultado"]["tabelas"]}
    assert "olist_orders_dataset" in nomes
    colunas = {c for t in res["resultado"]["tabelas"] for c in t["colunas"]}
    assert "order_status" in colunas
    # a base não tem dados de custo/lucro: a skill precisa recusar perguntas sobre isso
    assert not {"cost", "profit", "margin", "lucro", "custo"} & colunas


# ----------------------------------------------------------------------------- entradas inválidas
def test_pasta_inexistente(tmp_path):
    with pytest.raises(oa.ErroDeEntrada, match="pasta"):
        oa.pedidos_por_mes(tmp_path / "nao_existe")


def test_arquivo_ausente(tmp_path):
    pasta = monta_pasta(tmp_path / "d")
    (pasta / "olist_orders_dataset.csv").unlink()
    with pytest.raises(oa.ErroDeEntrada, match="olist_orders_dataset"):
        oa.pedidos_por_mes(pasta)


def test_coluna_ausente(tmp_path):
    pasta = monta_pasta(tmp_path / "d")
    (pasta / "olist_orders_dataset.csv").write_text("order_id,customer_id\n", encoding="utf-8")
    with pytest.raises(oa.ErroDeEntrada, match="order_status"):
        oa.pedidos_por_mes(pasta)


@pytest.mark.parametrize("texto", ["ontem", "2018-13-01", "2018/01/01", "31-01-2018", ""])
def test_data_invalida(texto):
    with pytest.raises(oa.ErroDeEntrada):
        oa.parse_data(texto, fim=False)


def test_parse_data_aceita_mes_e_completa_inicio_e_fim():
    assert oa.parse_data("2018-02", fim=False) == date(2018, 2, 1)
    assert oa.parse_data("2018-02", fim=True) == date(2018, 2, 28)
    assert oa.parse_data("2020-02", fim=True) == date(2020, 2, 29)
    assert oa.parse_data("2018-02-10", fim=True) == date(2018, 2, 10)


def test_inicio_depois_do_fim():
    with pytest.raises(oa.ErroDeEntrada, match="inicial"):
        oa.pedidos_por_mes(RECORTE, inicio=date(2018, 3, 1), fim=date(2018, 1, 1))


def test_top_invalido():
    with pytest.raises(oa.ErroDeEntrada, match="top"):
        oa.top_ufs(RECORTE, top=0)


# ----------------------------------------------------------------------------- casos sintéticos
PED = [
    ("p1", "c1", "delivered", "2018-01-05 10:00:00"),
    ("p2", "c2", "delivered", "2018-01-20 23:59:59"),
    ("p3", "c1", "delivered", "2018-02-01 00:00:00"),
    ("p4", "c3", "canceled", "2018-01-10 09:00:00"),
]
CLI = [("c1", "SP"), ("c2", "RJ"), ("c3", "SP")]


def test_pedido_entregue_sem_itens_fica_no_denominador(tmp_path):
    itens = [("p1", "100.00"), ("p1", "50.00"), ("p2", "30.00")]  # p3 não tem item
    pasta = monta_pasta(tmp_path / "d", PED, itens, CLI)
    res = oa.ticket_medio(pasta)
    r = res["resultado"]
    assert r["pedidos"] == 3 and r["itens"] == 3 and r["pedidos_com_itens"] == 2
    assert r["soma_preco"] == pytest.approx(180.0)
    assert r["ticket_medio"] == pytest.approx(60.0)                # 180 / 3 pedidos
    assert r["ticket_medio_apenas_pedidos_com_itens"] == pytest.approx(90.0)  # 180 / 2
    assert r["cobertura_itens_pct"] == pytest.approx(66.67, abs=0.01)
    assert any("sem itens" in a for a in res["avisos"])


def test_varios_itens_nao_multiplicam_pedidos(tmp_path):
    itens = [("p1", "10"), ("p1", "10"), ("p1", "10"), ("p1", "10")]
    pasta = monta_pasta(tmp_path / "d", PED[:1], itens, CLI)
    assert oa.pedidos_por_mes(pasta)["resultado"]["total"] == 1
    assert oa.ticket_medio(pasta)["resultado"]["ticket_medio"] == pytest.approx(40.0)


def test_data_invalida_e_ausente_saem_e_sao_avisadas(tmp_path):
    ped = PED + [("p5", "c1", "delivered", "isto-nao-e-data"), ("p6", "c1", "delivered", "")]
    pasta = monta_pasta(tmp_path / "d", ped, [], CLI)
    res = oa.pedidos_por_mes(pasta)
    assert res["resultado"]["total"] == 3
    assert res["cobertura"]["sem_data_valida"] == 2
    assert any("data" in a.lower() for a in res["avisos"])


def test_id_de_pedido_repetido_conta_uma_vez(tmp_path):
    ped = PED + [("p1", "c1", "delivered", "2018-01-05 10:00:00")]
    pasta = monta_pasta(tmp_path / "d", ped, [("p1", "10")], CLI)
    res = oa.pedidos_por_mes(pasta)
    assert res["resultado"]["total"] == 3
    assert any("repetid" in a for a in res["avisos"])


def test_id_com_situacoes_conflitantes_e_avisado(tmp_path):
    ped = PED + [("p1", "c1", "canceled", "2018-01-06 10:00:00")]
    pasta = monta_pasta(tmp_path / "d", ped, [], CLI)
    res = oa.pedidos_por_mes(pasta)
    assert any("conflit" in a for a in res["avisos"])


def test_preco_corrompido_vira_ausente_e_e_avisado(tmp_path):
    itens = [("p1", "100.00"), ("p1", "2024-10-29 00:00:00"), ("p2", ""), ("p3", "20.00")]
    pasta = monta_pasta(tmp_path / "d", PED, itens, CLI)
    res = oa.ticket_medio(pasta)
    assert res["resultado"]["soma_preco"] == pytest.approx(120.0)  # só os preços válidos
    assert res["cobertura"]["precos_invalidos"] == 2
    assert any("preço" in a for a in res["avisos"])


def test_cliente_sem_correspondencia_fica_fora_do_ranking(tmp_path):
    ped = PED + [("p7", "c-fantasma", "delivered", "2018-01-09 10:00:00")]
    pasta = monta_pasta(tmp_path / "d", ped, [], CLI)
    res = oa.top_ufs(pasta)
    assert res["resultado"]["total_com_uf"] == 3
    assert res["cobertura"]["sem_cliente_correspondente"] == 1
    assert any("sem cliente" in a for a in res["avisos"])
    # o pedido sem cliente continua contando na análise por mês, que não depende de UF
    assert oa.pedidos_por_mes(pasta)["resultado"]["total"] == 4


def test_cliente_repetido_nao_multiplica_pedidos(tmp_path):
    cli = CLI + [("c1", "SP")]
    pasta = monta_pasta(tmp_path / "d", PED, [], cli)
    res = oa.top_ufs(pasta)
    assert res["resultado"]["total_com_uf"] == 3
    assert any("clientes repetid" in a for a in res["avisos"])


def test_uf_em_minusculas_e_espacos_e_normalizada(tmp_path):
    cli = [("c1", " sp "), ("c2", "rj"), ("c3", "SP")]
    pasta = monta_pasta(tmp_path / "d", PED, [], cli)
    ufs = {r["uf"]: r["pedidos"] for r in oa.top_ufs(pasta)["resultado"]["linhas"]}
    assert ufs == {"SP": 2, "RJ": 1}
    assert oa.ticket_medio(pasta, uf="sp")["resultado"]["pedidos"] == 2


def test_arquivo_xlsx_da_o_mesmo_resultado_que_csv(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    pasta = tmp_path / "xlsx"
    pasta.mkdir()
    for nome in ("olist_orders_dataset", "olist_order_items_dataset", "olist_customers_dataset"):
        wb = openpyxl.Workbook()
        ws = wb.active
        with open(RECORTE / f"{nome}.csv", newline="", encoding="utf-8") as f:
            for linha in csv.reader(f):
                ws.append(linha)
        wb.save(pasta / f"{nome}.xlsx")
    a, b = oa.ticket_medio(RECORTE), oa.ticket_medio(pasta)
    assert a["resultado"] == b["resultado"]
    assert linhas_mes(oa.pedidos_por_mes(RECORTE)) == linhas_mes(oa.pedidos_por_mes(pasta))
    assert oa.top_ufs(RECORTE)["resultado"] == oa.top_ufs(pasta)["resultado"]


# ----------------------------------------------------------------------------- linha de comando
def test_cli_json(capsys):
    codigo = oa.main(["ticket-medio", "--dados", str(RECORTE), "--inicio", "2018-01", "--fim", "2018-01", "--json"])
    saida = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert saida["filtros"]["inicio"] == "2018-01-01" and saida["filtros"]["fim"] == "2018-01-31"
    assert saida["resultado"]["pedidos"] == 7


def test_cli_markdown_mostra_metrica_filtros_arquivos(capsys):
    assert oa.main(["top-ufs", "--dados", str(RECORTE), "--top", "3"]) == 0
    texto = capsys.readouterr().out
    for esperado in ("Métrica", "Filtros", "Arquivos", "olist_orders_dataset", "SP"):
        assert esperado in texto


def test_cli_variavel_de_ambiente(monkeypatch, capsys):
    monkeypatch.setenv("OLIST_DATA_DIR", str(RECORTE))
    assert oa.main(["pedidos-por-mes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["resultado"]["total"] == 17


def test_cli_sem_pasta_de_dados_explica(monkeypatch, capsys):
    monkeypatch.delenv("OLIST_DATA_DIR", raising=False)
    assert oa.main(["pedidos-por-mes"]) == 2
    assert "--dados" in capsys.readouterr().err


def test_cli_erro_de_entrada_retorna_2(capsys):
    assert oa.main(["pedidos-por-mes", "--dados", str(RECORTE), "--inicio", "ontem"]) == 2
    assert "data" in capsys.readouterr().err.lower()


def test_cli_salva_saida_sem_sobrescrever_nem_gravar_nos_dados(tmp_path, capsys):
    saida = tmp_path / "saidas"
    args = ["pedidos-por-mes", "--dados", str(RECORTE), "--saida", str(saida)]
    assert oa.main(args) == 0
    arquivos = sorted(p.name for p in saida.iterdir())
    assert len(arquivos) == 2 and {Path(a).suffix for a in arquivos} == {".csv", ".json"}
    capsys.readouterr()
    assert oa.main(args) == 2                       # já existe: não sobrescreve
    assert "sobrescrever" in capsys.readouterr().err
    assert oa.main(args + ["--sobrescrever"]) == 0
    dentro = ["pedidos-por-mes", "--dados", str(RECORTE), "--saida", str(RECORTE / "x")]
    assert oa.main(dentro) == 2                     # nunca grava dentro da pasta dos dados
    assert not (RECORTE / "x").exists()
