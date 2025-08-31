from pydantic import BaseModel

class QRCodeModel(BaseModel):
    id_number: str
    method: str
    stand_name: str
    tablet_name: str
    is_foreign: bool
    client_validated_at: str
