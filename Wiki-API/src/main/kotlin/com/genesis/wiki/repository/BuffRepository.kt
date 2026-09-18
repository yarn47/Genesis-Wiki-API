package com.genesis.wiki.repository

import com.genesis.wiki.entity.Buff
import com.genesis.wiki.entity.Debuff
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

// 버프/디버프를 쓰는 캐릭터 한 줄 (네이티브 조회 결과)
interface EffectUserRow {
    val effectId: Int
    val characterId: Int
    val characterName: String
    val thumbnailUrl: String?
}

// 캐릭터가 가진 모든 효과 텍스트 (고유 패시브·필살기·아티팩트·전용무기·클래스 스킬/패시브)
private const val CHARACTER_EFFECT_TEXTS = """
    SELECT cp.character_id AS character_id, cpl.effect_text AS t
      FROM character_passives cp JOIN character_passive_levels cpl ON cpl.passive_id = cp.passive_id
    UNION ALL
    SELECT cm.character_id, usl.effect_text
      FROM character_manifestation cm JOIN ultimate_skill_levels usl ON usl.ultimate_id = cm.ultimate_id
    UNION ALL
    SELECT a.character_id, al.effect_text
      FROM artifacts a JOIN artifact_levels al ON al.artifact_id = a.artifact_id
    UNION ALL
    SELECT ch.character_id, wel.effect_text
      FROM characters ch
      JOIN exclusive_weapon_effects we ON we.weapon_id = ch.exclusive_weapon_id
      JOIN exclusive_weapon_effect_levels wel ON wel.effect_id = we.effect_id
    UNION ALL
    SELECT cct.character_id, s.effect_text
      FROM character_class_tree cct
      JOIN class_skills cs ON cs.class_id = cct.class_id
      JOIN skills s ON s.skill_id = cs.skill_id
    UNION ALL
    SELECT cct.character_id, cl.passive1_lv1
      FROM character_class_tree cct JOIN classes cl ON cl.class_id = cct.class_id
    UNION ALL
    SELECT cct.character_id, cl.passive1_lv2
      FROM character_class_tree cct JOIN classes cl ON cl.class_id = cct.class_id
"""

interface BuffRepository : JpaRepository<Buff, Int> {

    fun findByName(name: String): Buff?
    fun findAllByNameContaining(name: String): List<Buff>
    fun findAllByNameIn(names: List<String>): List<Buff>
    fun findAllByHasLevelsTrue(): List<Buff>

    @Query("""
        SELECT DISTINCT b FROM Buff b
        LEFT JOIN FETCH b.levels
        LEFT JOIN FETCH b.tags
        LEFT JOIN FETCH b.sources
        WHERE b.buffId = :id
    """)
    fun findDetailById(id: Int): Buff?

    @Query("""
        SELECT DISTINCT b FROM Buff b
        LEFT JOIN FETCH b.levels
        LEFT JOIN FETCH b.tags
        LEFT JOIN FETCH b.sources
        WHERE b.name IN :names
    """)
    fun findAllWithDetailByNameIn(names: List<String>): List<Buff>

    // [버프명]{green} / [버프명 3]{green} 처럼 이름이 박힌 텍스트를 가진 캐릭터를 찾는다
    @Query(nativeQuery = true, value = """
        SELECT b.buff_id AS effectId, c.character_id AS characterId,
               c.name AS characterName, c.thumbnail_url AS thumbnailUrl
        FROM buffs b
        JOIN ($CHARACTER_EFFECT_TEXTS) src
          ON src.t LIKE CONCAT('%[', b.name, ']%') OR src.t LIKE CONCAT('%[', b.name, ' %')
        JOIN characters c ON c.character_id = src.character_id AND c.is_published = 1
        GROUP BY b.buff_id, c.character_id, c.name, c.thumbnail_url
        ORDER BY b.buff_id, c.character_id
    """)
    fun findUsingCharacters(): List<EffectUserRow>
}

interface DebuffRepository : JpaRepository<Debuff, Int> {

    fun findByName(name: String): Debuff?
    fun findAllByNameContaining(name: String): List<Debuff>
    fun findAllByNameIn(names: List<String>): List<Debuff>
    fun findAllByHasLevelsTrue(): List<Debuff>

    @Query("""
        SELECT DISTINCT d FROM Debuff d
        LEFT JOIN FETCH d.levels
        LEFT JOIN FETCH d.tags
        LEFT JOIN FETCH d.sources
        WHERE d.debuffId = :id
    """)
    fun findDetailById(id: Int): Debuff?

    @Query("""
        SELECT DISTINCT d FROM Debuff d
        LEFT JOIN FETCH d.levels
        LEFT JOIN FETCH d.tags
        LEFT JOIN FETCH d.sources
        WHERE d.name IN :names
    """)
    fun findAllWithDetailByNameIn(names: List<String>): List<Debuff>

    @Query(nativeQuery = true, value = """
        SELECT d.debuff_id AS effectId, c.character_id AS characterId,
               c.name AS characterName, c.thumbnail_url AS thumbnailUrl
        FROM debuffs d
        JOIN ($CHARACTER_EFFECT_TEXTS) src
          ON src.t LIKE CONCAT('%[', d.name, ']%') OR src.t LIKE CONCAT('%[', d.name, ' %')
        JOIN characters c ON c.character_id = src.character_id AND c.is_published = 1
        GROUP BY d.debuff_id, c.character_id, c.name, c.thumbnail_url
        ORDER BY d.debuff_id, c.character_id
    """)
    fun findUsingCharacters(): List<EffectUserRow>
}