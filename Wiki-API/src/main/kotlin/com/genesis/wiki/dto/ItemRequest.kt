package com.genesis.wiki.dto

// ─── 장비 ────────────────────────────────────────────────

data class EquipmentRequest(
    val name: String,
    val type: String,               // helmet/armor/gloves/boots/accessory
    val defenseType: String? = null, // light/medium/heavy (방어구만)
    val grade: String,              // rare/hero/legend
    val baseStats: String? = null,  // JSON 문자열
    val extraStats: String? = null,
    val setName: String? = null,
    val setEffect2: String? = null,
    val setEffect4: String? = null,
    val description: String? = null,
    val iconUrl: String? = null,
    val effects: List<EquipmentEffectRequest> = emptyList()
)

data class EquipmentEffectRequest(
    val effectName: String,
    val effectType: String = "normal", // normal/exclusive
    val baseEffect: String? = null,
    val iconUrl: String? = null,
    val levels: List<EffectLevelRequest> = emptyList()
)

data class EffectLevelRequest(
    val breakthroughStep: Int,
    val effectText: String? = null
)

// ─── 전용무기 ─────────────────────────────────────────────

data class ExclusiveWeaponRequest(
    val name: String,
    val weaponType: String? = null,
    val grade: String,              // rare/hero/legend
    val baseStats: String? = null,
    val extraStats: String? = null,
    val description: String? = null,
    val iconUrl: String? = null,
    val effects: List<WeaponEffectRequest> = emptyList()
)

data class WeaponEffectRequest(
    val effectName: String,
    val effectType: String = "normal", // normal/exclusive
    val baseEffect: String? = null,
    val iconUrl: String? = null,
    val levels: List<EffectLevelRequest> = emptyList()
)