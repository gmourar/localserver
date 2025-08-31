from offline_server.schemas.qrcode_schema import QRCodeModel
from offline_server.utils.crypto_utils import decrypt_cpf
from offline_server.services.activity_service import registrar_atividade

def processar_qrcode_controller(qr_data: QRCodeModel) -> dict:
    try:
        cpf = decrypt_cpf(qr_data.id_number)
        payload = qr_data.dict()
        payload["is_foreign"] = qr_data.is_foreign  # 🔹 adiciona o campo is_foreign ao payload
        payload["id_number"] = qr_data.id_number  # 🔹 salva também a chave recebida
        payload["method"] = qr_data.method  # 🔹 salva o método
        return registrar_atividade(payload)
    except Exception as e:
        return {"status": "error", "message": f"Falha ao processar QRCode: {str(e)}"}
