-- 아이린 사르데스: 다갈과 구분되는 가라드 진영을 추가한다.
ALTER TABLE characters
    MODIFY COLUMN faction ENUM('geysir','pendragon','independent','astania','zephyrfalcon','dagal','curtis','garad') NOT NULL;
