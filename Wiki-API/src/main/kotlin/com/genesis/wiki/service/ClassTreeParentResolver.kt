package com.genesis.wiki.service

import com.genesis.wiki.entity.WikiClass

/** 캐릭터 트리에 따라 달라지는 전직 경로. 공용 클래스의 원본 부모는 유지한다. */
internal fun resolveClassTreeParent(clazz: WikiClass, tree: List<WikiClass>): Int? {
    val parent = clazz.parentClass ?: return null
    if (tree.any { it.classId == parent.classId }) return parent.classId
    val alternateParent = when (clazz.name to parent.name) {
        "다크메이지" to "위치" -> "워록"
        "가드" to "솔져", "제너럴" to "솔져" -> "파이크"
        "로얄랜서" to "랜서" -> "제너럴"
        else -> null
    }
    if (alternateParent != null) {
        return tree.singleOrNull { it.name == alternateParent && it.tier == parent.tier }?.classId
            ?: parent.classId
    }
    return parent.classId
}
