-- 슈안 노르의 소속 사이럽스. 캐릭터 데이터 동기화 전에 적용한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus') NOT NULL,
    MODIFY COLUMN sub_faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus') NULL COMMENT '두 번째 소속 진영';
