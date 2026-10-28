-- 에밀리오의 주신 소속 추가. 기존 ENUM 순서를 보존한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han','tempest_circus','jushin') NOT NULL,
    MODIFY COLUMN sub_faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod','kashmir','bifrost','cyrus','amigo','trisis','han','tempest_circus','jushin') NULL COMMENT '두 번째 소속 진영';
