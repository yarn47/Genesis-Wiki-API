#!/usr/bin/env bash
# data/ 의 JSON을 SQL로 변환해 genesis-db에 반영 (서버에서 실행)
#   ./scripts/db-sync.sh            백업 → 반영 → 결과 요약
#   ./scripts/db-sync.sh --dry-run  생성될 SQL만 출력 (DB 접속 안 함)
set -euo pipefail
cd "$(dirname "$0")/.."

SQL=$(mktemp)
trap 'rm -f "$SQL"' EXIT
python3 scripts/gen_sql.py > "$SQL"

if [ "${1:-}" = "--dry-run" ]; then
    cat "$SQL"
    exit 0
fi

ENV_FILE=Wiki-API/.env
DB_CONTAINER=genesis-db
env_value() { grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '\r'; }
DB_USER=$(env_value DB_USERNAME)
DB_PASS=$(env_value DB_PASSWORD)
DB_NAME=$(env_value DB_URL | sed -E 's#^[^/]*//[^/]+/([^?]+).*#\1#')

# 반영 전 DB 전체 백업 (최근 30개만 보관)
BACKUP_DIR=~/db-backups
mkdir -p "$BACKUP_DIR"
BACKUP="$BACKUP_DIR/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
docker exec -e MYSQL_PWD="$DB_PASS" "$DB_CONTAINER" \
    mysqldump -u"$DB_USER" --single-transaction --no-tablespaces --default-character-set=utf8mb4 "$DB_NAME" > "$BACKUP"
echo "백업: $BACKUP"
ls -1t "$BACKUP_DIR"/${DB_NAME}_*.sql | tail -n +31 | xargs -r rm --

docker exec -i -e MYSQL_PWD="$DB_PASS" "$DB_CONTAINER" \
    mysql -u"$DB_USER" --default-character-set=utf8mb4 -t "$DB_NAME" < "$SQL"
echo "✅ 반영 완료"
