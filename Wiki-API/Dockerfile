# ─── 빌드 ─────────────────────────────────────────────────
FROM eclipse-temurin:17-jdk AS build
WORKDIR /src

# 의존성만 먼저 받아서 캐시 (소스만 바뀌면 이 단계는 재사용)
COPY gradlew settings.gradle.kts build.gradle.kts ./
COPY gradle gradle
RUN ./gradlew --no-daemon dependencies > /dev/null || true

COPY src src
RUN ./gradlew --no-daemon bootJar

# ─── 실행 ─────────────────────────────────────────────────
# DB 접속 정보는 이미지에 넣지 않고 실행 시 --env-file 로 전달
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /src/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
