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
    // 컬렉션은 fetch join 하지 않는다 — 여러 컬렉션을 한 번에 조인하면 카티션 곱이 되어
    // (자드 기준 8만 행) 쿼리가 몇 초씩 걸린다. 컬렉션은 default_batch_fetch_size 로 묶어서 로딩.
    @Query("""
        SELECT c FROM Character c
        LEFT JOIN FETCH c.stats
        LEFT JOIN FETCH c.exclusiveWeapon
        WHERE c.characterId = :id AND c.isPublished = true
    """)
    fun findDetailById(@Param("id") id: Int): Character?

    // 관리자용 상세 (비발행 포함)
    @Query("""
        SELECT c FROM Character c
        LEFT JOIN FETCH c.stats
        LEFT JOIN FETCH c.exclusiveWeapon
        WHERE c.characterId = :id
    """)
    fun findAdminDetailById(@Param("id") id: Int): Character?
}