-- 아리아나 위버: 기존 진영 값을 유지하고 커티스만 추가한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis') NOT NULL;
