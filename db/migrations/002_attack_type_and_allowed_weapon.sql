-- 공격 타입(관통/타격 등): 클래스 기본값 + 스킬별로 다를 때만 스킬에 저장
ALTER TABLE classes
    ADD COLUMN attack_type VARCHAR(20) NULL COMMENT '공격 타입 (관통/타격 등)' AFTER defense_type;

ALTER TABLE skills
    ADD COLUMN attack_type    VARCHAR(20)  NULL COMMENT '스킬 공격 타입 (클래스 기본값과 다를 때)' AFTER area,
    ADD COLUMN allowed_weapon VARCHAR(100) NULL COMMENT '허용 무기' AFTER attack_type;
