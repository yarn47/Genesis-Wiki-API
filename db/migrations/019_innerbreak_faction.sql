-- 에스테 도데의 이너브레이크 소속 추가. 기존 ENUM 순서를 보존한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han','tempest_circus','jushin','innerbreak') NOT NULL,
    MODIFY COLUMN sub_faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han','tempest_circus','jushin','innerbreak') NULL COMMENT '두 번째 소속 진영';
