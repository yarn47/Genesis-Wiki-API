-- 아우터원 전용 액티브는 일반 필살기와 독립적인 단계/효과를 가진다.
ALTER TABLE characters
    ADD COLUMN outer_skill_id INT NULL,
    ADD CONSTRAINT fk_character_outer_skill FOREIGN KEY (outer_skill_id)
        REFERENCES ultimate_skills (ultimate_id) ON DELETE SET NULL,
    ADD UNIQUE KEY uk_character_outer_skill (outer_skill_id);
