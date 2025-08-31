import subprocess
import platform
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timezone

# Configurações
USUARIOS_PATH = Path("data/usuarios.json")
REGISTROS_PATH = Path("data/registros.json")

AWS_ENDPOINT_USUARIOS = "http://ec2-54-233-101-11.sa-east-1.compute.amazonaws.com:3333/register"  
AWS_ENDPOINT_REGISTROS = "http://ec2-54-233-101-11.sa-east-1.compute.amazonaws.com:3333/activity/validate"  

PING_TARGET = "google.com"
PING_PARAM = "-n" if platform.system().lower() == "windows" else "-c"

def verificar_conexao():
    """Verifica conexão com a internet via ping"""
    result = subprocess.run(
        ["ping", PING_PARAM, "1", PING_TARGET],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def carregar_arquivo(path):
    """Carrega conteúdo JSON do arquivo"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if not conteudo:  # Arquivo vazio
                    print(f"Arquivo {path} está vazio - pulando")
                    return []
                return json.loads(conteudo)
        except json.JSONDecodeError:
            print(f"Erro ao ler {path} - JSON corrompido")
            return []
    else:
        print(f"Arquivo {path} não encontrado - criando novo")
        # Cria o arquivo com array vazio se não existir
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def salvar_arquivo(path, dados):
    """Salva conteúdo atualizado no JSON"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def montar_payload_registro(item):
    """Monta o payload correto para envio de registros"""
    return {
        "cpf": item["cpf"],
        "method": "qrcode" if "chave_cpf" in item else "cpf",
        "stand_name": item.get("atividade", ""),
        "tablet_name": item.get("id_tablet", ""),
        "client_validated_at": datetime.now(timezone.utc).astimezone().isoformat()
    }

def enviar_para_aws(item, endpoint, is_registro=False):
    """Envia item para AWS e trata resposta"""
    try:
        payload = montar_payload_registro(item) if is_registro else item

        response = requests.post(endpoint, json=payload, timeout=10)
        item["response"] = response.text

        if response.status_code == 200:
            print(f"Enviado com sucesso: {item.get('cpf')}")
            item["status"] = "enviado"
            return True
        else:
            print(f"Falha ao enviar {item.get('cpf')}. Status: {response.status_code}")
            return False
    except Exception as e:
        item["response"] = str(e)
        print(f"Erro ao enviar {item.get('cpf')}: {e}")
        return False

def processar_arquivo(path, endpoint, is_registro=False):
    """Percorre a lista do arquivo e envia apenas os itens com status local"""
    dados = carregar_arquivo(path)
    
    if not dados:  # Arquivo vazio
        print(f"Nenhum dado para processar em {path}")
        return
    
    for item in dados:
        if item.get("status") == "local":
            sucesso = enviar_para_aws(item, endpoint, is_registro=is_registro)
            if sucesso:
                salvar_arquivo(path, dados)  # <-- salva imediatamente após cada envio
                time.sleep(5)  # mantém o delay entre envios

# Loop infinito para envio periódico
while True:
    if verificar_conexao():
        print("Connected ✅")

        # Envia usuários
        processar_arquivo(USUARIOS_PATH, AWS_ENDPOINT_USUARIOS)

        # Envia registros
        processar_arquivo(REGISTROS_PATH, AWS_ENDPOINT_REGISTROS, is_registro=True)

    else:
        print("Offline ❌")
    
    # espera 10 minutos antes de tentar novamente
    time.sleep(600)
