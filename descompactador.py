#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os


class Descompactar:
    """
    Essa classe contém os métodos necessários para descompactar arquivos com extensão .zip, .tar.gz, .tar.bz2 e .tar.xz.
    """

    def __init__(self):
        """
        Inicializa a classe Descompactar com a variável ponto igual a False.
        """
        self.ponto = False

    def extensao(self, extp):
        """
        Esse método recebe como parâmetro a extensão do arquivo a ser descompactado e realiza a descompactação se a extensão
        for uma das extensões esperadas. Para isso, o método utiliza o método filtro para filtrar a extensão do arquivo e 
        determinar qual o comando de descompactação deve ser executado. 

        :param extp: a extensão do arquivo a ser descompactado.
        """
        self.contador = 0
        ext = self.filtro(arq=extp, opcao="reverso")
        for x in ext:
            if "." in x:
                self.ponto = True
                self.contador += 1
        if self.ponto:
            exten = self.filtro(arq=ext, opcao="ponto")
            print(exten)
            if exten == ".zip":
                print(f"7z x {extp}")
                os.system(f"7z x {extp}")
            elif exten == ".tar.gz":
                print(f"tar -xvzf {extp}")
                os.system(f"tar -xvzf {extp}")
            elif exten == ".tar.bz2":
                print(f"tar -xvjf {extp}")
                os.system(f"tar -xvjf {extp}")
            elif exten == ".tar.xz":
                print(f"tar -xvf {extp}")
                os.system(f"tar -xvf {extp}")

    def filtro(self, arq=None, opcao=None):
        """
        Esse método recebe como parâmetro o nome do arquivo e a opção de filtragem (reverso ou ponto) e retorna a extensão 
        do arquivo de acordo com a opção de filtragem.

        :param arq: o nome do arquivo.
        :param opcao: a opção de filtragem (reverso ou ponto).
        :return: a extensão do arquivo.
        """
        if opcao == "reverso":
            self.arq = arq[::-1]
            return self.arq
        elif opcao == "ponto":
            revext_1 = arq[:arq.index(".") + 1]
            normal_1 = revext_1[::-1]
            corte = arq[len(revext_1):]
            if self.contador > 1:
                if normal_1 == ".zip" or normal_1 == ".rar":
                    return normal_1
                else:
                    revext_2 = corte[:corte.index(".") + 1]
                    normal_2 = revext_2[::-1]
                    return f"{normal_2}{normal_1}"
            else:
                return normal_1


if __name__ == "__main__":
    d = Descompactar()
    d.extensao(sys.argv[1])
