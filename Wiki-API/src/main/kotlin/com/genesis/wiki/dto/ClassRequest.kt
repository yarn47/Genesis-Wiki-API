package com.genesis.wiki.dto

data class ClassRequest(
    val name: String,
    val tier: Int,
    val weaponType: String? = null,
    val defenseType: String? = null,      // "light" | "medium" | "heavy"
    val attackType: String? = null,       // "관통" | "타격" 등
    val attackRange: Int? = null,
    val moveRange: Int? = null,
    val baseHp: Int? = null,
    val baseAttack: Int? = null,
    val parentClassId: Int? = null,
    val description: String? = null,
    val iconUrl: String? = null,
    val passive1Name: String? = null,
    val passive1Lv1: String? = null,
    val passive1Lv2: String? = null,
    val passive1IconUrl: String? = null,
    val skills: List<SkillRequest> = emptyList()
)

data class SkillRequest(
    val name: String,
    val type: String = "active",          // "active" | "passive"
    val tpCost: Int? = null,
    val rangeMin: Int? = null,
    val rangeMax: Int? = null,
    val area: String? = null,
    val attackType: String? = null,       // 클래스 기본값과 다를 때만
    val allowedWeapon: String? = null,
    val cooldown: Int? = null,
    val effectText: String? = null,
    val iconUrl: String? = null,
    val unlockOrder: Int? = null,
    val tagIds: List<Int> = emptyList()
)