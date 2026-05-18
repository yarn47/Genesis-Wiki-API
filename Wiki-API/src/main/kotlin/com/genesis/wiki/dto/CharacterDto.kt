package com.genesis.wiki.dto

// ─── 공통 ─────────────────────────────────────────────────
data class SkillDto(
    val skillId: Int,
    val name: String,
    val type: String,
    val tpCost: Int?,
    val rangeMin: Int?,
    val rangeMax: Int?,
    val area: String?,
    val cooldown: Int?,
    val effectText: String?,
    val iconUrl: String?
)

data class TagDto(
    val tagId: Int,
    val name: String,
    val color: String
)

// ─── 캐릭터 목록 ──────────────────────────────────────────
data class CharacterSummaryDto(
    val characterId: Int,
    val name: String,
    val grade: String,
    val faction: String,
    val element: String,
    val thumbnailUrl: String?
)

// ─── 캐릭터 상세 ──────────────────────────────────────────
data class CharacterDetailDto(
    val characterId: Int,
    val name: String,
    val grade: String,
    val faction: String,
    val element: String,
    val birthYear: String?,
    val height: String?,
    val cv: String?,
    val profileText: String?,
    val thumbnailUrl: String?,
    val portraitUrl: String?,
    val fullImageUrl: String?,
    val stats: CharacterStatsDto?,
    val skins: List<CharacterSkinDto>,
    val classTree: List<ClassTreeNodeDto>,
    val passive: CharacterPassiveDto?,
    val ultimateSkill: UltimateSkillDto?,
    val artifacts: List<ArtifactDto>,
    val manifestations: List<CharacterManifestationDto>,
    val exclusiveWeapon: ExclusiveWeaponDto?,
    val relatedBuffs: List<BuffDto>,
    val relatedDebuffs: List<DebuffDto>
)

data class CharacterStatsDto(
    val hp: Long?,
    val attack: Int?,
    val defense: Int?,
    val critRate: Int?,
    val critDamage: Int?,
    val physPen: Int?,
    val magicPen: Int?,
    val effectResist: Int?
)

data class CharacterSkinDto(
    val skinId: Int,
    val skinName: String,
    val isDefault: Boolean,
    val thumbnailUrl: String?,
    val portraitUrl: String?,
    val fullImageUrl: String?,
    val howToObtain: String?,
    val releaseDate: String?
)

data class ClassTreeNodeDto(
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
    val orderInTier: Int?,
    val iconUrl: String?,
    val passive1Name: String?,
    val passive1Lv1: String?,
    val passive1Lv2: String?,
    val skills: List<SkillDto>
)

data class CharacterPassiveDto(
    val passiveId: Int,
    val name: String,
    val iconUrl: String?,
    val levels: List<CharacterPassiveLevelDto>
)

data class CharacterPassiveLevelDto(
    val unlockType: String,
    val unlockStep: Int,
    val effectText: String?
)

data class UltimateSkillDto(
    val ultimateId: Int,
    val name: String,
    val iconUrl: String?,
    val levels: List<UltimateSkillLevelDto>
)

data class UltimateSkillLevelDto(
    val manifestStep: Int,
    val tpCost: Int?,
    val rangeMin: Int?,
    val rangeMax: Int?,
    val cooldown: Int?,
    val effectText: String?
)

data class ArtifactDto(
    val artifactId: Int,
    val name: String,
    val artifactOrder: Int,
    val iconUrl: String?,
    val levels: List<ArtifactLevelDto>
)

data class ArtifactLevelDto(
    val manifestStep: Int,
    val effectText: String?
)

data class CharacterManifestationDto(
    val manifestLevel: Int,
    val ultimateId: Int?,
    val passiveId: Int?,
    val artifact1Id: Int?,
    val artifact2Id: Int?,
    val artifact3Id: Int?,
    val artifact4Id: Int?
)

data class ExclusiveWeaponDto(
    val weaponId: Int,
    val name: String,
    val weaponType: String?,
    val grade: String,
    val baseStats: String?,
    val extraStats: String?,
    val description: String?,
    val iconUrl: String?,
    val effects: List<ExclusiveWeaponEffectDto>
)

data class ExclusiveWeaponEffectDto(
    val effectId: Int,
    val effectName: String,
    val effectType: String,
    val baseEffect: String?,
    val iconUrl: String?,
    val levels: List<WeaponEffectLevelDto>
)

data class WeaponEffectLevelDto(
    val breakthroughStep: Int,
    val effectText: String?
)