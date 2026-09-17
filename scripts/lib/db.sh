# db-sync.sh / db-migrate.sh 공통: 서버의 Wiki-API/.env로 genesis-db 접속, 백업
# 저장소 루트에서 source 해서 사용

ENV_FILE=Wiki-API/.env
DB_CONTAINER=genesis-db

env_value() { grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '\r'; }
DB_USER=$(env_value DB_USERNAME)
DB_PASS=$(env_value DB_PASSWORD)
DB_NAME=$(env_value DB_URL | sed -E 's#^[^/]*//[^/]+/([^?]+).*#\1#')

# 사용: db_mysql [mysql 옵션...] < file.sql
db_mysql() {
    docker exec -i -e MYSQL_PWD="$DB_PASS" "$DB_CONTAINER" \
        mysql -u"$DB_USER" --default-character-set=utf8mb4 "$@" "$DB_NAME"
}

# DB 전체 백업 (최근 30개만 보관)
db_backup() {
    local dir=~/db-backups
    mkdir -p "$dir"
    local file="$dir/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    docker exec -e MYSQL_PWD="$DB_PASS" "$DB_CONTAINER" \
        mysqldump -u"$DB_USER" --single-transaction --no-tablespaces --default-character-set=utf8mb4 "$DB_NAME" > "$file"
    echo "백업: $file"
    ls -1t "$dir"/${DB_NAME}_*.sql | tail -n +31 | xargs -r rm --
}
