from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Pasta onde ficam os arquivos de dados
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)  # garante que a pasta exista

# Caminhos dos arquivos JSON
ARQUIVO_JSON = DATA_DIR / "usuarios.json"
REGISTRO_JSON = DATA_DIR / "registros.json"

# Chave de criptografia
SECRET_KEY = os.getenv("SECRET_KEY")
