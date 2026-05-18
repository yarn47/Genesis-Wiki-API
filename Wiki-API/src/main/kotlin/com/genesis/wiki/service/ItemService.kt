package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.Equipment
import com.genesis.wiki.entity.ExclusiveWeapon
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
    // 장비 목록
    fun getEquipmentList(): List<EquipmentSummaryDto> =
        equipmentRepository.findAll().map { it.toSummaryDto() }

    // 장비 상세
    fun getEquipmentDetail(id: Int): EquipmentDetailDto =
        equipmentRepository.findDetailById(id)?.toDetailDto()
            ?: throw NoSuchElementException("장비를 찾을 수 없습니다: $id")

    // 전용무기 상세
    fun getExclusiveWeaponDetail(id: Int): ExclusiveWeaponDto =
        exclusiveWeaponRepository.findDetailById(id)?.toDto()
            ?: throw NoSuchElementException("전용무기를 찾을 수 없습니다: $id")

    // 전용무기 검색 (캐릭터 연결용)
    fun searchExclusiveWeapons(name: String): List<ExclusiveWeaponDto> =
        exclusiveWeaponRepository.findAllByNameContaining(name).map { it.toDto() }

    // ─── Entity → DTO ───────────────────────────────────

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