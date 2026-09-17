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

# 시작 완료/실패가 로그에 찍힐 때까지 최대 2분 대기
echo "시작 대기 중..."
for _ in $(seq 1 60); do
    logs=$(docker logs genesis-api 2>&1)
    if grep -q "Started WikiApiApplication" <<<"$logs"; then
        echo "✅ genesis-api 시작 완료"
        exit 0
    fi
    if grep -q "APPLICATION FAILED TO START\|Application run failed" <<<"$logs"; then
        break
    fi
    sleep 2
done
echo "❌ genesis-api 시작 실패 또는 2분 초과. 최근 로그:"
docker logs --tail 80 genesis-api
exit 1
