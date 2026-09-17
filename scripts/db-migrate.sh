#!/usr/bin/env bash
# db/migrations/*.sql 중 아직 적용 안 된 파일을 이름 순서대로 적용 (서버에서 실행)
# 적용 기록은 schema_migrations 테이블에 남김. 백엔드 배포(deploy.sh) 전에 실행.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib/db.sh

echo "CREATE TABLE IF NOT EXISTS schema_migrations (
    version    VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);" | db_mysql

applied=$(echo "SELECT version FROM schema_migrations;" | db_mysql -N)
pending=()
for f in db/migrations/*.sql; do
    [ -e "$f" ] || continue
    grep -qxF "$(basename "$f" .sql)" <<<"$applied" || pending+=("$f")
done

if [ ${#pending[@]} -eq 0 ]; then
    echo "적용할 마이그레이션 없음"
    exit 0
fi

db_backup
for f in "${pending[@]}"; do
    version=$(basename "$f" .sql)
    echo "적용: $version"
    db_mysql < "$f"
    echo "INSERT INTO schema_migrations (version) VALUES ('$version');" | db_mysql
done
echo "✅ 마이그레이션 완료"
