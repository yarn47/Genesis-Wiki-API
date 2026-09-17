#!/usr/bin/env bash
# 서버에서 git pull 후 실행: 이미지 빌드 → genesis-api 컨테이너 교체
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f Wiki-API/.env ]; then
    echo "Wiki-API/.env 가 없습니다. Wiki-API/.env.example 을 참고해서 만들어주세요."
    exit 1
fi

docker build -t genesis-api Wiki-API

docker rm -f genesis-api 2>/dev/null || true
# DB(genesis-db)를 localhost:3307 로 접속하므로 host 네트워크 사용 → API는 서버 8080 포트
docker run -d --name genesis-api \
    --network host \
    --restart unless-stopped \
    --env-file Wiki-API/.env \
    genesis-api

echo "시작 로그 (Ctrl+C 로 로그 보기만 종료, 컨테이너는 계속 실행됨)"
docker logs -f --tail 50 genesis-api
