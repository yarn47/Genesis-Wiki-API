package com.genesis.wiki.service

import com.genesis.wiki.entity.WikiClass
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class ClassTreeParentResolverTest {
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
