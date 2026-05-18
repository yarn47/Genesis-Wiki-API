package com.genesis.wiki.dto

data class BuffRequest(
    val name: String,
    val description: String?,
    val iconUrl: String?,
    val duration: Int?,
    val maxStack: Int = 1,
    val hasLevels: Boolean = false,
    val levels: List<BuffLevelRequest> = emptyList(),
    val tagIds: List<Int> = emptyList()
)

data class BuffLevelRequest(
    val level: Int,
    val levelName: String?,
    val effectText: String?,
    val duration: Int? = null,    // 추가
    val maxStack: Int? = null     // 추가
)

data class DebuffRequest(
    val name: String,
    val description: String?,
    val iconUrl: String?,
    val duration: Int?,
    val maxStack: Int = 1,
    val hasLevels: Boolean = false,
    val levels: List<BuffLevelRequest> = emptyList(),
    val tagIds: List<Int> = emptyList()
)

data class TagRequest(
    val name: String,
    val color: String = "gray"
)