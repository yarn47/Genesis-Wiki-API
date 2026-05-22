package com.genesis.wiki.dto

// ─── 캐릭터 기본 ──────────────────────────────────────────

data class CharacterRequest(
    val name: String,
    val grade: String,              // rare/hero/legend/outer
    val faction: String,            // geysir/pendragon/independent/astania/zephyrfalcon/dagal
    val element: String,            // light/dark/fire/crystal/nature
    val exclusiveWeaponId: Int? = null,
    val birthYear: String? = null,
    val height: String? = null,
    val cv: String? = null,
    val profileText: String? = null,
    val thumbnailUrl: String? = null,
    val portraitUrl: String? = null,
    val fullImageUrl: String? = null,
    val isPublished: Boolean = false,
    val stats: CharacterStatsRequest? = null,
    val classTreeIds: List<ClassTreeNodeRequest> = emptyList(),
    val passive: PassiveRequest? = null,
    val ultimate: UltimateRequest? = null,
    val artifacts: List<ArtifactRequest> = emptyList()
)

data class CharacterStatsRequest(
    val hp: Long? = null,
    val attack: Int? = null,
    val defense: Int? = null,
    val critRate: Int? = null,
    val critDamage: Int? = null,
    val physPen: Int? = null,
    val magicPen: Int? = null,
    val effectResist: Int? = null
)

data class ClassTreeNodeRequest(
    val classId: Int,
    val orderInTier: Int? = null
)

// ─── 고유 패시브 ──────────────────────────────────────────

data class PassiveRequest(
    val name: String,
    val iconUrl: String? = null,
    val levels: List<PassiveLevelRequest> = emptyList()
)

data class PassiveLevelRequest(
    val unlockType: String,   // awaken/manifest
    val unlockStep: Int,
    val effectText: String? = null
)

// ─── 필살기 ───────────────────────────────────────────────

data class UltimateRequest(
    val name: String,
    val iconUrl: String? = null,
    val levels: List<UltimateLevelRequest> = emptyList()
)

data class UltimateLevelRequest(
    val manifestStep: Int,    // 0/1/3/5
    val tpCost: Int? = null,
    val rangeMin: Int? = null,
    val rangeMax: Int? = null,
    val cooldown: Int? = null,
    val effectText: String? = null
)

// ─── 아티팩트 ─────────────────────────────────────────────

data class ArtifactRequest(
    val name: String,
    val artifactOrder: Int,
    val iconUrl: String? = null,
    val levels: List<ArtifactLevelRequest> = emptyList()
)

data class ArtifactLevelRequest(
    val manifestStep: Int,    // 3/4/5/6
    val effectText: String? = null
)