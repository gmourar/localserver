# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socket

from offline_server.routes import register_routes, activity_routes, qr_routes, cpf_routes

app = FastAPI(
    title="API PromoTablet",
    description="API para cadastro e registro de atividades via tablet ou QRCode",
    version="1.0.0",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(register_routes.router)
app.include_router(cpf_routes.router)
app.include_router(activity_routes.router)
app.include_router(qr_routes.router)


if __name__ == "__main__":
    import uvicorn
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\nAPI disponível em:")
    print(f"http://localhost:8000")
    print(f"http://{local_ip}:8000\n")

    # 🔹 Se rodar direto com "py main.py"
    uvicorn.run(app, host="0.0.0.0", port=8000)


    # 🔹 Se rodar como módulo (uvicorn offline_server.main:app) também funciona
