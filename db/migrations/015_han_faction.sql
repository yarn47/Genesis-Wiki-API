-- 백옥당의 소속 한제국. 캐릭터 데이터 동기화 전에 적용한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han') NOT NULL,
    MODIFY COLUMN sub_faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han') NULL COMMENT '두 번째 소속 진영';
