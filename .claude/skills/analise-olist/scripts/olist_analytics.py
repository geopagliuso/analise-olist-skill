#!/usr/bin/env python3
"""Análises da skill analise-olist (autor: George Pagliuso).

Responde, a partir dos arquivos do Olist, a três perguntas sobre PEDIDOS ENTREGUES:
  pedidos-por-mes  quantos pedidos entregues por mês
  top-ufs          as UFs dos clientes com mais pedidos entregues
  ticket-medio     soma do preço dos itens / nº de pedidos entregues distintos (sem frete)
e a um comando de apoio:
  inspecionar      lista os arquivos da pasta e suas colunas (para checar o que a base permite)

Regras (detalhes em ../references/regras-e-metricas.md):
  * só pedidos com order_status = delivered (descSituacao);
  * data de referência = order_purchase_timestamp (dtPedido);
  * período: datas inicial e final INCLUSIVAS, comparadas por dia do calendário;
  * nº de pedidos = order_id (idPedido) DISTINTOS;
  * o script só LÊ os dados; nenhum número é fixado no código.

Exemplos:
  python olist_analytics.py pedidos-por-mes --dados ./dados
  python olist_analytics.py top-ufs --dados ./dados --inicio 2018-01 --fim 2018-03 --top 5
  python olist_analytics.py ticket-medio --dados ./dados --uf SP --json
A pasta dos dados também pode vir da variável de ambiente OLIST_DATA_DIR.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------------------ configuração
SITUACAO_ENTREGUE = "delivered"
ARQ_PEDIDOS = "olist_orders_dataset"
ARQ_ITENS = "olist_order_items_dataset"
ARQ_CLIENTES = "olist_customers_dataset"
COLS_PEDIDOS = ["order_id", "customer_id", "order_status", "order_purchase_timestamp"]
COLS_ITENS = ["order_id", "price"]
COLS_CLIENTES = ["customer_id", "customer_state"]
# nomes dos arquivos reconhecidos pelo comando "inspecionar"
ARQUIVOS_CONHECIDOS = [
    ARQ_PEDIDOS, ARQ_ITENS, ARQ_CLIENTES, "olist_order_payments_dataset", "olist_products_dataset",
    "olist_sellers_dataset", "olist_order_reviews_dataset", "olist_geolocation_dataset",
    "product_category_name_translation",
]
EXTENSOES = (".csv", ".xlsx")
DATA_REF = "order_purchase_timestamp (dtPedido)"


class ErroDeEntrada(Exception):
    """Entrada ausente ou inválida: a mensagem explica o impedimento ao usuário."""


# ------------------------------------------------------------------------------ datas
def parse_data(texto: str, *, fim: bool) -> date:
    """Aceita AAAA-MM-DD ou AAAA-MM. Em AAAA-MM a data inicial vira o dia 1 e a final, o último dia."""
    texto = (texto or "").strip()
    try:
        if len(texto) == 7:
            ano, mes = int(texto[:4]), int(texto[5:7])
            if texto[4] != "-":
                raise ValueError
            return date(ano, mes, calendar.monthrange(ano, mes)[1] if fim else 1)
        if len(texto) == 10 and texto[4] == "-" and texto[7] == "-":
            return date.fromisoformat(texto)
    except ValueError:
        pass
    raise ErroDeEntrada(
        f"Data inválida: {texto!r}. Use AAAA-MM-DD (ex.: 2018-01-31) ou AAAA-MM (ex.: 2018-01)."
    )


# ------------------------------------------------------------------------------ leitura
def localizar(pasta: Path, nome: str) -> Path:
    for ext in EXTENSOES:
        caminho = pasta / f"{nome}{ext}"
        if caminho.is_file():
            return caminho
    raise ErroDeEntrada(
        f"Arquivo {nome}.csv (ou .xlsx) não encontrado na pasta {pasta}. "
        "Confira a pasta dos dados (--dados ou OLIST_DATA_DIR)."
    )


def cabecalho(caminho: Path) -> list[str]:
    if caminho.suffix == ".csv":
        with open(caminho, newline="", encoding="utf-8-sig") as f:
            return [c.strip() for c in next(csv.reader(f), [])]
    import openpyxl  # só necessário para .xlsx

    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    try:
        primeira = next(wb[wb.sheetnames[0]].iter_rows(max_row=1, values_only=True), ())
    finally:
        wb.close()
    return [("" if c is None else str(c)).strip() for c in primeira]


def ler_tabela(caminho: Path, colunas: list[str]) -> pd.DataFrame:
    """Lê só as colunas necessárias, tudo como texto; vazio vira ''. Valida a presença das colunas."""
    existentes = cabecalho(caminho)
    faltam = [c for c in colunas if c not in existentes]
    if faltam:
        raise ErroDeEntrada(
            f"Coluna(s) {faltam} não encontrada(s) em {caminho.name}. Colunas existentes: {existentes}."
        )
    if caminho.suffix == ".csv":
        df = pd.read_csv(caminho, usecols=colunas, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    else:
        df = pd.read_excel(caminho, usecols=colunas, dtype=str, engine="openpyxl").fillna("")
    for c in colunas:
        df[c] = df[c].astype(str).str.strip()
    return df


def validar_pasta(dados) -> Path:
    if not dados:
        raise ErroDeEntrada(
            "Informe a pasta dos dados com --dados <pasta> ou com a variável de ambiente OLIST_DATA_DIR."
        )
    pasta = Path(dados).expanduser()
    if not pasta.is_dir():
        raise ErroDeEntrada(f"A pasta dos dados não existe: {pasta}")
    return pasta


# ------------------------------------------------------------------------------ seleção comum
class Selecao:
    """Pedidos entregues, distintos, com data válida, no período (e UF, quando pedida)."""

    def __init__(self, pedidos, funil, avisos, arquivos, ids_todos):
        self.pedidos = pedidos
        self.funil = funil
        self.avisos = avisos
        self.arquivos = arquivos
        self.ids_todos = ids_todos


def _validar_periodo(inicio, fim):
    if inicio and fim and inicio > fim:
        raise ErroDeEntrada(f"A data inicial ({inicio}) é posterior à data final ({fim}).")


def selecionar(dados, inicio=None, fim=None, uf=None, precisa_uf=False) -> Selecao:
    pasta = validar_pasta(dados)
    _validar_periodo(inicio, fim)
    avisos: list[str] = []
    funil: dict = {}

    arq_ped = localizar(pasta, ARQ_PEDIDOS)
    arquivos = [str(arq_ped)]
    ped = ler_tabela(arq_ped, COLS_PEDIDOS)
    funil["linhas_pedidos"] = len(ped)
    ids_todos = set(ped["order_id"])

    situacao = ped["order_status"].str.lower()
    ent = ped[situacao == SITUACAO_ENTREGUE].copy()
    funil["linhas_entregues"] = len(ent)
    outros_ids = set(ped.loc[situacao != SITUACAO_ENTREGUE, "order_id"])

    vazios = int((ent["order_id"] == "").sum())
    if vazios:
        avisos.append(f"{vazios} linha(s) entregue(s) sem idPedido foram descartadas.")
        ent = ent[ent["order_id"] != ""]
    funil["sem_id"] = vazios

    conflito = len(set(ent["order_id"]) & outros_ids)
    if conflito:
        avisos.append(
            f"{conflito} idPedido aparecem como delivered e também com outra situação (conflito); "
            "foram mantidos como entregues."
        )
    repetidos = int(ent.duplicated("order_id").sum())
    if repetidos:
        avisos.append(f"{repetidos} linha(s) de idPedido repetido foram removidas (conta-se 1 por pedido).")
        ent = ent.drop_duplicates("order_id", keep="first")
    funil["repetidos_removidos"] = repetidos
    funil["entregues_distintos"] = len(ent)

    ent["dt"] = pd.to_datetime(ent["order_purchase_timestamp"], format="ISO8601", errors="coerce")
    sem_data = int(ent["dt"].isna().sum())
    funil["sem_data_valida"] = sem_data
    if sem_data:
        avisos.append(
            f"{sem_data} pedido(s) entregue(s) com data de pedido (dtPedido) ausente ou inválida ficam fora de todas as análises."
        )
        ent = ent[ent["dt"].notna()]
    ent["dia"] = ent["dt"].dt.normalize()

    if inicio:
        ent = ent[ent["dia"] >= pd.Timestamp(inicio)]
    if fim:
        ent = ent[ent["dia"] <= pd.Timestamp(fim)]
    funil["no_periodo"] = len(ent)

    if precisa_uf or uf:
        arq_cli = localizar(pasta, ARQ_CLIENTES)
        arquivos.append(str(arq_cli))
        cli = ler_tabela(arq_cli, COLS_CLIENTES)
        cli["uf"] = cli["customer_state"].str.upper()
        cli.loc[cli["uf"] == "", "uf"] = pd.NA
        rep_cli = int(cli.duplicated("customer_id").sum())
        if rep_cli:
            avisos.append(f"{rep_cli} linha(s) de clientes repetidos em idCliente; mantida a primeira ocorrência.")
            cli = cli.drop_duplicates("customer_id", keep="first")
        ufs_existentes = sorted(cli["uf"].dropna().unique())
        ent = ent.merge(cli[["customer_id", "uf"]], on="customer_id", how="left", validate="m:1")
        sem_cli = int((~ent["customer_id"].isin(set(cli["customer_id"]))).sum())
        cli_sem_uf = int(ent["uf"].isna().sum()) - sem_cli
        funil["sem_cliente_correspondente"] = sem_cli
        funil["cliente_sem_uf"] = cli_sem_uf
        if sem_cli:
            avisos.append(f"{sem_cli} pedido(s) sem cliente correspondente (idCliente não encontrado) ficam sem UF.")
        if cli_sem_uf:
            avisos.append(f"{cli_sem_uf} pedido(s) com cliente sem UF preenchida ficam sem UF.")
        if uf:
            uf = uf.strip().upper()
            if uf not in ufs_existentes:
                avisos.append(f"A UF {uf} não consta na base de clientes (UFs existentes: {', '.join(ufs_existentes)}).")
            ent = ent[ent["uf"] == uf]
    funil["selecionados"] = len(ent)
    return Selecao(ent, funil, avisos, arquivos, ids_todos)


def _filtros(inicio, fim, uf) -> dict:
    return {
        "situacao": f"descSituacao = {SITUACAO_ENTREGUE} (order_status)",
        "data_referencia": DATA_REF,
        "inicio": inicio.isoformat() if inicio else None,
        "fim": fim.isoformat() if fim else None,
        "intervalo": "datas inicial e final inclusivas, por dia do calendário",
        "uf": uf.strip().upper() if uf else None,
    }


def _pacote(analise, metrica, sel, inicio, fim, uf, resultado) -> dict:
    return {
        "analise": analise,
        "metrica": metrica,
        "filtros": _filtros(inicio, fim, uf),
        "arquivos": sel.arquivos,
        "resultado": resultado,
        "cobertura": sel.funil,
        "avisos": sel.avisos,
    }


# ------------------------------------------------------------------------------ análises
def pedidos_por_mes(dados, inicio=None, fim=None, uf=None) -> dict:
    sel = selecionar(dados, inicio, fim, uf)
    ped = sel.pedidos
    contagem = ped.groupby(ped["dia"].dt.to_period("M"))["order_id"].nunique()
    if inicio or fim:
        primeiro = pd.Period(inicio, "M") if inicio else (contagem.index.min() if len(contagem) else None)
        ultimo = pd.Period(fim, "M") if fim else (contagem.index.max() if len(contagem) else None)
    else:
        primeiro = contagem.index.min() if len(contagem) else None
        ultimo = contagem.index.max() if len(contagem) else None
    linhas = []
    if primeiro is not None and ultimo is not None:
        for mes in pd.period_range(primeiro, ultimo, freq="M"):
            parcial = bool(
                (inicio and mes == pd.Period(inicio, "M") and inicio.day != 1)
                or (fim and mes == pd.Period(fim, "M") and fim.day != calendar.monthrange(fim.year, fim.month)[1])
            )
            linhas.append({"mes": str(mes), "pedidos": int(contagem.get(mes, 0)), "mes_parcial": parcial})
    if any(l["mes_parcial"] for l in linhas):
        sel.avisos.append("Mês parcial: o período não cobre o mês inteiro (marcado em 'mes_parcial').")
    if sel.funil["selecionados"] == 0:
        sel.avisos.append("Nenhum pedido entregue no período/filtros informados: contagem = 0.")
    resultado = {"linhas": linhas, "total": int(sel.funil["selecionados"])}
    return _pacote(
        "pedidos-por-mes",
        "Quantidade de idPedido distintos com descSituacao = delivered, agrupados pelo mês de dtPedido.",
        sel, inicio, fim, uf, resultado,
    )


def top_ufs(dados, inicio=None, fim=None, uf=None, top=5) -> dict:
    if not isinstance(top, int) or top < 1:
        raise ErroDeEntrada("O valor de top deve ser um inteiro maior ou igual a 1.")
    sel = selecionar(dados, inicio, fim, uf, precisa_uf=True)
    com_uf = sel.pedidos[sel.pedidos["uf"].notna()]
    contagem = com_uf.groupby("uf")["order_id"].nunique().reset_index(name="pedidos")
    contagem = contagem.sort_values(["pedidos", "uf"], ascending=[False, True]).reset_index(drop=True)
    total = int(len(com_uf))
    if len(contagem) > top and contagem.loc[top - 1, "pedidos"] == contagem.loc[top, "pedidos"]:
        corte = int(contagem.loc[top - 1, "pedidos"])
        n_empate = int((contagem["pedidos"] == corte).sum())
        sel.avisos.append(
            f"Empate no corte do ranking: {n_empate} UFs têm {corte} pedido(s); "
            "o desempate mostrado é a ordem alfabética da UF."
        )
    if sel.funil["selecionados"] == 0:
        sel.avisos.append("Nenhum pedido entregue no período/filtros informados: ranking vazio.")
    linhas = [
        {"posicao": i + 1, "uf": r.uf, "pedidos": int(r.pedidos),
         "pct_dos_pedidos_com_uf": round(100 * r.pedidos / total, 2) if total else None}
        for i, r in contagem.head(top).iterrows()
    ]
    resultado = {"linhas": linhas, "top": top, "total_com_uf": total, "ufs_distintas": int(len(contagem))}
    return _pacote(
        "top-ufs",
        "UFs (descUF) dos clientes com mais idPedido distintos entregues; pedido e cliente ligados por idCliente.",
        sel, inicio, fim, uf, resultado,
    )


def ticket_medio(dados, inicio=None, fim=None, uf=None) -> dict:
    sel = selecionar(dados, inicio, fim, uf)
    pasta = validar_pasta(dados)
    arq_itens = localizar(pasta, ARQ_ITENS)
    sel.arquivos.append(str(arq_itens))
    itens = ler_tabela(arq_itens, COLS_ITENS)
    n_ped = int(sel.funil["selecionados"])

    orfaos = int((~itens["order_id"].isin(sel.ids_todos)).sum())
    if orfaos:
        sel.avisos.append(f"{orfaos} item(ns) na base inteira apontam para idPedido inexistente em pedidos.")
    sel.funil["itens_com_pedido_inexistente"] = orfaos

    itens = itens[itens["order_id"].isin(set(sel.pedidos["order_id"]))].copy()
    itens["preco"] = pd.to_numeric(itens["price"].replace("", pd.NA), errors="coerce")
    invalidos = int(itens["preco"].isna().sum())
    sel.funil["precos_invalidos"] = invalidos
    if invalidos:
        sel.avisos.append(
            f"{invalidos} item(ns) dos pedidos selecionados têm preço (vlPreco) ausente ou não numérico "
            "(ex.: célula convertida em data) e foram ignorados na soma; o ticket pode estar subestimado."
        )
    if (itens["preco"] < 0).any():
        sel.avisos.append("Há vlPreco negativo entre os itens selecionados; os valores foram mantidos na soma.")

    # Soma por pedido ANTES de qualquer junção: um pedido tem vários itens e não pode ser repetido.
    por_pedido = itens.groupby("order_id").agg(soma=("preco", "sum"), itens=("order_id", "size"))
    com_itens = int(len(por_pedido))
    soma_total = float(por_pedido["soma"].sum()) if com_itens else 0.0
    sem_itens = n_ped - com_itens
    sel.funil["pedidos_com_itens"] = com_itens
    sel.funil["pedidos_sem_itens"] = sem_itens
    if sem_itens:
        sel.avisos.append(
            f"{sem_itens} pedido(s) selecionado(s) sem itens: ficam no denominador do ticket "
            "(nº de pedidos distintos) e reduzem a cobertura."
        )
    if n_ped == 0:
        sel.avisos.append("Nenhum pedido entregue no período/filtros informados: ticket médio não aplicável.")
    resultado = {
        "pedidos": n_ped,
        "itens": int(por_pedido["itens"].sum()) if com_itens else 0,
        "pedidos_com_itens": com_itens,
        "cobertura_itens_pct": round(100 * com_itens / n_ped, 2) if n_ped else None,
        "soma_preco": round(soma_total, 2),
        "ticket_medio": round(soma_total / n_ped, 2) if n_ped else None,
        "ticket_medio_apenas_pedidos_com_itens": round(soma_total / com_itens, 2) if com_itens else None,
        "frete_incluido": False,
    }
    return _pacote(
        "ticket-medio",
        "Soma de vlPreco dos itens dos pedidos entregues selecionados dividida pelo número de idPedido "
        "distintos selecionados, sem vlFrete.",
        sel, inicio, fim, uf, resultado,
    )


def inspecionar(dados) -> dict:
    pasta = validar_pasta(dados)
    tabelas = []
    for nome in ARQUIVOS_CONHECIDOS:
        for ext in EXTENSOES:
            caminho = pasta / f"{nome}{ext}"
            if caminho.is_file():
                tabelas.append({"tabela": nome, "arquivo": str(caminho), "colunas": cabecalho(caminho)})
                break
    if not tabelas:
        raise ErroDeEntrada(f"Nenhum arquivo do Olist reconhecido em {pasta}. Esperados: {ARQUIVOS_CONHECIDOS}.")
    ausentes = [n for n in ARQUIVOS_CONHECIDOS if n not in {t['tabela'] for t in tabelas}]
    return {
        "analise": "inspecionar",
        "metrica": "Arquivos e colunas existentes na pasta dos dados (apenas o cabeçalho é lido).",
        "filtros": {},
        "arquivos": [t["arquivo"] for t in tabelas],
        "resultado": {"tabelas": tabelas, "nao_encontrados": ausentes},
        "cobertura": {},
        "avisos": [],
    }


# ------------------------------------------------------------------------------ saída
def _tabela(cabecalhos, linhas) -> str:
    out = ["| " + " | ".join(cabecalhos) + " |", "| " + " | ".join("---" for _ in cabecalhos) + " |"]
    out += ["| " + " | ".join("" if v is None else str(v) for v in l) + " |" for l in linhas]
    return "\n".join(out)


def formatar_markdown(res: dict) -> str:
    f, r, a = res["filtros"], res["resultado"], res["analise"]
    txt = [f"## {a}", f"**Métrica:** {res['metrica']}"]
    if f:
        periodo = f"{f['inicio'] or 'início da base'} a {f['fim'] or 'fim da base'} ({f['intervalo']})"
        txt.append(f"**Filtros:** {f['situacao']}; data de referência {f['data_referencia']}; "
                   f"período {periodo}; UF: {f['uf'] or 'todas'}")
    txt.append("**Arquivos:** " + ", ".join(Path(p).name for p in res["arquivos"]))
    if a == "pedidos-por-mes":
        txt += ["", _tabela(["mês", "pedidos entregues", "mês parcial"],
                            [(l["mes"], l["pedidos"], "sim" if l["mes_parcial"] else "") for l in r["linhas"]]),
                f"\n**Total no período:** {r['total']}"]
    elif a == "top-ufs":
        txt += ["", _tabela(["posição", "UF", "pedidos entregues", "% dos pedidos com UF"],
                            [(l["posicao"], l["uf"], l["pedidos"], l["pct_dos_pedidos_com_uf"]) for l in r["linhas"]]),
                f"\n**Pedidos com UF no período:** {r['total_com_uf']} em {r['ufs_distintas']} UF(s)"]
    elif a == "ticket-medio":
        tk = r["ticket_medio"]
        txt += ["", _tabela(["indicador", "valor"], [
            ("pedidos entregues distintos (denominador)", r["pedidos"]),
            ("itens", r["itens"]),
            ("pedidos com itens", r["pedidos_com_itens"]),
            ("cobertura de itens (%)", r["cobertura_itens_pct"] if r["cobertura_itens_pct"] is not None else "não aplicável"),
            ("soma de vlPreco (sem frete)", r["soma_preco"]),
            ("**ticket médio**", tk if tk is not None else "não aplicável (sem pedidos)"),
            ("ticket médio só dos pedidos com itens", r["ticket_medio_apenas_pedidos_com_itens"]
             if r["ticket_medio_apenas_pedidos_com_itens"] is not None else "não aplicável"),
        ])]
    elif a == "inspecionar":
        for t in r["tabelas"]:
            txt.append(f"- **{t['tabela']}**: {', '.join(t['colunas'])}")
        if r["nao_encontrados"]:
            txt.append("- Não encontrados: " + ", ".join(r["nao_encontrados"]))
    if res["cobertura"]:
        txt += ["", "**Cobertura e conferências:** " + "; ".join(f"{k} = {v}" for k, v in res["cobertura"].items())]
    if res["avisos"]:
        txt += ["", "**Avisos:**"] + [f"- {x}" for x in res["avisos"]]
    return "\n".join(txt)


def _nome_base(res: dict) -> str:
    f = res["filtros"]
    periodo = f"{f['inicio']}_{f['fim']}" if f.get("inicio") and f.get("fim") else \
        f"desde-{f['inicio']}" if f.get("inicio") else f"ate-{f['fim']}" if f.get("fim") else "toda-a-base"
    partes = [res["analise"], periodo]
    if f.get("uf"):
        partes.append(f"UF-{f['uf']}")
    return "__".join(partes)


def salvar(res: dict, destino: Path, dados: Path, sobrescrever: bool) -> list[Path]:
    destino = destino.expanduser().resolve()
    dados = dados.expanduser().resolve()
    if destino == dados or dados in destino.parents:
        raise ErroDeEntrada("A pasta de saída não pode ficar dentro da pasta dos dados (os originais são preservados).")
    base = _nome_base(res)
    alvos = [destino / f"{base}.json", destino / f"{base}.csv"]
    existentes = [p.name for p in alvos if p.exists()]
    if existentes and not sobrescrever:
        raise ErroDeEntrada(f"Já existe: {', '.join(existentes)}. Use --sobrescrever para substituir.")
    destino.mkdir(parents=True, exist_ok=True)
    alvos[0].write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    linhas = res["resultado"].get("linhas")
    if linhas is None:
        linhas = [{k: v for k, v in res["resultado"].items() if not isinstance(v, (list, dict))}]
    pd.DataFrame(linhas).to_csv(alvos[1], index=False)
    return alvos


# ------------------------------------------------------------------------------ linha de comando
def montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Análises Olist (pedidos entregues) - skill analise-olist.")
    p.add_argument("analise", choices=["pedidos-por-mes", "top-ufs", "ticket-medio", "inspecionar"])
    p.add_argument("--dados", help="pasta com os arquivos do Olist (ou defina OLIST_DATA_DIR)")
    p.add_argument("--inicio", help="data inicial inclusiva: AAAA-MM-DD ou AAAA-MM")
    p.add_argument("--fim", help="data final inclusiva: AAAA-MM-DD ou AAAA-MM")
    p.add_argument("--uf", help="filtra a UF do cliente (ex.: SP)")
    p.add_argument("--top", type=int, default=5, help="tamanho do ranking de UFs (padrão 5)")
    p.add_argument("--json", action="store_true", help="imprime JSON em vez de tabela em Markdown")
    p.add_argument("--saida", help="pasta onde salvar .json e .csv (nunca dentro da pasta dos dados)")
    p.add_argument("--sobrescrever", action="store_true", help="permite substituir saídas existentes")
    return p


def main(argv=None) -> int:
    args = montar_parser().parse_args(argv)
    try:
        dados = args.dados or os.environ.get("OLIST_DATA_DIR")
        inicio = parse_data(args.inicio, fim=False) if args.inicio else None
        fim = parse_data(args.fim, fim=True) if args.fim else None
        if args.analise == "inspecionar":
            res = inspecionar(dados)
        elif args.analise == "pedidos-por-mes":
            res = pedidos_por_mes(dados, inicio, fim, args.uf)
        elif args.analise == "top-ufs":
            res = top_ufs(dados, inicio, fim, args.uf, args.top)
        else:
            res = ticket_medio(dados, inicio, fim, args.uf)
        salvos = salvar(res, Path(args.saida), Path(dados), args.sobrescrever) if args.saida else []
    except ErroDeEntrada as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2) if args.json else formatar_markdown(res))
    for caminho in salvos:
        print(f"[salvo] {os.path.relpath(caminho)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
