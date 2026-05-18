package com.genesis.wiki.dto

data class ClassSummaryDto(
    val classId: Int,
    val name: String,
    val tier: Int,
    val weaponType: String?,
    val defenseType: String?,
    val iconUrl: String?,
    val parentClassId: Int?
)

data class ClassDetailDto(
    val classId: Int,
    val name: String,
    val tier: Int,
    val weaponType: String?,
    val defenseType: String?,
    val attackRange: Int?,
    val moveRange: Int?,
    val baseHp: Int?,
    val baseAttack: Int?,
    val parentClassId: Int?,
    val description: String?,
    val iconUrl: String?,
    val passive1Name: String?,
    val passive1Lv1: String?,
    val passive1Lv2: String?,
    val skills: List<SkillDto>  // CharacterDto.kt의 SkillDto 사용
)