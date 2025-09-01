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
    """Monta o payload para /activity/validate conforme o backend"""
    # Deriva stand/tablet a partir de possíveis chaves antigas
    stand_name = item.get("stand_name") or item.get("atividade") or ""
    tablet_name = item.get("tablet_name") or item.get("id_tablet") or ""

    # Determina o método
    method = item.get("method")
    if not method:
        if "chave_cpf" in item:
            method = "qrcode"
        else:
            method = "cpf"

    # Determina id_number
    id_number = item.get("id_number")
    if not id_number:
        id_number = item.get("cpf") or item.get("chave_cpf") or ""

    # is_foreign e id_type
    is_foreign = item.get("is_foreign")
    if is_foreign is None:
        is_foreign = False

    id_type = item.get("id_type")
    if not id_type:
        id_type = "passport" if is_foreign else "cpf"

    # client_validated_at
    client_validated_at = item.get("client_validated_at")
    if not client_validated_at:
        # tenta usar data_hora antiga se existir
        data_hora = item.get("data_hora")
        if data_hora:
            try:
                # parse "YYYY-MM-DD HH:MM:SS" como local e exporta ISO com timezone local
                dt = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
                client_validated_at = dt.astimezone().isoformat()
            except Exception:
                client_validated_at = datetime.now(timezone.utc).astimezone().isoformat()
        else:
            client_validated_at = datetime.now(timezone.utc).astimezone().isoformat()

    return {
        "is_foreign": is_foreign,
        "id_type": id_type,
        "id_number": id_number,
        "method": method,
        "stand_name": stand_name,
        "tablet_name": tablet_name,
        "client_validated_at": client_validated_at,
    }

def montar_payload_usuario(item):
    """Monta o payload para /register conforme o backend"""
    payload = {
        "name": item.get("name"),
        "email": item.get("email"),
        "phone": item.get("phone"),
        "date_birthday": item.get("date_birthday"),
        "is_foreign": item.get("is_foreign"),
        "id_type": item.get("id_type"),
        "id_number": item.get("id_number"),
        "source": item.get("source"),
    }
    # Campos opcionais
    if item.get("tablet_name"):
        payload["tablet_name"] = item.get("tablet_name")
    # client_created_at: se existir, usa; senão gera agora
    client_created_at = item.get("client_created_at")
    if not client_created_at:
        client_created_at = datetime.now(timezone.utc).astimezone().isoformat()
    payload["client_created_at"] = client_created_at
    return payload

def enviar_para_aws(item, endpoint, is_registro=False):
    """Envia item para AWS e trata resposta"""
    try:
        payload = montar_payload_registro(item) if is_registro else montar_payload_usuario(item)

        response = requests.post(endpoint, json=payload, timeout=10)
        item["response"] = response.text

        if response.status_code == 200:
            identificador = payload.get("id_number") or item.get("cpf") or item.get("email") or "sem_id"
            print(f"Enviado com sucesso: {identificador}")
            item["status"] = "enviado"
            return True
        else:
            identificador = payload.get("id_number") or item.get("cpf") or item.get("email") or "sem_id"
            print(f"Falha ao enviar {identificador}. Status: {response.status_code}")
            return False
    except Exception as e:
        item["response"] = str(e)
        identificador = item.get("cpf") or item.get("email") or "sem_id"
        print(f"Erro ao enviar {identificador}: {e}")
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
