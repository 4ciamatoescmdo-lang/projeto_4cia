#!/bin/bash

# CONFIGURAÇÕES
PROJECT_DIR="/home/mendes/Documentos/GitHub/aplicativo_4cia_2026/projeto4cia"
BACKUP_DIR="$PROJECT_DIR/backups/database"
LOG_DIR="$PROJECT_DIR/backups/logs"
DB_FILE="$PROJECT_DIR/db.sqlite3"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${DATE}.sqlite3.gz"
LOG_FILE="$LOG_DIR/backup_$(date +%Y%m%d).log"

# Criar diretórios se não existirem
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Início
log "🚀 INICIANDO BACKUP AUTOMÁTICO"

# Verificar se o banco existe
if [ ! -f "$DB_FILE" ]; then
    log "❌ ERRO: Banco de dados não encontrado em $DB_FILE"
    exit 1
fi

# Verificar tamanho do banco
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
log "📊 Tamanho do banco: $DB_SIZE"

# Criar backup comprimido
log "📦 Criando backup: $BACKUP_NAME"
gzip -c "$DB_FILE" > "$BACKUP_DIR/$BACKUP_NAME"

# Verificar se o backup foi criado
if [ -f "$BACKUP_DIR/$BACKUP_NAME" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
    log "✅ Backup criado com sucesso: $BACKUP_NAME ($BACKUP_SIZE)"
else
    log "❌ ERRO: Falha ao criar backup"
    exit 1
fi

# Remover backups antigos (manter últimos 30)
log "🗑️ Removendo backups antigos..."
cd "$BACKUP_DIR"
ls -t backup_*.gz 2>/dev/null | tail -n +31 | while read old_backup; do
    rm -f "$old_backup"
    log "   Removido: $old_backup"
done

# Contar backups atuais
BACKUP_COUNT=$(ls -1 backup_*.gz 2>/dev/null | wc -l)
log "📁 Total de backups atuais: $BACKUP_COUNT"

# Verificar integridade do último backup
log "🔍 Verificando integridade..."
if gzip -t "$BACKUP_DIR/$BACKUP_NAME" 2>/dev/null; then
    log "✅ Backup íntegro e válido"
else
    log "❌ ERRO: Backup corrompido!"
    exit 1
fi

log "✅ BACKUP CONCLUÍDO COM SUCESSO"
echo "---"
exit 0
