from pathlib import Path

from core.caminhos import (
    obter_caminho_base,
    obter_caminho_arquivo,
    obter_caminho_log,
    obter_caminho_pasta,
)
from core.config import RAIZ_PROJETO, carregar_configuracoes


def test_pastas_configuradas_existem_no_workspace():
    configuracoes = carregar_configuracoes()

    for nome_pasta in configuracoes["pastas"]:
        caminho = obter_caminho_pasta(nome_pasta)

        assert caminho == obter_caminho_base() / configuracoes["pastas"][nome_pasta]
        assert caminho.exists()
        assert caminho.is_dir()


def test_arquivos_configurados_ficam_nas_pastas_esperadas():
    configuracoes = carregar_configuracoes()

    casos = {
        "entrada": "entrada",
        "destino_p1": "destino",
        "destino_rp1": "destino",
        "auditoria": "auditoria",
    }

    for nome_arquivo, nome_pasta in casos.items():
        caminho_arquivo = obter_caminho_arquivo(nome_arquivo)
        pasta_esperada = obter_caminho_pasta(nome_pasta)
        nome_esperado = configuracoes["arquivos"][nome_arquivo]["nome"]

        assert caminho_arquivo.parent == pasta_esperada
        assert caminho_arquivo.name == nome_esperado


def test_arquivos_operacionais_existentes_batem_com_json_local():
    arquivos_obrigatorios = [
        "entrada",
        "destino_p1",
        "destino_rp1",
        "auditoria",
    ]

    for nome_arquivo in arquivos_obrigatorios:
        caminho_arquivo = obter_caminho_arquivo(nome_arquivo)

        assert caminho_arquivo.exists(), (
            f"Arquivo configurado nao encontrado: {caminho_arquivo}"
        )
        assert caminho_arquivo.is_file()


def test_colunas_destino_estao_contidas_nas_colunas_obrigatorias():
    configuracoes = carregar_configuracoes()
    colunas_obrigatorias = set(configuracoes["colunas_obrigatorias"])

    for colunas_destino in configuracoes["colunas_destino"].values():
        assert set(colunas_destino).issubset(colunas_obrigatorias)


def test_pastas_configuradas_continuam_relativas_ao_caminho_base():
    configuracoes = carregar_configuracoes()

    for caminho_relativo in configuracoes["pastas"].values():
        assert not Path(caminho_relativo).is_absolute()


def test_caminho_base_configurado_resolve_para_raiz_operacional():
    configuracoes = carregar_configuracoes()
    caminho_base = Path(configuracoes["caminho_base"])

    if caminho_base.is_absolute():
        assert obter_caminho_base() == caminho_base
    else:
        assert obter_caminho_base() == RAIZ_PROJETO / caminho_base


def test_caminho_log_usa_pasta_e_arquivo_configurados_no_json():
    configuracoes = carregar_configuracoes()

    caminho_log = obter_caminho_log()

    assert caminho_log == (
        obter_caminho_base()
        / configuracoes["pastas"]["logs"]
        / configuracoes["arquivos"]["log"]["nome"]
    )
