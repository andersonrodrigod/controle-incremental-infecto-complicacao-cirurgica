from services.pipeline import executar_pipeline


def main() -> None:
    print("Iniciando controle incremental...")
    executar_pipeline()
    print("Execução finalizada.")

if __name__ == "__main__":
    main()