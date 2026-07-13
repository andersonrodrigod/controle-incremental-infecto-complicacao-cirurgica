import pandas as pd

from core import caminhos
from services import inicializacao


def _configuracoes_base(tmp_path):
    return {
        "estrutura_criacao": {
            "caminho_base": str(tmp_path),
            "pasta": "data",
            "arquivos": {
                "controle_30_dias": {
                    "nome": "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx",
                    "aba": "BASE",
                    "colunas_destino": "p1",
                },
                "controle_60_dias": {
                    "nome": "CONTROLE INFECTOLOGIA 60 DIAS - MAIO.xlsx",
                    "aba": "BASE",
                    "colunas_destino": "rp1",
                },
                "auditoria": {
                    "nome": "auditoria_execucoes.xlsx",
                    "aba": "BASE",
                },
            },
            "pastas": {
                "backups_30_dias": "backups/30_dias",
                "backups_60_dias": "backups/60_dias",
                "logs": "logs",
            },
        },
        "fluxos": {
            "p1": {
                "entrada": {
                    "caminho_base": str(tmp_path),
                    "pasta": "entrada_p1",
                    "nome": "COMPLICACAO JUNHO.xlsx",
                    "aba": "BASE",
                },
            },
            "rp1": {
                "entrada": {
                    "caminho_base": str(tmp_path),
                    "pasta": "entrada_rp1",
                    "nome": "COMPLICACAO MAIO.xlsx",
                    "aba": "BASE",
                },
            },
        },
        "colunas_destino": {
            "p1": ["SENHA", "P1"],
            "rp1": ["SENHA", "RP1 Nº"],
        },
    }


def _aplicar_configuracoes(monkeypatch, configuracoes):
    monkeypatch.setattr(
        inicializacao,
        "carregar_configuracoes",
        lambda: configuracoes,
    )
    monkeypatch.setattr(
        caminhos,
        "carregar_configuracoes",
        lambda: configuracoes,
    )


def test_preparar_estrutura_operacional_cria_pasta_arquivos_e_subpastas(
    monkeypatch,
    tmp_path,
):
    configuracoes = _configuracoes_base(tmp_path)
    _aplicar_configuracoes(monkeypatch, configuracoes)

    resumo = inicializacao.preparar_estrutura_operacional()

    caminho_p1 = (
        tmp_path / "data" / "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx"
    )
    caminho_rp1 = (
        tmp_path / "data" / "CONTROLE INFECTOLOGIA 60 DIAS - MAIO.xlsx"
    )
    caminho_auditoria = tmp_path / "data" / "auditoria_execucoes.xlsx"

    assert caminho_p1.exists()
    assert caminho_rp1.exists()
    assert caminho_auditoria.exists()
    assert (tmp_path / "data" / "backups" / "30_dias").is_dir()
    assert (tmp_path / "data" / "backups" / "60_dias").is_dir()
    assert (tmp_path / "data" / "logs").is_dir()
    assert not (tmp_path / "entrada_p1" / "COMPLICACAO JUNHO.xlsx").exists()
    assert not (tmp_path / "entrada_rp1" / "COMPLICACAO MAIO.xlsx").exists()
    assert resumo["arquivo_entrada_p1_existe"] is False
    assert resumo["arquivo_entrada_rp1_existe"] is False

    p1 = pd.read_excel(caminho_p1, sheet_name="BASE")
    rp1 = pd.read_excel(caminho_rp1, sheet_name="BASE")
    auditoria = pd.read_excel(caminho_auditoria, sheet_name="BASE")

    assert p1.columns.tolist() == ["SENHA", "P1"]
    assert rp1.columns.tolist() == ["SENHA", "RP1 Nº"]
    assert auditoria.columns.tolist() == inicializacao.COLUNAS_AUDITORIA


def test_preparar_estrutura_operacional_nao_sobrescreve_saida_existente(
    monkeypatch,
    tmp_path,
):
    caminho_p1 = (
        tmp_path / "data" / "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx"
    )
    caminho_p1.parent.mkdir(parents=True)
    pd.DataFrame([{"SENHA": "123", "P1": "Sim"}]).to_excel(
        caminho_p1,
        sheet_name="BASE",
        index=False,
    )

    configuracoes = _configuracoes_base(tmp_path)
    _aplicar_configuracoes(monkeypatch, configuracoes)

    inicializacao.preparar_estrutura_operacional()

    p1 = pd.read_excel(caminho_p1, sheet_name="BASE")

    assert p1.to_dict("records") == [{"SENHA": 123, "P1": "Sim"}]
