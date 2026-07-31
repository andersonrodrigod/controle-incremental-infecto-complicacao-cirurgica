from copy import deepcopy

import pandas as pd

from core import caminhos
from core.config import carregar_configuracoes as carregar_configuracoes_real
from services import auditoria, inicializacao, pipeline


def _remapear_configuracao_para_tmp(tmp_path):
    configuracoes = deepcopy(carregar_configuracoes_real())

    estrutura = configuracoes["estrutura_criacao"]
    if "caminho_base" in estrutura:
        estrutura["caminho_base"] = str(tmp_path / "estrutura")

    for nome_fluxo, fluxo in configuracoes["fluxos"].items():
        for tipo_caminho, configuracao_caminho in fluxo.items():
            if "caminho_base" in configuracao_caminho:
                configuracao_caminho["caminho_base"] = str(
                    tmp_path / "fluxos" / nome_fluxo
                )

    return configuracoes


def _aplicar_configuracoes(monkeypatch, configuracoes):
    for modulo in (auditoria, caminhos, inicializacao, pipeline):
        monkeypatch.setattr(
            modulo,
            "carregar_configuracoes",
            lambda: configuracoes,
        )


def _linha_entrada(configuracoes, senha, usuario):
    linha = {
        coluna: ""
        for coluna in configuracoes["colunas_obrigatorias"]
    }
    linha.update(
        {
            "FILIAL": "FILIAL TESTE",
            "SENHA": senha,
            "COD USUARIO": f"COD-{senha}",
            "USUARIO": usuario,
            "PRESTADOR": "PRESTADOR TESTE",
            "PROCEDIMENTO": "PROCEDIMENTO TESTE",
            "DT ENVIO": "2026-07-31",
            "DT INTERNACAO": "2026-07-01",
            "DATA DE ENVIO": "",
            "P1": "Sim",
            "P2": "Sim",
            "RP1": "",
            "LIGACAO EFETIVADA": "Sim",
            "TP ATENDIMENTO": "Internacao",
            "UF": "CE",
            "DISTRITO": "Fortaleza",
            "TELEFONE 1": "5585999999999",
            "TELEFONE 2": "",
            "TELEFONE 3": "",
            "TELEFONE 4": "",
            "TELEFONE 5": "",
            "TIPO": "VIDEO ABDOMINAL",
        }
    )

    linha["RP1 NÂº"] = 1

    return linha


def _colunas_saida(configuracoes, nome_fluxo):
    renomear = configuracoes["renomear_colunas"][nome_fluxo]

    return [
        renomear.get(coluna, coluna)
        for coluna in configuracoes["colunas_destino"][nome_fluxo]
    ]


def test_inicializacao_com_config_referenciada_cria_apenas_em_tmp(
    monkeypatch,
    tmp_path,
):
    configuracoes = _remapear_configuracao_para_tmp(tmp_path)
    _aplicar_configuracoes(monkeypatch, configuracoes)

    resumo = inicializacao.preparar_estrutura_operacional()

    estrutura = configuracoes["estrutura_criacao"]
    pasta_principal = (
        tmp_path / "estrutura" / estrutura.get("pasta", "")
    )
    arquivo_destino = (
        pasta_principal
        / estrutura["arquivos"]["controle_30_dias"]["nome"]
    )
    arquivo_entrada_fluxo = caminhos.obter_caminho_fluxo("p1", "entrada")

    assert arquivo_destino.exists()
    assert not arquivo_entrada_fluxo.exists()
    assert all(str(caminho).startswith(str(tmp_path)) for caminho in (
        resumo["pastas_criadas"] + resumo["arquivos_criados"]
    ))

    destino = pd.read_excel(arquivo_destino, sheet_name="BASE")
    assert destino.columns.tolist() == _colunas_saida(configuracoes, "p1")


def test_pipeline_atualiza_copia_temporaria_sem_alterar_referencias(
    monkeypatch,
    tmp_path,
):
    configuracoes = _remapear_configuracao_para_tmp(tmp_path)
    _aplicar_configuracoes(monkeypatch, configuracoes)

    caminho_entrada = caminhos.obter_caminho_fluxo("p1", "entrada")
    caminho_destino = caminhos.obter_caminho_fluxo("p1", "destino")
    caminho_auditoria = caminhos.obter_caminho_fluxo("p1", "auditoria")
    caminho_backups = caminhos.obter_caminho_pasta_fluxo("p1", "backups")

    caminho_entrada.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            _linha_entrada(configuracoes, "100", "Maria atualizada"),
            _linha_entrada(configuracoes, "101", "Joao novo"),
        ]
    ).to_excel(caminho_entrada, sheet_name="BASE", index=False)

    colunas_saida = _colunas_saida(configuracoes, "p1")
    linha_historico = {
        coluna: ""
        for coluna in colunas_saida
    }
    linha_historico.update(
        {
            "SENHA": "100",
            "USUARIO": "Maria manual",
            "AUDITORIA MEDICA": "revisado manualmente",
        }
    )
    caminho_destino.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([linha_historico], columns=colunas_saida).to_excel(
        caminho_destino,
        sheet_name="BASE",
        index=False,
    )

    resumo = pipeline.executar_pipeline(nomes_fluxos=("p1",))

    resultado = pd.read_excel(caminho_destino, sheet_name="BASE")
    senhas = resultado["SENHA"].astype("string").tolist()

    assert senhas == ["100", "101"]
    assert resultado.loc[0, "USUARIO"] == "Maria manual"
    assert resultado.loc[0, "AUDITORIA MEDICA"] == "revisado manualmente"
    assert resultado.loc[1, "USUARIO"] == "Joao novo"
    assert resumo["novos_p1"] == 1
    assert caminho_auditoria.exists()
    assert list(caminho_backups.glob("*.xlsx"))

