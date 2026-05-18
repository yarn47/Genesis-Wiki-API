package com.genesis.wiki.repository

import com.genesis.wiki.entity.WikiClass
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

interface ClassRepository : JpaRepository<WikiClass, Int> {

    // Tier별 조회
    fun findAllByTierOrderByClassId(tier: Int): List<WikiClass>

    // 상위 클래스로 하위 클래스 조회
    fun findAllByParentClassClassId(parentClassId: Int): List<WikiClass>

    // 클래스 상세 (스킬 포함)
    @Query("""
        SELECT DISTINCT c FROM WikiClass c
        LEFT JOIN FETCH c.classSkills cs
        LEFT JOIN FETCH cs.skill
        WHERE c.classId = :id
    """)
    fun findDetailById(id: Int): WikiClass?

    // 이름 검색 (ClassTreeModal용)
    fun findAllByNameContaining(name: String): List<WikiClass>
}