-- 주문력
ALTER TABLE character_stats
    ADD COLUMN spell_attack INT NULL COMMENT '주문력' AFTER attack;
