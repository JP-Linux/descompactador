# Descompactador de arquivos

Este é um script Python que permite descompactar arquivos com extensões `.zip`, `.tar.gz`, `.tar.bz2` e `.tar.xz`. Ele utiliza a biblioteca `os` para interagir com o sistema operacional e executar os comandos necessários para a descompactação.

## Como usar

Para usar o script, você pode executá-lo na linha de comando e passar o nome do arquivo a ser descompactado como argumento:

```sh
$ python3 descompactador.py arquivo.zip
```

O script detectará automaticamente a extensão do arquivo e executará o comando adequado para a descompactação.

## Exemplos

Descompactar um arquivo `.zip`:

```bash
$ python descompactador.py arquivo.zip
```

Descompactar um arquivo `.tar.gz`:

```bash
$ python descompactador.py arquivo.tar.gz
```

Descompactar um arquivo `.tar.bz2`:

```bash
$ python descompactador.py arquivo.tar.bz2
```

Descompactar um arquivo `.tar.xz`:

```bash
$ python descompactador.py arquivo.tar.xz
```