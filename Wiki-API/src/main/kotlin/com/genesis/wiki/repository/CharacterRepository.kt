package com.genesis.wiki.repository

import com.genesis.wiki.entity.Character
import com.genesis.wiki.entity.Element
import com.genesis.wiki.entity.Faction
import com.genesis.wiki.entity.Grade
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface CharacterRepository : JpaRepository<Character, Int> {

    fun findAllByIsPublishedTrue(): List<Character>
    fun findAllByGradeAndIsPublishedTrue(grade: Grade): List<Character>
    fun findAllByFactionAndIsPublishedTrue(faction: Faction): List<Character>
    fun findAllByElementAndIsPublishedTrue(element: Element): List<Character>
    fun findAllByNameContainingAndIsPublishedTrue(name: String): List<Character>
    fun findAllByOrderByCreatedAtDesc(): List<Character>
    fun findAllByNameContaining(name: String): List<Character>

    // 공개용 상세 (isPublished = true)
    @Query("""
        SELECT DISTINCT c FROM Character c
        LEFT JOIN FETCH c.stats
        LEFT JOIN FETCH c.skins
        LEFT JOIN FETCH c.classTree ct
        LEFT JOIN FETCH ct.clazz cl
        LEFT JOIN FETCH cl.classSkills cs
        LEFT JOIN FETCH cs.skill
        LEFT JOIN FETCH c.passives p
        LEFT JOIN FETCH p.levels
        LEFT JOIN FETCH c.artifacts a
        LEFT JOIN FETCH a.levels
        LEFT JOIN FETCH c.manifestations m
        LEFT JOIN FETCH m.ultimate u
        LEFT JOIN FETCH u.levels
        LEFT JOIN FETCH c.exclusiveWeapon w
        LEFT JOIN FETCH w.effects e
        LEFT JOIN FETCH e.levels
        WHERE c.characterId = :id AND c.isPublished = true
    """)
    fun findDetailById(@Param("id") id: Int): Character?

    // 관리자용 상세 (비발행 포함)
    @Query("""
        SELECT DISTINCT c FROM Character c
        LEFT JOIN FETCH c.stats
        LEFT JOIN FETCH c.skins
        LEFT JOIN FETCH c.classTree ct
        LEFT JOIN FETCH ct.clazz cl
        LEFT JOIN FETCH cl.classSkills cs
        LEFT JOIN FETCH cs.skill
        LEFT JOIN FETCH c.passives p
        LEFT JOIN FETCH p.levels
        LEFT JOIN FETCH c.artifacts a
        LEFT JOIN FETCH a.levels
        LEFT JOIN FETCH c.manifestations m
        LEFT JOIN FETCH m.ultimate u
        LEFT JOIN FETCH u.levels
        LEFT JOIN FETCH c.exclusiveWeapon w
        LEFT JOIN FETCH w.effects e
        LEFT JOIN FETCH e.levels
        WHERE c.characterId = :id 리
    """)
    fun findAdminDetailById(@Param("id") id: Int): Character?
}