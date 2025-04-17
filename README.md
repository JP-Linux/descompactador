# 🔓 Descompactador de Arquivos Avançado

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma ferramenta robusta para descompactação de arquivos com tratamento de erros e suporte a múltiplos formatos.

## 📋 Recursos
- Formatos suportados: `.zip`, `.tar.gz`, `.tar.bz2`, `.tar.xz`
- Detecção automática de formato
- Saída para diretório customizado
- Validação de integridade de arquivos
- Logging detalhado das operações
- Tratamento de erros granular
- Interface em português

## 📦 Pré-requisitos
- Python 3.8+
- Nenhuma dependência externa necessária

## ⚙️ Instalação
```bash
git clone https://github.com/JP-Linux/descompactador.git
cd descompactador
```

## 🚀 Como Usar
### Descompactação básica:
```bash
python3 descompactador.py arquivo_compactado.extensao
```

### Especificando diretório de saída:
```bash
python3 descompactador.py arquivo_compactado.zip saida/
```

### Exemplos:
```bash
# Descompactar .tar.gz para diretório específico
python3 descompactador.py backup.tar.gz documentos/

# Verificar extração de .zip corrompido
python3 descompactador.py arquivo_invalido.zip
```

## 🛑 Possíveis Erros
```bash
# Arquivo não encontrado
Erro: Arquivo não encontrado: arquivo_inexistente.zip

# Formato não suportado
Erro: Formato não suportado: arquivo.rar

# Arquivo corrompido
Erro: Arquivo ZIP inválido ou corrompido
```

## 🧩 Como Funciona
O script utiliza:
- `zipfile` para manipulação de arquivos ZIP
- `tarfile` para arquivos TAR com diferentes compressões
- Verificação de integridade antes da extração
- Sistema hierárquico de exceções customizadas

## 📄 Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
