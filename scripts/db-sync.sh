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

source scripts/lib/db.sh
db_backup
db_mysql -t < "$SQL"
echo "✅ 반영 완료"
