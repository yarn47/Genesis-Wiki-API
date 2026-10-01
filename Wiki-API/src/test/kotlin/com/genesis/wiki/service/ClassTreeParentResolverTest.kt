package com.genesis.wiki.service

import com.genesis.wiki.entity.WikiClass
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class ClassTreeParentResolverTest {
    @Test
    fun `landam paths reuse shared classes and preserve original parents`() {
        val soldier = WikiClass(classId = 10, name = "솔져", tier = 1)
        val pike = WikiClass(classId = 11, name = "파이크", tier = 1)
        val guard = WikiClass(classId = 12, name = "가드", tier = 2, parentClass = soldier)
        val general = WikiClass(classId = 13, name = "제너럴", tier = 2, parentClass = soldier)
        val lancer = WikiClass(classId = 14, name = "랜서", tier = 2, parentClass = pike)
        val royal = WikiClass(classId = 15, name = "로얄랜서", tier = 3, parentClass = lancer)
        val earth = WikiClass(classId = 16, name = "어스퀘이커", tier = 3, parentClass = guard)
        val marshal = WikiClass(classId = 17, name = "마샬", tier = 3, parentClass = general)
        val tree = listOf(pike, guard, general, earth, marshal, royal)
        assertEquals(listOf(null, 11, 11, 12, 13, 13), tree.map { resolveClassTreeParent(it, tree) })
        assertEquals(10, resolveClassTreeParent(guard, tree + soldier))
        assertEquals(10, resolveClassTreeParent(general, tree + soldier))
        assertEquals(14, resolveClassTreeParent(royal, tree + lancer))
        assertEquals(soldier, guard.parentClass)
        assertEquals(soldier, general.parentClass)
        assertEquals(lancer, royal.parentClass)
        assertEquals(14, resolveClassTreeParent(royal, listOf(royal)))
    }

    private val witch = WikiClass(classId = 1, name = "위치", tier = 1)
    private val warlock = WikiClass(classId = 2, name = "워록", tier = 1)
    private val darkMage = WikiClass(classId = 3, name = "다크메이지", tier = 2, parentClass = witch)

    @Test
    fun `gishne uses warlock without changing shared class parent`() {
        assertEquals(2, resolveClassTreeParent(darkMage, listOf(warlock, darkMage)))
        assertEquals(witch, darkMage.parentClass)
        assertNull(resolveClassTreeParent(warlock, listOf(warlock, darkMage)))
    }

    @Test
    fun `original parent wins and unrelated missing parents are not guessed`() {
        assertEquals(1, resolveClassTreeParent(darkMage, listOf(witch, warlock, darkMage)))
        assertEquals(1, resolveClassTreeParent(darkMage, listOf(darkMage)))
        val other = WikiClass(classId = 4, name = "다른 클래스", tier = 2, parentClass = witch)
        assertEquals(1, resolveClassTreeParent(other, listOf(warlock, other)))
    }
}
