#!/usr/bin/env python3
"""
Módulo profissional para descompactação de arquivos usando bibliotecas nativas do Python.
"""

import logging
import zipfile
import tarfile
from pathlib import Path
import sys

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class ErroArquivo(Exception):
    """Exceção base para erros de arquivo"""
    pass


class ArquivoInvalidoError(ErroArquivo):
    """Exceção para arquivos inválidos ou corrompidos"""
    pass


class FormatoNaoSuportadoError(ErroArquivo):
    """Exceção para formatos não suportados"""
    pass


class Descompactador:
    """
    Classe para descompactação de arquivos com suporte para:
    .zip, .tar.gz, .tar.bz2, .tar.xz

    Uso:
    ```python
    descompactador = Descompactador("arquivo.zip")
    descompactador.extrair()
    ```
    """

    FORMATOS_SUPORTADOS = ('.zip', '.tar.gz', '.tar.bz2', '.tar.xz')

    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho_arquivo = Path(caminho_arquivo).resolve()
        self._validar_arquivo()

    def _validar_arquivo(self) -> None:
        """Validação inicial do arquivo"""
        if not self.caminho_arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")

        if not self.caminho_arquivo.is_file():
            raise ArquivoInvalidoError(f"Caminho não é um arquivo: {self.caminho_arquivo}")

        if self.caminho_arquivo.stat().st_size == 0:
            raise ArquivoInvalidoError(f"Arquivo vazio: {self.caminho_arquivo}")

    def _detectar_formato(self) -> str:
        """Detecta o formato do arquivo usando sufixos"""
        sufixos = self.caminho_arquivo.suffixes
        
        # Verifica combinações de sufixos conhecidos
        if len(sufixos) >= 2:
            combinado = ''.join(sufixos[-2:])
            if combinado in self.FORMATOS_SUPORTADOS:
                return combinado

        # Verifica sufixo único
        if sufixos and sufixos[-1] in self.FORMATOS_SUPORTADOS:
            return sufixos[-1]

        raise FormatoNaoSuportadoError(
            f"Formato não suportado: {self.caminho_arquivo}. "
            f"Formatos suportados: {', '.join(self.FORMATOS_SUPORTADOS)}"
        )

    def extrair(self, diretorio_saida: str = None) -> None:
        """
        Descompacta o arquivo para o diretório especificado

        :param diretorio_saida: Diretório de saída (usa o diretório atual se não especificado)
        """
        caminho_saida = Path(diretorio_saida).resolve() if diretorio_saida else Path.cwd()
        caminho_saida.mkdir(parents=True, exist_ok=True)

        formato = self._detectar_formato()
        logging.info(f"Iniciando extração de {self.caminho_arquivo} para {caminho_saida}")

        try:
            if formato == '.zip':
                self._extrair_zip(caminho_saida)
            else:
                self._extrair_tar(formato, caminho_saida)
        except Exception as e:
            logging.error(f"Falha na extração: {str(e)}")
            raise ErroArquivo("Erro durante a extração") from e

    def _extrair_zip(self, diretorio_saida: Path) -> None:
        """Método interno para extração de ZIP"""
        try:
            with zipfile.ZipFile(self.caminho_arquivo) as arquivo_zip:
                arquivo_zip.testzip()  # Verifica integridade do arquivo
                arquivo_zip.extractall(diretorio_saida)
        except zipfile.BadZipFile as e:
            raise ArquivoInvalidoError("Arquivo ZIP inválido ou corrompido") from e

    def _extrair_tar(self, formato: str, diretorio_saida: Path) -> None:
        """Método interno para extração de TAR com diferentes compressões"""
        mapeamento_compressao = {
            '.tar.gz': 'gz',
            '.tar.bz2': 'bz2',
            '.tar.xz': 'xz'
        }
        modo = f'r:{mapeamento_compressao[formato]}'

        try:
            with tarfile.open(self.caminho_arquivo, modo) as arquivo_tar:
                arquivo_tar.extractall(diretorio_saida)
        except tarfile.ReadError as e:
            raise ArquivoInvalidoError("Arquivo TAR inválido ou corrompido") from e


def principal():
    """Função principal para uso via CLI"""
    if len(sys.argv) not in (2, 3):
        print(f"Uso: {sys.argv[0]} <arquivo> [diretório_saida]")
        sys.exit(1)

    try:
        descompactador = Descompactador(sys.argv[1])
        descompactador.extrair(sys.argv[2] if len(sys.argv) == 3 else None)
        logging.info("Extração concluída com sucesso")
    except ErroArquivo as e:
        logging.error(f"Erro: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.warning("Extração interrompida pelo usuário")
        sys.exit(130)


if __name__ == "__main__":
    principal()