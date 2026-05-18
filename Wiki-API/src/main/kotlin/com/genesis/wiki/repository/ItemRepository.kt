package com.genesis.wiki.repository

import com.genesis.wiki.entity.Equipment
import com.genesis.wiki.entity.EquipmentGrade
import com.genesis.wiki.entity.EquipmentType
import com.genesis.wiki.entity.ExclusiveWeapon
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

interface EquipmentRepository : JpaRepository<Equipment, Int> {

    fun findAllByType(type: EquipmentType): List<Equipment>
    fun findAllByGrade(grade: EquipmentGrade): List<Equipment>
    fun findAllBySetName(setName: String): List<Equipment>
    fun findAllByNameContaining(name: String): List<Equipment>

    @Query("""
        SELECT DISTINCT e FROM Equipment e
        LEFT JOIN FETCH e.effects ef
        LEFT JOIN FETCH ef.levels
        WHERE e.equipmentId = :id
    """)
    fun findDetailById(id: Int): Equipment?
}

interface ExclusiveWeaponRepository : JpaRepository<ExclusiveWeapon, Int> {

    fun findAllByNameContaining(name: String): List<ExclusiveWeapon>
    fun findByName(name: String): ExclusiveWeapon?

    @Query("""
        SELECT DISTINCT w FROM ExclusiveWeapon w
        LEFT JOIN FETCH w.effects e
        LEFT JOIN FETCH e.levels
        WHERE w.weaponId = :id
    """)
    fun findDetailById(id: Int): ExclusiveWeapon?
}