import pandas as pd

from services.tipagem import aplicar_schema_colunas


def test_aplicar_schema_colunas_converte_tipos_configurados():
    dados = pd.DataFrame(
        {
            "SENHA": [123],
            "TELEFONE 1": [5585992493600],
            "DIARIAS": ["2"],
            "DT INTERNACAO": ["2026-07-13"],
            "DUPLICIDADE": ["sim"],
        }
    )

    resultado = aplicar_schema_colunas(
        dados=dados,
        schema_colunas={
            "texto": ["SENHA", "TELEFONE 1"],
            "numero": ["DIARIAS"],
            "data": ["DT INTERNACAO"],
            "booleano": ["DUPLICIDADE"],
        },
    )

    assert str(resultado["SENHA"].dtype) == "string"
    assert str(resultado["TELEFONE 1"].dtype) == "string"
    assert str(resultado["DIARIAS"].dtype) == "int64"
    assert str(resultado["DT INTERNACAO"].dtype) == "datetime64[ns]"
    assert str(resultado["DUPLICIDADE"].dtype) == "boolean"
    assert resultado.loc[0, "TELEFONE 1"] == "5585992493600"
