from fastapi import APIRouter
from offline_server.schemas.qrcode_schema import QRCodeModel
from offline_server.controllers.qr_controller import processar_qrcode_controller

router = APIRouter(prefix="/activity/validate-qr", tags=["QR Code"])

@router.post("")
async def process_qrcode(qr_data: QRCodeModel):
    return processar_qrcode_controller(qr_data)
