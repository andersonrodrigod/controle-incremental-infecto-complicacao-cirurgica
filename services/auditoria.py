from datetime import datetime
from typing import Any

import pandas as pd

from core.caminhos import obter_caminho_arquivo
from core.config import carregar_configuracoes


FORMATO_DATA_HORA_AUDITORIA = "%Y-%m-%d %H:%M:%S"


def registrar_auditoria_execucao(
    registro: dict[str, Any]
) -> None:
    configuracoes = carregar_configuracoes()
    configuracao_auditoria = configuracoes["arquivos"]["auditoria"]
    caminho_auditoria = obter_caminho_arquivo("auditoria")

    caminho_auditoria.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    registro_auditoria = {
        "data_hora": datetime.now().strftime(
            FORMATO_DATA_HORA_AUDITORIA
        ),
        **registro
    }
    nova_linha = pd.DataFrame([registro_auditoria])

    if caminho_auditoria.exists() and caminho_auditoria.stat().st_size > 0:
        try:
            historico = pd.read_excel(
                caminho_auditoria,
                sheet_name=configuracao_auditoria["aba"]
            )
        except ValueError:
            historico = pd.DataFrame()

        dados_auditoria = pd.concat(
            [historico, nova_linha],
            ignore_index=True
        )
    else:
        dados_auditoria = nova_linha

    dados_auditoria.to_excel(
        caminho_auditoria,
        sheet_name=configuracao_auditoria["aba"],
        index=False
    )
