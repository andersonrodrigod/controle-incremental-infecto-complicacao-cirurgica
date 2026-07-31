import pandas as pd

from core import caminhos
from services import inicializacao


def _configuracoes_base(tmp_path):
    caminho_infecto = tmp_path / "INFECTO" / "2026" / "JUNHO"
    caminho_sciras = tmp_path / "INFECTO SCIRAS" / "2026" / "JUNHO"

    return {
        "estrutura_criacao": {
            "por_fluxos": True,
        },
        "fluxos": {
            "p1": {
                "entrada": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "",
                    "nome": "COMPLICACAO JUNHO.xlsx",
                    "aba": "BASE",
                },
                "destino": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "",
                    "nome": "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx",
                    "aba": "BASE",
                },
                "auditoria": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA",
                    "nome": "auditoria_execucoes_p1.xlsx",
                    "aba": "BASE",
                },
                "backups": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA/backups/p1",
                },
                "log": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA/logs",
                    "nome": "execucoes_p1.log",
                },
            },
            "rp1": {
                "entrada": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "",
                    "nome": "COMPLICACAO JUNHO.xlsx",
                    "aba": "BASE",
                },
                "destino": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "",
                    "nome": "CONTROLE INFECTOLOGIA 60 DIAS - JUNHO.xlsx",
                    "aba": "BASE",
                },
                "auditoria": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA",
                    "nome": "auditoria_execucoes_rp1.xlsx",
                    "aba": "BASE",
                },
                "backups": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA/backups/rp1",
                },
                "log": {
                    "caminho_base": str(caminho_infecto),
                    "pasta": "DATA/logs",
                    "nome": "execucoes_rp1.log",
                },
            },
            "p1_sciras": {
                "entrada": {
                    "caminho_base": str(caminho_sciras),
                    "pasta": "",
                    "nome": "COMPLICACAO JUNHO.xlsx",
                    "aba": "BASE",
                },
                "destino": {
                    "caminho_base": str(caminho_sciras),
                    "pasta": "",
                    "nome": "CONTROLE INFECTOLOGIA 30 DIAS SCIRAS - JUNHO.xlsx",
                    "aba": "BASE",
                },
                "auditoria": {
                    "caminho_base": str(caminho_sciras),
                    "pasta": "DATA",
                    "nome": "auditoria_execucoes_p1_sciras.xlsx",
                    "aba": "BASE",
                },
                "backups": {
                    "caminho_base": str(caminho_sciras),
                    "pasta": "DATA/backups/p1_sciras",
                },
                "log": {
                    "caminho_base": str(caminho_sciras),
                    "pasta": "DATA/logs",
                    "nome": "execucoes_p1_sciras.log",
                },
            },
        },
        "colunas_destino": {
            "p1": ["SENHA", "P1"],
            "rp1": ["SENHA", "RP1 No"],
            "p1_sciras": ["SENHA", "P1 SCIRAS"],
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


def test_preparar_estrutura_operacional_cria_por_fluxos(
    monkeypatch,
    tmp_path,
):
    configuracoes = _configuracoes_base(tmp_path)
    _aplicar_configuracoes(monkeypatch, configuracoes)

    resumo = inicializacao.preparar_estrutura_operacional()

    caminho_infecto = tmp_path / "INFECTO" / "2026" / "JUNHO"
    caminho_sciras = tmp_path / "INFECTO SCIRAS" / "2026" / "JUNHO"
    caminho_p1 = (
        caminho_infecto / "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx"
    )
    caminho_rp1 = (
        caminho_infecto / "CONTROLE INFECTOLOGIA 60 DIAS - JUNHO.xlsx"
    )
    caminho_sciras_saida = (
        caminho_sciras / "CONTROLE INFECTOLOGIA 30 DIAS SCIRAS - JUNHO.xlsx"
    )
    caminho_auditoria_p1 = (
        caminho_infecto / "DATA" / "auditoria_execucoes_p1.xlsx"
    )
    caminho_auditoria_sciras = (
        caminho_sciras / "DATA" / "auditoria_execucoes_p1_sciras.xlsx"
    )

    assert caminho_p1.exists()
    assert caminho_rp1.exists()
    assert caminho_sciras_saida.exists()
    assert caminho_auditoria_p1.exists()
    assert caminho_auditoria_sciras.exists()
    assert (caminho_infecto / "DATA" / "backups" / "p1").is_dir()
    assert (caminho_infecto / "DATA" / "backups" / "rp1").is_dir()
    assert (caminho_infecto / "DATA" / "logs").is_dir()
    assert (caminho_sciras / "DATA" / "backups" / "p1_sciras").is_dir()
    assert (caminho_sciras / "DATA" / "logs").is_dir()
    assert not (caminho_infecto / "COMPLICACAO JUNHO.xlsx").exists()
    assert not (caminho_sciras / "COMPLICACAO JUNHO.xlsx").exists()
    assert resumo["arquivo_entrada_p1_existe"] is False
    assert resumo["arquivo_entrada_rp1_existe"] is False
    assert resumo["arquivo_entrada_p1_sciras_existe"] is False

    p1 = pd.read_excel(caminho_p1, sheet_name="BASE")
    rp1 = pd.read_excel(caminho_rp1, sheet_name="BASE")
    sciras = pd.read_excel(caminho_sciras_saida, sheet_name="BASE")
    auditoria = pd.read_excel(caminho_auditoria_p1, sheet_name="BASE")

    assert p1.columns.tolist() == ["SENHA", "P1"]
    assert rp1.columns.tolist() == ["SENHA", "RP1 No"]
    assert sciras.columns.tolist() == ["SENHA", "P1 SCIRAS"]
    assert auditoria.columns.tolist() == inicializacao.COLUNAS_AUDITORIA


def test_preparar_estrutura_operacional_nao_sobrescreve_saida_existente(
    monkeypatch,
    tmp_path,
):
    caminho_p1 = (
        tmp_path
        / "INFECTO"
        / "2026"
        / "JUNHO"
        / "CONTROLE INFECTOLOGIA 30 DIAS - JUNHO.xlsx"
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
