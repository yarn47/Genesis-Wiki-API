package com.genesis.wiki.repository

import com.genesis.wiki.entity.Character
import com.genesis.wiki.entity.Element
import com.genesis.wiki.entity.Faction
import com.genesis.wiki.entity.Grade
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface CharacterRepository : JpaRepository<Character, Int> {

    // 발행된 캐릭터 전체 목록
    fun findAllByIsPublishedTrue(): List<Character>

    // 등급별 필터
    fun findAllByGradeAndIsPublishedTrue(grade: Grade): List<Character>

    // 진영별 필터
    fun findAllByFactionAndIsPublishedTrue(faction: Faction): List<Character>

    // 속성별 필터
    fun findAllByElementAndIsPublishedTrue(element: Element): List<Character>

    // 이름 검색
    fun findAllByNameContainingAndIsPublishedTrue(name: String): List<Character>

    // 캐릭터 상세 (연관 데이터 한번에 로드)
    @Query("""
        SELECT DISTINCT c FROM Character c
        LEFT JOIN FETCH c.stats
        LEFT JOIN FETCH c.skins
        LEFT JOIN FETCH c.classTree ct
        LEFT JOIN FETCH ct.clazz
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

    // 관리자용 전체 목록 (비발행 포함)
    fun findAllByOrderByCreatedAtDesc(): List<Character>
}