from cli import executor
from cli import executar_30_dias, executar_30_dias_p1_sciras, executar_60_dias


def test_cli_30_dias_executa_somente_fluxo_p1(monkeypatch):
    fluxos_executados = []

    monkeypatch.setattr(executor, "configurar_logging", lambda: None)
    monkeypatch.setattr(
        executor,
        "executar_pipeline",
        lambda nomes_fluxos: fluxos_executados.extend(nomes_fluxos),
    )

    executar_30_dias.main()

    assert fluxos_executados == ["p1"]


def test_cli_60_dias_executa_somente_fluxo_rp1(monkeypatch):
    fluxos_executados = []

    monkeypatch.setattr(executor, "configurar_logging", lambda: None)
    monkeypatch.setattr(
        executor,
        "executar_pipeline",
        lambda nomes_fluxos: fluxos_executados.extend(nomes_fluxos),
    )

    executar_60_dias.main()

    assert fluxos_executados == ["rp1"]


def test_cli_30_dias_sciras_executa_somente_fluxo_p1_sciras(monkeypatch):
    fluxos_executados = []

    monkeypatch.setattr(executor, "configurar_logging", lambda: None)
    monkeypatch.setattr(
        executor,
        "executar_pipeline",
        lambda nomes_fluxos: fluxos_executados.extend(nomes_fluxos),
    )

    executar_30_dias_p1_sciras.main()

    assert fluxos_executados == ["p1_sciras"]
