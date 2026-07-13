import json
from pathlib import Path

from core.caminhos import (
    obter_caminho_fluxo,
    obter_caminho_pasta_fluxo,
    resolver_caminho_base,
)
from core.config import RAIZ_PROJETO, carregar_configuracoes


def test_fluxos_configurados_resolvem_caminhos_operacionais():
    configuracoes = carregar_configuracoes()

    for nome_fluxo in ("p1", "rp1"):
        fluxo = configuracoes["fluxos"][nome_fluxo]

        for tipo_caminho in ("entrada", "destino", "auditoria", "log"):
            caminho = obter_caminho_fluxo(nome_fluxo, tipo_caminho)
            configuracao_caminho = fluxo[tipo_caminho]

            assert caminho.name == configuracao_caminho["nome"]
            assert caminho.parent == (
                Path(configuracao_caminho["caminho_base"])
                / configuracao_caminho["pasta"]
            )


def test_fluxos_configurados_resolvem_pastas_de_backup():
    configuracoes = carregar_configuracoes()

    for nome_fluxo in ("p1", "rp1"):
        caminho = obter_caminho_pasta_fluxo(nome_fluxo, "backups")
        configuracao_caminho = configuracoes["fluxos"][nome_fluxo][
            "backups"
        ]

        assert caminho == (
            Path(configuracao_caminho["caminho_base"])
            / configuracao_caminho["pasta"]
        )


def test_estrutura_criacao_define_pasta_arquivos_e_subpastas():
    configuracoes = carregar_configuracoes()
    estrutura = configuracoes["estrutura_criacao"]
    caminho_base = resolver_caminho_base(estrutura["caminho_base"])
    pasta_principal = caminho_base / estrutura["pasta"]

    assert estrutura["pasta"] == "data"
    assert not Path(estrutura["pasta"]).is_absolute()

    for caminho_relativo in estrutura["pastas"].values():
        assert not Path(caminho_relativo).is_absolute()
        assert (pasta_principal / caminho_relativo).is_relative_to(
            pasta_principal
        )

    assert {
        "controle_30_dias",
        "controle_60_dias",
        "auditoria",
    }.issubset(estrutura["arquivos"])


def test_configuracao_nao_usa_blocos_antigos_de_caminho():
    configuracoes = carregar_configuracoes()

    assert "caminho_base" not in configuracoes
    assert "pastas" not in configuracoes
    assert "arquivos" not in configuracoes


def test_configuracao_principal_nao_guarda_esquemas_operacionais():
    caminho_configuracao = RAIZ_PROJETO / "config" / "configuracoes.json"
    configuracao_principal = json.loads(
        caminho_configuracao.read_text(encoding="utf-8")
    )

    for chave in (
        "colunas_manuais",
        "schema_colunas",
        "colunas_obrigatorias",
        "colunas_destino",
        "regras_processamento",
        "mapear_valores",
        "renomear_colunas",
    ):
        assert chave not in configuracao_principal


def test_carregar_configuracoes_mescla_esquemas_operacionais():
    configuracoes = carregar_configuracoes()

    for chave in (
        "colunas_manuais",
        "schema_colunas",
        "colunas_obrigatorias",
        "colunas_destino",
        "regras_processamento",
        "mapear_valores",
        "renomear_colunas",
    ):
        assert chave in configuracoes


def test_colunas_destino_estao_contidas_nas_colunas_obrigatorias():
    configuracoes = carregar_configuracoes()
    colunas_obrigatorias = set(configuracoes["colunas_obrigatorias"])

    for colunas_destino in configuracoes["colunas_destino"].values():
        assert set(colunas_destino).issubset(colunas_obrigatorias)


def test_resolver_caminho_base_relativo_usa_raiz_do_projeto():
    assert resolver_caminho_base("data") == RAIZ_PROJETO / "data"
