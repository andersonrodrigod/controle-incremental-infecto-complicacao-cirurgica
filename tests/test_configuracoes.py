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

    for nome_fluxo in ("p1", "p1_sciras", "rp1"):
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

    for nome_fluxo in ("p1", "p1_sciras", "rp1"):
        caminho = obter_caminho_pasta_fluxo(nome_fluxo, "backups")
        configuracao_caminho = configuracoes["fluxos"][nome_fluxo][
            "backups"
        ]

        assert caminho == (
            Path(configuracao_caminho["caminho_base"])
            / configuracao_caminho["pasta"]
        )


def test_estrutura_criacao_por_fluxos():
    configuracoes = carregar_configuracoes()
    estrutura = configuracoes["estrutura_criacao"]

    assert estrutura["por_fluxos"] is True


def test_fluxos_configurados_usam_arvores_infecto_e_sciras():
    configuracoes = carregar_configuracoes()
    fluxos = configuracoes["fluxos"]

    assert "INFECTO/2026/JUNHO" in fluxos["p1"]["destino"]["caminho_base"]
    assert "INFECTO/2026/JUNHO" in fluxos["rp1"]["destino"]["caminho_base"]
    assert (
        "INFECTO SCIRAS/2026/JUNHO"
        in fluxos["p1_sciras"]["destino"]["caminho_base"]
    )
    assert "INFECTO SCIRAS" not in fluxos["p1"]["destino"]["caminho_base"]
    assert "INFECTO SCIRAS" not in fluxos["rp1"]["destino"]["caminho_base"]


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


def test_coluna_auditoria_medica_esta_na_posicao_configurada():
    configuracoes = carregar_configuracoes()
    colunas_p1 = configuracoes["colunas_destino"]["p1"]
    colunas_p1_sciras = configuracoes["colunas_destino"]["p1_sciras"]
    colunas_rp1 = configuracoes["colunas_destino"]["rp1"]

    assert colunas_p1.index("AUDITORIA MEDICA") == (
        colunas_p1.index("P2") + 1
    )
    assert colunas_p1_sciras.index("AUDITORIA MEDICA") == (
        colunas_p1_sciras.index("P2") + 1
    )
    assert colunas_rp1.index("AUDITORIA MEDICA") == (
        colunas_rp1.index("RP1") + 1
    )


def test_auditoria_medica_e_coluna_manual_dos_fluxos():
    configuracoes = carregar_configuracoes()

    assert "AUDITORIA MEDICA" in configuracoes["colunas_manuais"]["p1"]
    assert (
        "AUDITORIA MEDICA"
        in configuracoes["colunas_manuais"]["p1_sciras"]
    )
    assert "AUDITORIA MEDICA" in configuracoes["colunas_manuais"]["rp1"]


def test_resolver_caminho_base_relativo_usa_raiz_do_projeto():
    assert resolver_caminho_base("data") == RAIZ_PROJETO / "data"
