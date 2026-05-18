package com.genesis.wiki.dto

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
    val sources: List<BuffSourceDto>
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
    val sources: List<DebuffSourceDto>
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