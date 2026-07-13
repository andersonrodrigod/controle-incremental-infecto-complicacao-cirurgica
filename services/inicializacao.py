from pathlib import Path
from typing import Any

import pandas as pd

from core.caminhos import (
    obter_caminho_fluxo,
    resolver_caminho_base,
)
from core.config import carregar_configuracoes


COLUNAS_AUDITORIA = [
    "data_hora",
    "fluxo",
    "status",
    "arquivo_entrada",
    "aba_entrada",
    "linhas_lidas",
    "colunas_lidas",
    "arquivo_entrada_p1",
    "aba_entrada_p1",
    "linhas_lidas_p1",
    "colunas_lidas_p1",
    "arquivo_entrada_rp1",
    "aba_entrada_rp1",
    "linhas_lidas_rp1",
    "colunas_lidas_rp1",
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

    estrutura_criacao = configuracoes["estrutura_criacao"]
    caminho_base_criacao = resolver_caminho_base(
        estrutura_criacao["caminho_base"]
    )
    caminho_pasta_principal = (
        caminho_base_criacao / estrutura_criacao.get("pasta", "")
    )
    existia = caminho_pasta_principal.exists()

    caminho_pasta_principal.mkdir(parents=True, exist_ok=True)

    if not existia:
        pastas_criadas.append(str(caminho_pasta_principal))

    for caminho_relativo in estrutura_criacao.get("pastas", {}).values():
        caminho_pasta = caminho_pasta_principal / caminho_relativo
        existia = caminho_pasta.exists()

        caminho_pasta.mkdir(parents=True, exist_ok=True)

        if not existia:
            pastas_criadas.append(str(caminho_pasta))

    arquivos_para_criar = []

    for configuracao_arquivo in estrutura_criacao["arquivos"].values():
        caminho_arquivo = (
            caminho_pasta_principal / configuracao_arquivo["nome"]
        )
        chave_colunas = configuracao_arquivo.get("colunas_destino")
        colunas = (
            configuracoes["colunas_destino"][chave_colunas]
            if chave_colunas
            else COLUNAS_AUDITORIA
        )
        arquivos_para_criar.append(
            (configuracao_arquivo, caminho_arquivo, colunas)
        )

    for configuracao_arquivo, caminho_arquivo, colunas in arquivos_para_criar:

        criado = _criar_excel_se_nao_existir(
            caminho=caminho_arquivo,
            nome_aba=configuracao_arquivo["aba"],
            colunas=colunas,
        )

        if criado:
            arquivos_criados.append(str(caminho_arquivo))
        else:
            arquivos_existentes.append(str(caminho_arquivo))

    caminho_entrada_p1 = obter_caminho_fluxo("p1", "entrada")
    caminho_entrada_rp1 = obter_caminho_fluxo("rp1", "entrada")

    return {
        "pastas_criadas": pastas_criadas,
        "arquivos_criados": arquivos_criados,
        "arquivos_existentes": arquivos_existentes,
        "arquivo_entrada_esperado": str(caminho_entrada_p1),
        "arquivo_entrada_existe": caminho_entrada_p1.exists(),
        "arquivo_entrada_p1_esperado": str(caminho_entrada_p1),
        "arquivo_entrada_p1_existe": caminho_entrada_p1.exists(),
        "arquivo_entrada_rp1_esperado": str(caminho_entrada_rp1),
        "arquivo_entrada_rp1_existe": caminho_entrada_rp1.exists(),
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
