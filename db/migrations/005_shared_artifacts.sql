-- 아티팩트를 캐릭터 소속이 아니라 공용 목록으로
-- (같은 아티팩트를 여러 캐릭터가 씀. 발현 3~6단 = 아티팩트 ★1~★4)

CREATE TABLE IF NOT EXISTS character_artifacts (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    character_id   INT NOT NULL,
    artifact_id    INT NOT NULL,
    artifact_order INT NOT NULL COMMENT '캐릭터 발현 트리에서의 순서 1~4',
    UNIQUE KEY uk_character_order (character_id, artifact_order),
    UNIQUE KEY uk_character_artifact (character_id, artifact_id),
    CONSTRAINT fk_ca_character FOREIGN KEY (character_id) REFERENCES characters (character_id) ON DELETE CASCADE,
    CONSTRAINT fk_ca_artifact  FOREIGN KEY (artifact_id)  REFERENCES artifacts (artifact_id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='캐릭터가 쓰는 아티팩트';

-- 기존 캐릭터-아티팩트 관계 이관
INSERT IGNORE INTO character_artifacts (character_id, artifact_id, artifact_order)
SELECT character_id, artifact_id, artifact_order FROM artifacts;

-- artifacts 는 이제 공용 목록
ALTER TABLE artifacts
    ADD COLUMN grade VARCHAR(20) NULL COMMENT '희귀/영웅/전설' AFTER name,
    ADD COLUMN description TEXT NULL COMMENT '플레이버 텍스트' AFTER icon_url;

ALTER TABLE artifacts DROP COLUMN character_id;
ALTER TABLE artifacts DROP COLUMN artifact_order;
ALTER TABLE artifacts ADD UNIQUE KEY uk_artifact_name (name);
