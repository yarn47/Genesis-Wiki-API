package com.genesis.wiki.repository

import com.genesis.wiki.entity.Buff
import com.genesis.wiki.entity.Debuff
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

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
}