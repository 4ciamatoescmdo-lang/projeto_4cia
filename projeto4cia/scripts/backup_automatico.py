"""
backup_automatico.py
====================
Backup automático do projeto Django (SQLite + media) para o Google Drive.

SETUP (rodar UMA VEZ antes de agendar):
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Depois coloque o arquivo credentials.json (baixado do Google Cloud Console)
na mesma pasta deste script e rode uma vez manualmente para autorizar.
"""

import os
import shutil
import zipfile
import logging
import datetime
import sys
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURAÇÕES — EDITE AQUI
# ──────────────────────────────────────────────

# Pasta raiz do seu projeto Django (onde está manage.py)
PROJETO_RAIZ = Path(r"C:\Users\TCO\Downloads\GITHUB\aplicativo_4cia_2026_1-main\aplicativo_4cia_2026_1-main\projeto4cia")

# Arquivos/pastas a incluir no backup
ITENS_BACKUP = [
    PROJETO_RAIZ / "db.sqlite3",          # banco SQLite
    PROJETO_RAIZ / "media",               # uploads (assinaturas, fotos, etc.)
]

# Pasta local onde os ZIPs ficam antes de subir
PASTA_BACKUP_LOCAL = PROJETO_RAIZ / "backups" / "database"

# Nome da pasta no Google Drive (será criada se não existir)
PASTA_DRIVE = "Backups_Django_Policia"

# Quantos backups locais manter (mais antigos são deletados)
MAX_BACKUPS_LOCAIS = 7

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────

LOG_FILE = PROJETO_RAIZ / "backups" / "logs" / "backup.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# PASSO 1 — CRIAR ZIP
# ──────────────────────────────────────────────

def criar_zip() -> Path:
    """Compacta banco + media em um único .zip com timestamp."""
    PASTA_BACKUP_LOCAL.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_zip = f"backup_{ts}.zip"
    caminho_zip = PASTA_BACKUP_LOCAL / nome_zip

    log.info(f"Criando zip: {caminho_zip}")

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in ITENS_BACKUP:
            item = Path(item)
            if not item.exists():
                log.warning(f"  Item não encontrado, pulando: {item}")
                continue

            if item.is_file():
                zf.write(item, item.name)
                log.info(f"  + {item.name}")
            elif item.is_dir():
                for arq in item.rglob("*"):
                    if arq.is_file():
                        arcname = arq.relative_to(item.parent)
                        zf.write(arq, arcname)
                log.info(f"  + {item.name}/ (pasta)")

    tamanho_mb = caminho_zip.stat().st_size / 1_048_576
    log.info(f"Zip criado: {tamanho_mb:.1f} MB")
    return caminho_zip


# ──────────────────────────────────────────────
# PASSO 2 — AUTENTICAR NO GOOGLE DRIVE
# ──────────────────────────────────────────────

def autenticar_drive():
    """
    Retorna um serviço autenticado do Google Drive.
    Na primeira execução abre o browser para autorizar.
    Nas próximas usa o token salvo em token.json.
    """
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    CREDS_FILE = Path(__file__).parent / "credentials.json"
    TOKEN_FILE = Path(__file__).parent / "token.json"

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                log.error("ERRO: credentials.json não encontrado!")
                log.error("Baixe em: console.cloud.google.com → APIs → Credenciais → OAuth 2.0")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


# ──────────────────────────────────────────────
# PASSO 3 — FAZER UPLOAD
# ──────────────────────────────────────────────

def obter_ou_criar_pasta(service, nome_pasta: str) -> str:
    """Retorna o ID da pasta no Drive, criando se necessário."""
    query = (
        f"name='{nome_pasta}' "
        f"and mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    resultado = service.files().list(q=query, fields="files(id,name)").execute()
    arquivos = resultado.get("files", [])

    if arquivos:
        pasta_id = arquivos[0]["id"]
        log.info(f"Pasta no Drive encontrada: {nome_pasta} (id={pasta_id})")
        return pasta_id

    # Cria a pasta
    meta = {"name": nome_pasta, "mimeType": "application/vnd.google-apps.folder"}
    pasta = service.files().create(body=meta, fields="id").execute()
    pasta_id = pasta["id"]
    log.info(f"Pasta criada no Drive: {nome_pasta} (id={pasta_id})")
    return pasta_id


def fazer_upload(service, caminho_zip: Path, pasta_id: str):
    """Envia o zip para o Google Drive."""
    from googleapiclient.http import MediaFileUpload

    meta = {"name": caminho_zip.name, "parents": [pasta_id]}
    media = MediaFileUpload(str(caminho_zip), mimetype="application/zip", resumable=True)

    log.info(f"Enviando para o Drive: {caminho_zip.name} ...")
    arquivo = service.files().create(body=meta, media_body=media, fields="id,name").execute()
    log.info(f"Upload concluído: {arquivo['name']} (id={arquivo['id']})")


# ──────────────────────────────────────────────
# PASSO 4 — LIMPAR BACKUPS ANTIGOS LOCAIS
# ──────────────────────────────────────────────

def limpar_backups_antigos():
    """Mantém apenas os N backups mais recentes na pasta local."""
    zips = sorted(PASTA_BACKUP_LOCAL.glob("backup_*.zip"))
    remover = zips[:-MAX_BACKUPS_LOCAIS] if len(zips) > MAX_BACKUPS_LOCAIS else []
    for arq in remover:
        arq.unlink()
        log.info(f"Backup antigo removido: {arq.name}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    log.info("=" * 55)
    log.info("INICIANDO BACKUP AUTOMÁTICO")
    log.info("=" * 55)

    try:
        # 1. Criar zip
        caminho_zip = criar_zip()

        # 2. Autenticar e fazer upload
        log.info("Autenticando no Google Drive...")
        service = autenticar_drive()
        pasta_id = obter_ou_criar_pasta(service, PASTA_DRIVE)
        fazer_upload(service, caminho_zip, pasta_id)

        # 3. Limpar locais antigos
        limpar_backups_antigos()

        log.info("BACKUP CONCLUÍDO COM SUCESSO ✓")

    except Exception as e:
        log.exception(f"ERRO NO BACKUP: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()