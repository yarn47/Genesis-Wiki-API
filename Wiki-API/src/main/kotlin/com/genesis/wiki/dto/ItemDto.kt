package com.genesis.wiki.dto

data class EquipmentSummaryDto(
    val equipmentId: Int,
    val name: String,
    val type: String,
    val grade: String,
    val iconUrl: String?,
    val setName: String?
)

data class EquipmentDetailDto(
    val equipmentId: Int,
    val name: String,
    val type: String,
    val defenseType: String?,
    val grade: String,
    val baseStats: String?,
    val extraStats: String?,
    val setName: String?,
    val setEffect2: String?,
    val setEffect4: String?,
    val description: String?,
    val iconUrl: String?,
    val effects: List<EquipmentEffectDto>
)

data class EquipmentEffectDto(
    val eqEffectId: Int,
    val effectName: String,
    val effectType: String,
    val baseEffect: String?,
    val iconUrl: String?,
    val levels: List<EquipmentEffectLevelDto>
)

data class EquipmentEffectLevelDto(
    val breakthroughStep: Int,
    val effectText: String?
)