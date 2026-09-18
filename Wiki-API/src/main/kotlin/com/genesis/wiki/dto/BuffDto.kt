package com.genesis.wiki.dto

// 버프/디버프를 쓰는 캐릭터 (툴팁·목록의 "사용자")
data class CharacterBriefDto(
    val characterId: Int,
    val name: String,
    val thumbnailUrl: String?
)

data class BuffDto(
    val buffId: Int,
    val name: String,
    val description: String?,
    val iconUrl: String?,
    val duration: Int?,
    val maxStack: Int?,
    val hasLevels: Boolean,
    val levels: List<BuffLevelDto>,
    val tags: List<TagDto>,
    val sources: List<BuffSourceDto>,
    val usedBy: List<CharacterBriefDto> = emptyList()
)

data class BuffLevelDto(
    val level: Int,
    val levelName: String?,
    val effectText: String?,
    val duration: Int?,
    val maxStack: Int?
)

data class BuffSourceDto(
    val sourceType: String,
    val sourceId: Int,
    val briefDesc: String?
)

data class DebuffDto(
    val debuffId: Int,
    val name: String,
    val description: String?,
    val iconUrl: String?,
    val duration: Int?,
    val maxStack: Int?,
    val hasLevels: Boolean,
    val levels: List<DebuffLevelDto>,
    val tags: List<TagDto>,
    val sources: List<DebuffSourceDto>,
    val usedBy: List<CharacterBriefDto> = emptyList()
)

data class DebuffLevelDto(
    val level: Int,
    val levelName: String?,
    val effectText: String?,
    val duration: Int?,
    val maxStack: Int?
)

data class DebuffSourceDto(
    val sourceType: String,
    val sourceId: Int,
    val briefDesc: String?
)