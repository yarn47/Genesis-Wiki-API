-- 클래스 패시브 아이콘
ALTER TABLE classes
    ADD COLUMN passive1_icon_url VARCHAR(255) NULL COMMENT '클래스 패시브 아이콘' AFTER passive1_lv2;
