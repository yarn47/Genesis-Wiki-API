package com.genesis.wiki.service

import com.genesis.wiki.entity.WikiClass

/** 다크메이지는 위치와 워록 양쪽에서 전직한다. 공용 클래스의 원본 부모는 유지한다. */
internal fun resolveClassTreeParent(clazz: WikiClass, tree: List<WikiClass>): Int? {
    val parent = clazz.parentClass ?: return null
    if (tree.any { it.classId == parent.classId }) return parent.classId
    if (clazz.name == "다크메이지" && parent.name == "위치") {
        return tree.singleOrNull { it.name == "워록" && it.tier == parent.tier }?.classId
            ?: parent.classId
    }
    return parent.classId
}
