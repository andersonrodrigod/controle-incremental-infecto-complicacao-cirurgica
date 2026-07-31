# CLIs do projeto

Execute os comandos sempre pela raiz do projeto:

```powershell
cd C:\Users\anderson.dossantos\Desktop\dev\controle-incremental-infecto-complicacao-cirurgica
```

## 1. Preparar estrutura de pastas e arquivos

```powershell
python -m services.inicializacao
```

Use este comando antes de rodar os processamentos do mes/ano configurado.

Ele cria, se ainda nao existir:

- pastas principais dos fluxos;
- pasta `DATA`;
- pastas `DATA/backups/...`;
- pasta `DATA/logs`;
- arquivos Excel de destino vazios;
- arquivos Excel de auditoria.

Ele nao cria o arquivo de entrada `COMPLICACAO JUNHO.xlsx`. Esse arquivo precisa ser colocado manualmente na pasta esperada.

Ele tambem nao sobrescreve arquivos que ja existem.

Estrutura atual configurada:

```text
Complicacoes Cirurgicas/
  INFECTO/
    2026/
      JUNHO/
        COMPLICACAO JUNHO.xlsx
        2026 JUNHO PESQUISA DE COMPLICACAO INF - 30 DIAS.xlsx
        2026 JUNHO PESQUISA DE COMPLICACAO INF - 60 DIAS.xlsx
        DATA/
          auditoria_execucoes_p1.xlsx
          auditoria_execucoes_rp1.xlsx
          backups/
            p1/
            rp1/
          logs/

  INFECTO SCIRAS/
    2026/
      JUNHO/
        COMPLICACAO JUNHO.xlsx
        2026 JUNHO PESQUISA DE COMPLICACAO INF - 30 DIAS SCIRAS.xlsx
        DATA/
          auditoria_execucoes_p1_sciras.xlsx
          backups/
            p1_sciras/
          logs/
```

## 2. Executar todos os fluxos

```powershell
python main.py
```

Executa os tres fluxos configurados:

- `p1`: 30 dias;
- `rp1`: 60 dias;
- `p1_sciras`: 30 dias SCIRAS.

Use quando quiser atualizar tudo de uma vez.

Antes de executar, confira se existem os arquivos de entrada:

```text
INFECTO/2026/JUNHO/COMPLICACAO JUNHO.xlsx
INFECTO SCIRAS/2026/JUNHO/COMPLICACAO JUNHO.xlsx
```

## 3. Executar somente 30 dias

```powershell
python -m cli.executar_30_dias
```

Executa apenas o fluxo `p1`.

Entrada esperada:

```text
INFECTO/2026/JUNHO/COMPLICACAO JUNHO.xlsx
```

Saida atualizada:

```text
INFECTO/2026/JUNHO/2026 JUNHO PESQUISA DE COMPLICACAO INF - 30 DIAS.xlsx
```

## 4. Executar somente 60 dias

```powershell
python -m cli.executar_60_dias
```

Executa apenas o fluxo `rp1`.

Entrada esperada:

```text
INFECTO/2026/JUNHO/COMPLICACAO JUNHO.xlsx
```

Saida atualizada:

```text
INFECTO/2026/JUNHO/2026 JUNHO PESQUISA DE COMPLICACAO INF - 60 DIAS.xlsx
```

## 5. Executar somente 30 dias SCIRAS

```powershell
python -m cli.executar_30_dias_p1_sciras
```

Executa apenas o fluxo `p1_sciras`.

Entrada esperada:

```text
INFECTO SCIRAS/2026/JUNHO/COMPLICACAO JUNHO.xlsx
```

Saida atualizada:

```text
INFECTO SCIRAS/2026/JUNHO/2026 JUNHO PESQUISA DE COMPLICACAO INF - 30 DIAS SCIRAS.xlsx
```

## Ordem recomendada

```powershell
python -m services.inicializacao
python -m cli.executar_30_dias
python -m cli.executar_60_dias
python -m cli.executar_30_dias_p1_sciras
```

Ou, se quiser rodar tudo de uma vez depois da inicializacao:

```powershell
python -m services.inicializacao
python main.py
```

## Observacoes importantes

- Os comandos devem ser executados com os arquivos Excel fechados.
- Antes de atualizar uma saida existente, o pipeline cria backup em `DATA/backups/...`.
- Cada fluxo registra auditoria no arquivo correspondente dentro de `DATA`.
- Os logs ficam em `DATA/logs`.
- Para virar mes ou ano, altere primeiro os caminhos e nomes em `config/configuracoes.json`.
