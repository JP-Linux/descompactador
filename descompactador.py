#!/usr/bin/env python3
"""
Módulo profissional para descompactação segura de arquivos usando bibliotecas nativas do Python.
Suporta: .zip, .tar, .tar.gz, .tar.bz2, .tar.xz
"""

import logging
import zipfile
import tarfile
import os
import sys
from pathlib import Path
import shutil

# Configuração avançada de logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('descompactador.log', encoding='utf-8')
    ]
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
    Classe para descompactação segura de arquivos com:
    - Verificação de integridade
    - Prevenção contra path traversal
    - Suporte para .zip, .tar, .tar.gz, .tar.bz2, .tar.xz

    Uso:
    ```python
    descompactador = Descompactador("arquivo.zip")
    descompactador.extrair(destino="/caminho/seguro")
    ```
    """

    FORMATOS_SUPORTADOS = ('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz')

    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho_arquivo = Path(caminho_arquivo).resolve()
        self._validar_arquivo()
        self.formato = self._detectar_formato()

    def _validar_arquivo(self) -> None:
        """Validação rigorosa do arquivo"""
        if not self.caminho_arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")

        if not self.caminho_arquivo.is_file():
            raise ArquivoInvalidoError(f"Caminho não é um arquivo: {self.caminho_arquivo}")

        if self.caminho_arquivo.stat().st_size == 0:
            raise ArquivoInvalidoError(f"Arquivo vazio: {self.caminho_arquivo}")

        # Verificação adicional de permissões
        if not os.access(self.caminho_arquivo, os.R_OK):
            raise PermissionError(f"Permissão negada para ler o arquivo: {self.caminho_arquivo}")

    def _detectar_formato(self) -> str:
        """Detecta o formato do arquivo com prioridade para combinações"""
        sufixos = self.caminho_arquivo.suffixes

        # Combinações de sufixos (ex: .tar.gz)
        if len(sufixos) >= 2:
            for i in range(len(sufixos)-1):
                combinado = ''.join(sufixos[i:])
                if combinado in self.FORMATOS_SUPORTADOS:
                    return combinado

        # Sufixo único
        if sufixos:
            ultimo_sufixo = sufixos[-1]
            if ultimo_sufixo in self.FORMATOS_SUPORTADOS:
                return ultimo_sufixo

        raise FormatoNaoSuportadoError(
            f"Formato não suportado: {self.caminho_arquivo}. "
            f"Formatos suportados: {', '.join(self.FORMATOS_SUPORTADOS)}"
        )

    def extrair(self, diretorio_saida: str = None) -> None:
        """
        Descompacta o arquivo de forma segura para o diretório especificado

        :param diretorio_saida: Diretório de saída (padrão: diretório atual)
        """
        caminho_saida = Path(diretorio_saida).resolve() if diretorio_saida else Path.cwd()
        caminho_saida.mkdir(parents=True, exist_ok=True, mode=0o700)  # Permissões seguras

        logger.info(f"Iniciando extração de {self.caminho_arquivo} para {caminho_saida}")

        try:
            if self.formato == '.zip':
                self._extrair_zip(caminho_saida)
            else:
                self._extrair_tar(caminho_saida)
        except Exception as e:
            logger.exception(f"Falha crítica na extração: {str(e)}")
            # Limpeza em caso de falha
            if caminho_saida.exists() and any(caminho_saida.iterdir()):
                shutil.rmtree(caminho_saida, ignore_errors=True)
            raise ErroArquivo("Erro durante a extração") from e

    def _sanitizar_caminho(self, caminho: Path, destino: Path) -> Path:
        """Previne ataques de path traversal"""
        caminho_resolvido = (destino / caminho).resolve()
        if not caminho_resolvido.is_relative_to(destino.resolve()):
            raise ArquivoInvalidoError(f"Tentativa de path traversal detectada: {caminho}")
        return caminho_resolvido

    def _extrair_zip(self, diretorio_saida: Path) -> None:
        """Extrai arquivos ZIP com verificação de segurança"""
        try:
            with zipfile.ZipFile(self.caminho_arquivo) as arquivo_zip:
                # Verificação de integridade
                arquivo_corrompido = arquivo_zip.testzip()
                if arquivo_corrompido:
                    raise ArquivoInvalidoError(f"Arquivo ZIP corrompido: {arquivo_corrompido}")

                # Extração segura item por item
                for membro in arquivo_zip.infolist():
                    caminho_alvo = self._sanitizar_caminho(Path(membro.filename), diretorio_saida)
                    if membro.is_dir():
                        caminho_alvo.mkdir(exist_ok=True, mode=0o700)
                    else:
                        with arquivo_zip.open(membro) as origem, open(caminho_alvo, 'wb') as destino:
                            shutil.copyfileobj(origem, destino)
                        # Manter permissões originais (quando seguras)
                        modo = membro.external_attr >> 16 & 0o777
                        if modo and not (modo & 0o200):  # Evitar permissões inseguras
                            caminho_alvo.chmod(modo & 0o777)
        except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
            raise ArquivoInvalidoError("Arquivo ZIP inválido ou corrompido") from e

    def _extrair_tar(self, diretorio_saida: Path) -> None:
        """Extrai arquivos TAR com diferentes compressões"""
        mapeamento_compressao = {
            '.tar': '',
            '.tar.gz': 'gz',
            '.tar.bz2': 'bz2',
            '.tar.xz': 'xz'
        }
        modo = f'r:{mapeamento_compressao[self.formato]}' if mapeamento_compressao[self.formato] else 'r'

        try:
            with tarfile.open(self.caminho_arquivo, modo) as arquivo_tar:
                # Verificação de segurança para cada item
                for membro in arquivo_tar.getmembers():
                    caminho_alvo = self._sanitizar_caminho(Path(membro.name), diretorio_saida)
                    if membro.isdir():
                        caminho_alvo.mkdir(exist_ok=True, mode=0o700)
                    else:
                        arquivo_tar.extract(membro, diretorio_saida, set_attrs=False)
                        # Ajustar permissões
                        if membro.mode:
                            caminho_alvo.chmod(membro.mode & 0o777)
        except tarfile.ReadError as e:
            raise ArquivoInvalidoError("Arquivo TAR inválido ou corrompido") from e


def principal():
    """Função principal para CLI com tratamento robusto"""
    if len(sys.argv) not in (2, 3):
        print(f"Uso: {sys.argv[0]} <arquivo> [diretório_saida]")
        sys.exit(1)

    try:
        descompactador = Descompactador(sys.argv[1])
        descompactador.extrair(sys.argv[2] if len(sys.argv) == 3 else None)
        logger.info("✅ Extração concluída com sucesso")
        sys.exit(0)
    except ErroArquivo as e:
        logger.error(f"❌ Erro de processamento: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("⏹️ Extração interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"💣 Erro inesperado: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    principal()
