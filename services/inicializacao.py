from pathlib import Path
from typing import Any

import pandas as pd

from core.caminhos import obter_caminho_arquivo, obter_caminho_pasta
from core.config import carregar_configuracoes


# Execucao mensal manual:
# 1. Ajuste "caminho_base" em config/configuracoes.json para a pasta do mes.
# 2. Execute no terminal, a partir da raiz do projeto:
#    python -m services.inicializacao

COLUNAS_AUDITORIA = [
    "data_hora",
    "status",
    "arquivo_entrada",
    "aba_entrada",
    "linhas_lidas",
    "colunas_lidas",
    "registros_p1",
    "novos_p1",
    "registros_rp1",
    "novos_rp1",
    "linhas_finais_p1",
    "linhas_finais_rp1",
    "backup_p1",
    "backup_rp1",
    "mensagem_erro",
]


def _criar_excel_se_nao_existir(
    caminho: Path,
    nome_aba: str,
    colunas: list[str],
) -> bool:
    if caminho.exists():
        return False

    caminho.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(columns=colunas).to_excel(
        caminho,
        sheet_name=nome_aba,
        index=False,
    )

    return True


def preparar_estrutura_operacional() -> dict[str, Any]:
    configuracoes = carregar_configuracoes()

    pastas_criadas = []
    arquivos_criados = []
    arquivos_existentes = []

    for nome_pasta in configuracoes["pastas"]:
        caminho_pasta = obter_caminho_pasta(nome_pasta)
        existia = caminho_pasta.exists()

        caminho_pasta.mkdir(parents=True, exist_ok=True)

        if not existia:
            pastas_criadas.append(str(caminho_pasta))

    arquivos_para_criar = {
        "destino_p1": configuracoes["colunas_destino"]["p1"],
        "destino_rp1": configuracoes["colunas_destino"]["rp1"],
        "auditoria": COLUNAS_AUDITORIA,
    }

    for nome_arquivo, colunas in arquivos_para_criar.items():
        configuracao_arquivo = configuracoes["arquivos"][nome_arquivo]
        caminho_arquivo = obter_caminho_arquivo(nome_arquivo)

        criado = _criar_excel_se_nao_existir(
            caminho=caminho_arquivo,
            nome_aba=configuracao_arquivo["aba"],
            colunas=colunas,
        )

        if criado:
            arquivos_criados.append(str(caminho_arquivo))
        else:
            arquivos_existentes.append(str(caminho_arquivo))

    caminho_entrada = obter_caminho_arquivo("entrada")

    return {
        "pastas_criadas": pastas_criadas,
        "arquivos_criados": arquivos_criados,
        "arquivos_existentes": arquivos_existentes,
        "arquivo_entrada_esperado": str(caminho_entrada),
        "arquivo_entrada_existe": caminho_entrada.exists(),
    }


if __name__ == "__main__":
    resumo = preparar_estrutura_operacional()

    print("Estrutura operacional preparada.")
    print(f"Pastas criadas: {len(resumo['pastas_criadas'])}")
    print(f"Arquivos criados: {len(resumo['arquivos_criados'])}")
    print(
        "Arquivo de entrada existe: "
        f"{'sim' if resumo['arquivo_entrada_existe'] else 'nao'}"
    )
    print(
        "Arquivo de entrada esperado: "
        f"{resumo['arquivo_entrada_esperado']}"
    )
