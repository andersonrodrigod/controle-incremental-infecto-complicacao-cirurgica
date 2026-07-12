import pandas as pd

from services import auditoria


def test_registrar_auditoria_execucao_cria_e_acrescenta_linhas(
    monkeypatch,
    tmp_path
):
    caminho_auditoria = tmp_path / "auditoria_execucoes.xlsx"

    monkeypatch.setattr(
        auditoria,
        "obter_caminho_arquivo",
        lambda nome: caminho_auditoria
    )
    monkeypatch.setattr(
        auditoria,
        "carregar_configuracoes",
        lambda: {
            "arquivos": {
                "auditoria": {
                    "aba": "BASE"
                }
            }
        }
    )

    auditoria.registrar_auditoria_execucao(
        {
            "status": "SUCESSO",
            "linhas_lidas": 10,
        }
    )
    auditoria.registrar_auditoria_execucao(
        {
            "status": "FALHA",
            "mensagem_erro": "erro de teste",
        }
    )

    resultado = pd.read_excel(caminho_auditoria, sheet_name="BASE")

    assert resultado["status"].tolist() == ["SUCESSO", "FALHA"]
    assert resultado.loc[0, "linhas_lidas"] == 10
    assert resultado.loc[1, "mensagem_erro"] == "erro de teste"
