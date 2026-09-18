package com.genesis.wiki.repository

import com.genesis.wiki.entity.Buff
import com.genesis.wiki.entity.Debuff
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

// 버프/디버프를 쓰는 주체 한 줄 (네이티브 조회 결과)
interface EffectUserRow {
    val effectId: Int
    val ownerKind: String     // C = 캐릭터, W = 무기
    val ownerId: Int
    val ownerName: String
    val iconUrl: String?
}

// 효과 텍스트와 그 주인
// 캐릭터의 고유 패시브·필살기·아티팩트·클래스 스킬/패시브와 전용무기의 "캐릭터 전용" 효과는 캐릭터 것,
// 무기의 공용(일반) 옵션은 다른 무기에도 붙을 수 있으니 무기 것으로 본다
private const val EFFECT_TEXT_OWNERS = """
    SELECT 'C' AS owner_kind, cp.character_id AS owner_id, cpl.effect_text AS t
      FROM character_passives cp JOIN character_passive_levels cpl ON cpl.passive_id = cp.passive_id
    UNION ALL
    SELECT 'C', cm.character_id, usl.effect_text
      FROM character_manifestation cm JOIN ultimate_skill_levels usl ON usl.ultimate_id = cm.ultimate_id
    UNION ALL
    SELECT 'C', a.character_id, al.effect_text
      FROM artifacts a JOIN artifact_levels al ON al.artifact_id = a.artifact_id
    UNION ALL
    SELECT 'C', ch.character_id, wel.effect_text
      FROM characters ch
      JOIN exclusive_weapon_effects we ON we.weapon_id = ch.exclusive_weapon_id AND we.effect_type = 'exclusive'
      JOIN exclusive_weapon_effect_levels wel ON wel.effect_id = we.effect_id
    UNION ALL
    SELECT 'W', we.weapon_id, wel.effect_text
      FROM exclusive_weapon_effects we
      JOIN exclusive_weapon_effect_levels wel ON wel.effect_id = we.effect_id
     WHERE we.effect_type = 'normal'
    UNION ALL
    SELECT 'W', we.weapon_id, we.base_effect
      FROM exclusive_weapon_effects we WHERE we.effect_type = 'normal'
    UNION ALL
    SELECT 'C', cct.character_id, s.effect_text
      FROM character_class_tree cct
      JOIN class_skills cs ON cs.class_id = cct.class_id
      JOIN skills s ON s.skill_id = cs.skill_id
    UNION ALL
    SELECT 'C', cct.character_id, cl.passive1_lv1
      FROM character_class_tree cct JOIN classes cl ON cl.class_id = cct.class_id
    UNION ALL
    SELECT 'C', cct.character_id, cl.passive1_lv2
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

    // [버프명]{green} / [버프명 3]{green} 처럼 이름이 박힌 텍스트의 주인을 찾는다
    @Query(nativeQuery = true, value = """
        SELECT e.buff_id AS effectId, src.owner_kind AS ownerKind, src.owner_id AS ownerId,
               COALESCE(c.name, w.name) AS ownerName,
               COALESCE(c.thumbnail_url, w.icon_url) AS iconUrl
        FROM buffs e
        JOIN ($EFFECT_TEXT_OWNERS) src
          ON src.t LIKE CONCAT('%[', e.name, ']%') OR src.t LIKE CONCAT('%[', e.name, ' %')
        LEFT JOIN characters c ON src.owner_kind = 'C' AND c.character_id = src.owner_id AND c.is_published = 1
        LEFT JOIN exclusive_weapons w ON src.owner_kind = 'W' AND w.weapon_id = src.owner_id
        WHERE c.character_id IS NOT NULL OR w.weapon_id IS NOT NULL
        GROUP BY e.buff_id, src.owner_kind, src.owner_id, COALESCE(c.name, w.name),
                 COALESCE(c.thumbnail_url, w.icon_url)
        ORDER BY e.buff_id, src.owner_kind, src.owner_id
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

    // [디버프명]{green} / [버프명 3]{green} 처럼 이름이 박힌 텍스트의 주인을 찾는다
    @Query(nativeQuery = true, value = """
        SELECT e.debuff_id AS effectId, src.owner_kind AS ownerKind, src.owner_id AS ownerId,
               COALESCE(c.name, w.name) AS ownerName,
               COALESCE(c.thumbnail_url, w.icon_url) AS iconUrl
        FROM debuffs e
        JOIN ($EFFECT_TEXT_OWNERS) src
          ON src.t LIKE CONCAT('%[', e.name, ']%') OR src.t LIKE CONCAT('%[', e.name, ' %')
        LEFT JOIN characters c ON src.owner_kind = 'C' AND c.character_id = src.owner_id AND c.is_published = 1
        LEFT JOIN exclusive_weapons w ON src.owner_kind = 'W' AND w.weapon_id = src.owner_id
        WHERE c.character_id IS NOT NULL OR w.weapon_id IS NOT NULL
        GROUP BY e.debuff_id, src.owner_kind, src.owner_id, COALESCE(c.name, w.name),
                 COALESCE(c.thumbnail_url, w.icon_url)
        ORDER BY e.debuff_id, src.owner_kind, src.owner_id
    """)
    fun findUsingCharacters(): List<EffectUserRow>
}