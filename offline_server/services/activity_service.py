import datetime
from datetime import UTC
import re
from config import REGISTRO_JSON
from offline_server.utils.file_utils import carregar_dados, salvar_dados
from offline_server.utils.crypto_utils import encrypt_cpf

def registrar_atividade(atividade_dict: dict):
    registros = carregar_dados(REGISTRO_JSON)
    data_hoje = datetime.datetime.now(UTC).strftime("%Y-%m-%d")
    data_hora_atual = datetime.datetime.now(UTC).astimezone().isoformat()

    identificador = None
    metodo = None

    if atividade_dict.get("is_foreign") == False:
        # Usuário brasileiro → valida CPF
        if atividade_dict.get("method") == "cpf":
            cpf_raw = atividade_dict.get("id_number", "")
            cpf_formatado = re.sub(r'\D', '', cpf_raw)

            if len(cpf_formatado) != 11 or cpf_formatado == cpf_formatado[0] * 11:
                return {"status": "error", "message": "CPF inválido"}

            # 1º dígito verificador
            soma = sum(int(cpf_formatado[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto

            # 2º dígito verificador
            soma = sum(int(cpf_formatado[i]) * (11 - i) for i in range(9)) + digito1 * 2
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto

            if int(cpf_formatado[9]) != digito1 or int(cpf_formatado[10]) != digito2:
                return {"status": "error", "message": "CPF inválido"}

            identificador = cpf_formatado
            metodo = "cpf"
        else:
            # Caso seja outro método, ex: QRCode
            identificador = atividade_dict.get("id_number", "")
            metodo = "qrcode"

    else:
        # Usuário estrangeiro → usa passaporte
        passport = atividade_dict.get("id_number", "").strip()
        if not passport:
            return {"status": "error", "message": "Passaporte obrigatório"}
        identificador = passport
        metodo = "passport"

    # Monta o registro
    novo_registro = {
        "id_number": identificador,
        "method": metodo,
        "stand_name": atividade_dict.get("stand_name", ""),
        "tablet_name": atividade_dict.get("tablet_name", ""),
        "client_validated_at": data_hora_atual,
        "status": "local"
    }

    # Evita duplicados no mesmo dia
    for registro in registros:
        registro_data = registro.get('client_validated_at', '') or registro.get('data_hora', '')
        if (registro.get('id_number') == identificador and
            registro.get('stand_name') == atividade_dict.get("stand_name", "") and
            registro_data.startswith(data_hoje)):
            registros.append(novo_registro)
            salvar_dados(registros, REGISTRO_JSON)
            return {"status": "success", "message": "Atividade já registrada hoje"}

    registros.append(novo_registro)
    salvar_dados(registros, REGISTRO_JSON)
    return {"status": "success", "message": "Atividade registrada com sucesso"}
