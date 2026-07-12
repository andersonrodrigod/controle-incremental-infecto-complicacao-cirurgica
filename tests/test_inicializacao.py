import pandas as pd

from core import caminhos
from services import inicializacao


def test_preparar_estrutura_operacional_cria_saidas_sem_criar_entrada(
    monkeypatch,
    tmp_path,
):
    configuracoes = {
        "caminho_base": str(tmp_path),
        "pastas": {
            "entrada": "entrada",
            "destino": "destino",
            "auditoria": "auditoria",
            "backups": "backups",
            "logs": "logs",
        },
        "arquivos": {
            "entrada": {
                "nome": "COMPLICACAO JUNHO.xlsx",
                "aba": "BASE",
            },
            "destino_p1": {
                "nome": "CONTROLE INFECTOLOGIA.xlsx",
                "aba": "BASE",
            },
            "destino_rp1": {
                "nome": "CONTROLE INFECTOLOGIA_RP1.xlsx",
                "aba": "BASE",
            },
            "auditoria": {
                "nome": "auditoria_execucoes.xlsx",
                "aba": "BASE",
            },
        },
        "colunas_destino": {
            "p1": ["SENHA", "P1"],
            "rp1": ["SENHA", "RP1 NÂº"],
        },
    }

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

    resumo = inicializacao.preparar_estrutura_operacional()

    caminho_entrada = tmp_path / "entrada" / "COMPLICACAO JUNHO.xlsx"
    caminho_p1 = tmp_path / "destino" / "CONTROLE INFECTOLOGIA.xlsx"
    caminho_rp1 = tmp_path / "destino" / "CONTROLE INFECTOLOGIA_RP1.xlsx"
    caminho_auditoria = (
        tmp_path / "auditoria" / "auditoria_execucoes.xlsx"
    )

    assert not caminho_entrada.exists()
    assert caminho_p1.exists()
    assert caminho_rp1.exists()
    assert caminho_auditoria.exists()
    assert resumo["arquivo_entrada_existe"] is False

    p1 = pd.read_excel(caminho_p1, sheet_name="BASE")
    rp1 = pd.read_excel(caminho_rp1, sheet_name="BASE")
    auditoria = pd.read_excel(caminho_auditoria, sheet_name="BASE")

    assert p1.columns.tolist() == ["SENHA", "P1"]
    assert rp1.columns.tolist() == ["SENHA", "RP1 NÂº"]
    assert auditoria.columns.tolist() == inicializacao.COLUNAS_AUDITORIA


def test_preparar_estrutura_operacional_nao_sobrescreve_saida_existente(
    monkeypatch,
    tmp_path,
):
    caminho_p1 = tmp_path / "destino" / "CONTROLE INFECTOLOGIA.xlsx"
    caminho_p1.parent.mkdir(parents=True)
    pd.DataFrame([{"SENHA": "123", "P1": "Sim"}]).to_excel(
        caminho_p1,
        sheet_name="BASE",
        index=False,
    )

    configuracoes = {
        "caminho_base": str(tmp_path),
        "pastas": {
            "entrada": "entrada",
            "destino": "destino",
            "auditoria": "auditoria",
            "backups": "backups",
            "logs": "logs",
        },
        "arquivos": {
            "entrada": {
                "nome": "COMPLICACAO JUNHO.xlsx",
                "aba": "BASE",
            },
            "destino_p1": {
                "nome": "CONTROLE INFECTOLOGIA.xlsx",
                "aba": "BASE",
            },
            "destino_rp1": {
                "nome": "CONTROLE INFECTOLOGIA_RP1.xlsx",
                "aba": "BASE",
            },
            "auditoria": {
                "nome": "auditoria_execucoes.xlsx",
                "aba": "BASE",
            },
        },
        "colunas_destino": {
            "p1": ["SENHA", "P1"],
            "rp1": ["SENHA", "RP1 NÂº"],
        },
    }

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

    inicializacao.preparar_estrutura_operacional()

    p1 = pd.read_excel(caminho_p1, sheet_name="BASE")

    assert p1.to_dict("records") == [{"SENHA": 123, "P1": "Sim"}]
