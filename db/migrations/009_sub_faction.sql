-- 이루스: 게임 프로필의 소속 진영이 "게이시르, 암흑신" 두 개다.
-- 주 진영은 faction 에, 두 번째 진영은 sub_faction 에 넣는다 (목록 필터는 둘 다 본다).
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod') NOT NULL;

ALTER TABLE characters
    ADD COLUMN sub_faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad','darkgod') NULL
        COMMENT '두 번째 소속 진영' AFTER faction;
