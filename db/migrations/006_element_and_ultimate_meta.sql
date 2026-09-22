-- 속성(빙한/화염/전격) + 필살기에도 스킬과 같은 태그·공격타입·범위
-- 게임에서 스킬 이름 옆 검은 원형 문양 = 공격 타입, 파란 ✳ = 속성.

ALTER TABLE skills
    ADD COLUMN element VARCHAR(20) NULL COMMENT '속성 (빙한/화염/전격)' AFTER attack_type;

ALTER TABLE buffs
    ADD COLUMN element VARCHAR(20) NULL COMMENT '속성 (빙한/화염/전격)' AFTER icon_url;

ALTER TABLE debuffs
    ADD COLUMN element VARCHAR(20) NULL COMMENT '속성 (빙한/화염/전격)' AFTER icon_url;

-- 필살기는 이름·아이콘만 있었다. 스킬과 같은 수준으로 맞춘다.
ALTER TABLE ultimate_skills
    ADD COLUMN area        VARCHAR(20) NULL COMMENT '범위 (단일/광역)'        AFTER icon_url,
    ADD COLUMN attack_type VARCHAR(20) NULL COMMENT '공격 타입 (참격/관통/타격/마법/절단)' AFTER area,
    ADD COLUMN element     VARCHAR(20) NULL COMMENT '속성 (빙한/화염/전격)'    AFTER attack_type;

CREATE TABLE IF NOT EXISTS ultimate_skill_tag_map (
    ultimate_id INT NOT NULL,
    tag_id      INT NOT NULL,
    PRIMARY KEY (ultimate_id, tag_id),
    CONSTRAINT fk_ustm_ultimate FOREIGN KEY (ultimate_id) REFERENCES ultimate_skills (ultimate_id) ON DELETE CASCADE,
    CONSTRAINT fk_ustm_tag      FOREIGN KEY (tag_id)      REFERENCES tags (tag_id)                 ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='필살기 태그';
