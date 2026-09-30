package com.genesis.wiki.service

import com.genesis.wiki.entity.*
import com.genesis.wiki.entity.Character
import com.genesis.wiki.repository.CharacterRepository
import com.genesis.wiki.repository.ClassRepository
import org.junit.jupiter.api.Test
import org.mockito.Mockito.*
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ActiveSkillServiceTest {
    private val classes = mock(ClassRepository::class.java)
    private val characters = mock(CharacterRepository::class.java)
    private val service = ActiveSkillService(classes, characters)

    @Test
    fun `shared active skills merge classes and published users without duplicate owners`() {
        val first = WikiClass(classId = 1, name = "메이지", tier = 1, attackType = "마법")
        val second = WikiClass(classId = 2, name = "위자드", tier = 2, attackType = "원거리")
        val skill = Skill(skillId = 1, name = "공용 스킬", type = SkillType.active, allowedWeapon = "스태프, 로드")
        first.classSkills.add(ClassSkill(clazz = first, skill = skill))
        second.classSkills.add(ClassSkill(clazz = second, skill = skill))
        first.classSkills.add(ClassSkill(clazz = first, skill = Skill(skillId = 2, name = "패시브", type = SkillType.passive)))
        val owner = Character(characterId = 1, name = "쿤", grade = Grade.legend, faction = Faction.geysir, element = Element.fire, isPublished = true)
        owner.classTree.add(CharacterClassTree(character = owner, clazz = first))
        owner.classTree.add(CharacterClassTree(character = owner, clazz = second))
        `when`(classes.findAllWithSkills()).thenReturn(listOf(first, second))
        `when`(characters.findAllByIsPublishedTrue()).thenReturn(listOf(owner))
        val result = service.getActiveSkills().single()
        assertEquals(listOf(1, 2), result.classes.map { it.classId })
        assertEquals(listOf("마법", "원거리"), result.attackTypes)
        assertEquals(listOf(1), result.usedBy.map { it.id })
        assertEquals("스태프, 로드", result.skill.allowedWeapon)
        verify(characters).findAllByIsPublishedTrue()
    }

    @Test
    fun `explicit attack type overrides class and unknown fields stay unknown`() {
        val clazz = WikiClass(classId = 1, name = "클래스", tier = 1, attackType = "마법")
        val explicit = Skill(skillId = 1, name = "스킬", type = SkillType.active, attackType = "근거리")
        clazz.classSkills.add(ClassSkill(clazz = clazz, skill = explicit))
        val unknown = WikiClass(classId = 2, name = "미등록", tier = 1)
        unknown.classSkills.add(ClassSkill(clazz = unknown, skill = Skill(skillId = 3, name = "스킬", type = SkillType.active)))
        `when`(classes.findAllWithSkills()).thenReturn(listOf(clazz, unknown))
        `when`(characters.findAllByIsPublishedTrue()).thenReturn(emptyList())
        val results = service.getActiveSkills()
        assertEquals(2, results.size) // Same name is not a shared identity.
        assertEquals(listOf("근거리"), results.first().attackTypes)
        assertTrue(results.last().attackTypes.isEmpty())
        assertTrue(results.all { it.usedBy.isEmpty() })
        assertEquals(null, results.last().skill.allowedWeapon)
    }
}
