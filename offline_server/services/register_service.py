import datetime
import re
from datetime import UTC
from validate_docbr import CPF
from config import ARQUIVO_JSON
from offline_server.utils.file_utils import carregar_dados, salvar_dados

def cadastrar_usuario(usuario_dict: dict):
    dados = carregar_dados(ARQUIVO_JSON)
    usuario_dict["client_created_at"] = datetime.datetime.now(UTC).astimezone().isoformat()
    usuario_dict["status"] = "local"

    cpf_valido = None  # variável para controle

    # ===== Verificação de nacionalidade =====
    if usuario_dict.get("is_foreign") == False:  
        # Usuário brasileiro → valida CPF
        usuario_dict["id_type"] = "cpf"
        cpf_raw = usuario_dict.get("id_number", "")
        cpf_validator = CPF()

        if not cpf_validator.validate(cpf_raw):
            return {"status": "error", "message": "CPF inválido"}

        # Normaliza (apenas números)
        cpf_valido = re.sub(r'\D', '', cpf_raw)
        usuario_dict["id_number"] = cpf_valido
        usuario_dict["cpf"] = cpf_valido

        # Verifica duplicidade
        if any(u.get("cpf") == cpf_valido for u in dados):
            return {"status": "error", "message": "CPF já cadastrado"}

    else:
        # Usuário estrangeiro → passport
        usuario_dict["id_type"] = "passport"
        passport = usuario_dict.get("id_number", "").strip()
        if not passport:
            return {"status": "error", "message": "Passport inválido"}

        if any(u.get("id_number") == passport for u in dados):
            return {"status": "error", "message": "Passport já cadastrado"}

    # ===== Validação de e-mail =====
    email = usuario_dict.get("email", "")
    padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not re.match(padrao_email, email):
        return {"status": "error", "message": "E-mail inválido"}

    # ===== Verifica duplicidade de email e telefone =====
    for u in dados:
        if email and u.get("email") == email:
            return {"status": "error", "message": "E-mail já cadastrado"}
        phone = usuario_dict.get("phone")
        if phone and u.get("phone") == phone:
            return {"status": "error", "message": "Telefone já cadastrado"}

    # ===== Salva após todas as validações =====
    dados.append(usuario_dict)
    salvar_dados(dados, ARQUIVO_JSON)

    return {
        "status": "success",
        "message": "Cadastro realizado com sucesso",
        "dados_cadastrados": usuario_dict
    }
