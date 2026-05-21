package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.*
import com.genesis.wiki.repository.EquipmentRepository
import com.genesis.wiki.repository.ExclusiveWeaponRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
@Transactional(readOnly = true)
class ItemService(
    private val equipmentRepository: EquipmentRepository,
    private val exclusiveWeaponRepository: ExclusiveWeaponRepository
) {
    // ─── 장비 조회 ───────────────────────────────────────────

    fun getEquipmentList(): List<EquipmentSummaryDto> =
        equipmentRepository.findAll().map { it.toSummaryDto() }

    fun getEquipmentDetail(id: Int): EquipmentDetailDto =
        equipmentRepository.findDetailById(id)?.toDetailDto()
            ?: throw NoSuchElementException("장비를 찾을 수 없습니다: $id")

    // ─── 장비 생성 ───────────────────────────────────────────

    @Transactional
    fun createEquipment(req: EquipmentRequest): EquipmentDetailDto {
        val equipment = Equipment(
            name = req.name,
            type = EquipmentType.valueOf(req.type),
            defenseType = req.defenseType?.let { DefenseType.valueOf(it) },
            grade = EquipmentGrade.valueOf(req.grade),
            baseStats = req.baseStats,
            extraStats = req.extraStats,
            setName = req.setName,
            setEffect2 = req.setEffect2,
            setEffect4 = req.setEffect4,
            description = req.description,
            iconUrl = req.iconUrl
        )
        val saved = equipmentRepository.save(equipment)
        req.effects.forEach { effectReq ->
            val effect = EquipmentEffect(
                equipment = saved,
                effectName = effectReq.effectName,
                effectType = EffectType.valueOf(effectReq.effectType),
                baseEffect = effectReq.baseEffect,
                iconUrl = effectReq.iconUrl
            )
            effectReq.levels.forEach { lvReq ->
                effect.levels.add(
                    EquipmentEffectLevel(effect = effect, breakthroughStep = lvReq.breakthroughStep, effectText = lvReq.effectText)
                )
            }
            saved.effects.add(effect)
        }
        equipmentRepository.saveAndFlush(saved)
        return equipmentRepository.findDetailById(saved.equipmentId)!!.toDetailDto()
    }

    // ─── 장비 수정 ───────────────────────────────────────────

    @Transactional
    fun updateEquipment(id: Int, req: EquipmentRequest): EquipmentDetailDto {
        val equipment = equipmentRepository.findDetailById(id)
            ?: throw NoSuchElementException("장비를 찾을 수 없습니다: $id")

        equipment.name = req.name
        equipment.type = EquipmentType.valueOf(req.type)
        equipment.defenseType = req.defenseType?.let { DefenseType.valueOf(it) }
        equipment.grade = EquipmentGrade.valueOf(req.grade)
        equipment.baseStats = req.baseStats
        equipment.extraStats = req.extraStats
        equipment.setName = req.setName
        equipment.setEffect2 = req.setEffect2
        equipment.setEffect4 = req.setEffect4
        equipment.description = req.description
        equipment.iconUrl = req.iconUrl

        equipment.effects.clear()
        equipmentRepository.saveAndFlush(equipment)

        req.effects.forEach { effectReq ->
            val effect = EquipmentEffect(
                equipment = equipment,
                effectName = effectReq.effectName,
                effectType = EffectType.valueOf(effectReq.effectType),
                baseEffect = effectReq.baseEffect,
                iconUrl = effectReq.iconUrl
            )
            effectReq.levels.forEach { lvReq ->
                effect.levels.add(
                    EquipmentEffectLevel(effect = effect, breakthroughStep = lvReq.breakthroughStep, effectText = lvReq.effectText)
                )
            }
            equipment.effects.add(effect)
        }
        equipmentRepository.saveAndFlush(equipment)
        return equipmentRepository.findDetailById(id)!!.toDetailDto()
    }

    // ─── 장비 삭제 ───────────────────────────────────────────

    @Transactional
    fun deleteEquipment(id: Int) {
        val equipment = equipmentRepository.findById(id)
            .orElseThrow { NoSuchElementException("장비를 찾을 수 없습니다: $id") }
        equipmentRepository.delete(equipment)
    }

    // ─── 전용무기 조회 ───────────────────────────────────────

    fun getExclusiveWeaponList(): List<ExclusiveWeaponDto> =
        exclusiveWeaponRepository.findAll().map { it.toDto() }

    fun getExclusiveWeaponDetail(id: Int): ExclusiveWeaponDto =
        exclusiveWeaponRepository.findDetailById(id)?.toDto()
            ?: throw NoSuchElementException("전용무기를 찾을 수 없습니다: $id")

    fun searchExclusiveWeapons(name: String): List<ExclusiveWeaponDto> =
        exclusiveWeaponRepository.findAllByNameContaining(name).map { it.toDto() }

    // ─── 전용무기 생성 ───────────────────────────────────────

    @Transactional
    fun createExclusiveWeapon(req: ExclusiveWeaponRequest): ExclusiveWeaponDto {
        val weapon = ExclusiveWeapon(
            name = req.name,
            weaponType = req.weaponType,
            grade = EquipmentGrade.valueOf(req.grade),
            baseStats = req.baseStats,
            extraStats = req.extraStats,
            description = req.description,
            iconUrl = req.iconUrl
        )
        val saved = exclusiveWeaponRepository.save(weapon)
        req.effects.forEach { effectReq ->
            val effect = ExclusiveWeaponEffect(
                weapon = saved,
                effectName = effectReq.effectName,
                effectType = EffectType.valueOf(effectReq.effectType),
                baseEffect = effectReq.baseEffect,
                iconUrl = effectReq.iconUrl
            )
            effectReq.levels.forEach { lvReq ->
                effect.levels.add(
                    ExclusiveWeaponEffectLevel(effect = effect, breakthroughStep = lvReq.breakthroughStep, effectText = lvReq.effectText)
                )
            }
            saved.effects.add(effect)
        }
        exclusiveWeaponRepository.saveAndFlush(saved)
        return exclusiveWeaponRepository.findDetailById(saved.weaponId)!!.toDto()
    }

    // ─── 전용무기 수정 ───────────────────────────────────────

    @Transactional
    fun updateExclusiveWeapon(id: Int, req: ExclusiveWeaponRequest): ExclusiveWeaponDto {
        val weapon = exclusiveWeaponRepository.findDetailById(id)
            ?: throw NoSuchElementException("전용무기를 찾을 수 없습니다: $id")

        weapon.name = req.name
        weapon.weaponType = req.weaponType
        weapon.grade = EquipmentGrade.valueOf(req.grade)
        weapon.baseStats = req.baseStats
        weapon.extraStats = req.extraStats
        weapon.description = req.description
        weapon.iconUrl = req.iconUrl

        weapon.effects.clear()
        exclusiveWeaponRepository.saveAndFlush(weapon)

        req.effects.forEach { effectReq ->
            val effect = ExclusiveWeaponEffect(
                weapon = weapon,
                effectName = effectReq.effectName,
                effectType = EffectType.valueOf(effectReq.effectType),
                baseEffect = effectReq.baseEffect,
                iconUrl = effectReq.iconUrl
            )
            effectReq.levels.forEach { lvReq ->
                effect.levels.add(
                    ExclusiveWeaponEffectLevel(effect = effect, breakthroughStep = lvReq.breakthroughStep, effectText = lvReq.effectText)
                )
            }
            weapon.effects.add(effect)
        }
        exclusiveWeaponRepository.saveAndFlush(weapon)
        return exclusiveWeaponRepository.findDetailById(id)!!.toDto()
    }

    // ─── 전용무기 삭제 ───────────────────────────────────────

    @Transactional
    fun deleteExclusiveWeapon(id: Int) {
        val weapon = exclusiveWeaponRepository.findById(id)
            .orElseThrow { NoSuchElementException("전용무기를 찾을 수 없습니다: $id") }
        exclusiveWeaponRepository.delete(weapon)
    }

    // ─── Entity → DTO ───────────────────────────────────────

    private fun Equipment.toSummaryDto() = EquipmentSummaryDto(
        equipmentId = equipmentId, name = name,
        type = type.name, grade = grade.name,
        iconUrl = iconUrl, setName = setName
    )

    private fun Equipment.toDetailDto() = EquipmentDetailDto(
        equipmentId = equipmentId, name = name,
        type = type.name, defenseType = defenseType?.name,
        grade = grade.name, baseStats = baseStats,
        extraStats = extraStats, setName = setName,
        setEffect2 = setEffect2, setEffect4 = setEffect4,
        description = description, iconUrl = iconUrl,
        effects = effects.map { effect ->
            EquipmentEffectDto(
                eqEffectId = effect.eqEffectId,
                effectName = effect.effectName,
                effectType = effect.effectType.name,
                baseEffect = effect.baseEffect,
                iconUrl = effect.iconUrl,
                levels = effect.levels.sortedBy { it.breakthroughStep }.map {
                    EquipmentEffectLevelDto(it.breakthroughStep, it.effectText)
                }
            )
        }
    )

    private fun ExclusiveWeapon.toDto() = ExclusiveWeaponDto(
        weaponId = weaponId, name = name, weaponType = weaponType,
        grade = grade.name, baseStats = baseStats, extraStats = extraStats,
        description = description, iconUrl = iconUrl,
        effects = effects.map { effect ->
            ExclusiveWeaponEffectDto(
                effectId = effect.effectId,
                effectName = effect.effectName,
                effectType = effect.effectType.name,
                baseEffect = effect.baseEffect,
                iconUrl = effect.iconUrl,
                levels = effect.levels.sortedBy { it.breakthroughStep }.map {
                    WeaponEffectLevelDto(it.breakthroughStep, it.effectText)
                }
            )
        }
    )
}