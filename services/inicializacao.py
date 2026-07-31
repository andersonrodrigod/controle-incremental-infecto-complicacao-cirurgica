from pathlib import Path
from typing import Any

import pandas as pd

from core.caminhos import (
    obter_caminho_fluxo,
    obter_caminho_pasta_fluxo,
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
    "arquivo_entrada_p1_sciras",
    "aba_entrada_p1_sciras",
    "linhas_lidas_p1_sciras",
    "colunas_lidas_p1_sciras",
    "registros_p1",
    "novos_p1",
    "registros_rp1",
    "novos_rp1",
    "registros_p1_sciras",
    "novos_p1_sciras",
    "linhas_finais_p1",
    "linhas_finais_rp1",
    "linhas_finais_p1_sciras",
    "backup_p1",
    "backup_rp1",
    "backup_p1_sciras",
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


def _colunas_destino_para_saida(
    configuracoes: dict[str, Any],
    nome_fluxo: str,
) -> list[str]:
    colunas = configuracoes["colunas_destino"][nome_fluxo]
    renomear_colunas = configuracoes.get("renomear_colunas", {}).get(
        nome_fluxo,
        {},
    )

    return [
        renomear_colunas.get(coluna, coluna)
        for coluna in colunas
    ]


def preparar_estrutura_operacional() -> dict[str, Any]:
    configuracoes = carregar_configuracoes()

    pastas_criadas = []
    arquivos_criados = []
    arquivos_existentes = []

    estrutura_criacao = configuracoes["estrutura_criacao"]

    if estrutura_criacao.get("por_fluxos"):
        return _preparar_estrutura_por_fluxos(
            configuracoes=configuracoes,
            pastas_criadas=pastas_criadas,
            arquivos_criados=arquivos_criados,
            arquivos_existentes=arquivos_existentes,
        )

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
            _colunas_destino_para_saida(configuracoes, chave_colunas)
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

    caminhos_entrada = {
        nome_fluxo: obter_caminho_fluxo(nome_fluxo, "entrada")
        for nome_fluxo in configuracoes["fluxos"]
    }
    caminho_entrada_padrao = (
        caminhos_entrada.get("p1")
        or next(iter(caminhos_entrada.values()))
    )

    resumo = {
        "pastas_criadas": pastas_criadas,
        "arquivos_criados": arquivos_criados,
        "arquivos_existentes": arquivos_existentes,
        "arquivo_entrada_esperado": str(caminho_entrada_padrao),
        "arquivo_entrada_existe": caminho_entrada_padrao.exists(),
    }

    for nome_fluxo, caminho_entrada in caminhos_entrada.items():
        resumo[f"arquivo_entrada_{nome_fluxo}_esperado"] = str(
            caminho_entrada
        )
        resumo[f"arquivo_entrada_{nome_fluxo}_existe"] = (
            caminho_entrada.exists()
        )

    return resumo


def _preparar_estrutura_por_fluxos(
    configuracoes: dict[str, Any],
    pastas_criadas: list[str],
    arquivos_criados: list[str],
    arquivos_existentes: list[str],
) -> dict[str, Any]:
    for nome_fluxo, fluxo in configuracoes["fluxos"].items():
        caminho_destino = obter_caminho_fluxo(nome_fluxo, "destino")
        chave_colunas = fluxo["destino"].get("colunas_destino", nome_fluxo)

        _registrar_pasta(
            caminho=caminho_destino.parent,
            pastas_criadas=pastas_criadas,
        )

        criado = _criar_excel_se_nao_existir(
            caminho=caminho_destino,
            nome_aba=fluxo["destino"]["aba"],
            colunas=_colunas_destino_para_saida(
                configuracoes,
                chave_colunas,
            ),
        )
        _registrar_arquivo(
            caminho=caminho_destino,
            criado=criado,
            arquivos_criados=arquivos_criados,
            arquivos_existentes=arquivos_existentes,
        )

        caminho_auditoria = obter_caminho_fluxo(nome_fluxo, "auditoria")
        _registrar_pasta(
            caminho=caminho_auditoria.parent,
            pastas_criadas=pastas_criadas,
        )

        criado = _criar_excel_se_nao_existir(
            caminho=caminho_auditoria,
            nome_aba=fluxo["auditoria"]["aba"],
            colunas=COLUNAS_AUDITORIA,
        )
        _registrar_arquivo(
            caminho=caminho_auditoria,
            criado=criado,
            arquivos_criados=arquivos_criados,
            arquivos_existentes=arquivos_existentes,
        )

        _registrar_pasta(
            caminho=obter_caminho_pasta_fluxo(nome_fluxo, "backups"),
            pastas_criadas=pastas_criadas,
        )
        _registrar_pasta(
            caminho=obter_caminho_fluxo(nome_fluxo, "log").parent,
            pastas_criadas=pastas_criadas,
        )

    return _criar_resumo_inicializacao(
        configuracoes=configuracoes,
        pastas_criadas=pastas_criadas,
        arquivos_criados=arquivos_criados,
        arquivos_existentes=arquivos_existentes,
    )


def _registrar_pasta(
    caminho: Path,
    pastas_criadas: list[str],
) -> None:
    existia = caminho.exists()
    caminho.mkdir(parents=True, exist_ok=True)

    if not existia:
        pastas_criadas.append(str(caminho))


def _registrar_arquivo(
    caminho: Path,
    criado: bool,
    arquivos_criados: list[str],
    arquivos_existentes: list[str],
) -> None:
    if criado:
        arquivos_criados.append(str(caminho))
    else:
        arquivos_existentes.append(str(caminho))


def _criar_resumo_inicializacao(
    configuracoes: dict[str, Any],
    pastas_criadas: list[str],
    arquivos_criados: list[str],
    arquivos_existentes: list[str],
) -> dict[str, Any]:
    caminhos_entrada = {
        nome_fluxo: obter_caminho_fluxo(nome_fluxo, "entrada")
        for nome_fluxo in configuracoes["fluxos"]
    }
    caminho_entrada_padrao = (
        caminhos_entrada.get("p1")
        or next(iter(caminhos_entrada.values()))
    )

    resumo = {
        "pastas_criadas": pastas_criadas,
        "arquivos_criados": arquivos_criados,
        "arquivos_existentes": arquivos_existentes,
        "arquivo_entrada_esperado": str(caminho_entrada_padrao),
        "arquivo_entrada_existe": caminho_entrada_padrao.exists(),
    }

    for nome_fluxo, caminho_entrada in caminhos_entrada.items():
        resumo[f"arquivo_entrada_{nome_fluxo}_esperado"] = str(
            caminho_entrada
        )
        resumo[f"arquivo_entrada_{nome_fluxo}_existe"] = (
            caminho_entrada.exists()
        )

    return resumo


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
