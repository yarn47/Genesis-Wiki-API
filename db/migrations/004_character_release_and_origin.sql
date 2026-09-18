-- 출시일 · 출현작 (원작 시리즈)
ALTER TABLE characters
    ADD COLUMN release_date DATE NULL COMMENT '출시일' AFTER cv,
    ADD COLUMN appeared_in VARCHAR(100) NULL COMMENT '출현작 (원작)' AFTER release_date;
