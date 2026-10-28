package com.genesis.wiki.service

import com.genesis.wiki.entity.*
import com.genesis.wiki.entity.Character
import com.genesis.wiki.repository.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.*
import kotlin.test.assertEquals
import kotlin.test.assertNull

class CharacterOuterSkillTest {
    private val characters = mock(CharacterRepository::class.java)
    private val service = CharacterService(characters, mock(ClassRepository::class.java),
        mock(ExclusiveWeaponRepository::class.java), mock(UltimateSkillRepository::class.java),
        mock(BuffRepository::class.java), mock(DebuffRepository::class.java),
        mock(ArtifactRepository::class.java), mock(TagRepository::class.java))

    @Test
    fun `outer skill is independent and sorted without inventing base level`() {
        val c = Character(characterId=75, name="흑태자", grade=Grade.outer, faction=Faction.geysir, element=Element.dark)
        val normal = UltimateSkill(ultimateId=1, name="아수라파천무")
        val outer = UltimateSkill(ultimateId=2, name="궁극 그리마", element="암흑")
        listOf(5,1,3).forEach { outer.levels.add(UltimateSkillLevel(ultimate=outer, manifestStep=it, cooldown=3, effectText="그리마")) }
        c.outerSkill=outer
        c.manifestations.add(CharacterManifestation(character=c, manifestLevel=3, ultimate=normal))
        `when`(characters.findDetailById(75)).thenReturn(c)
        val dto=service.getCharacterDetail(75)
        assertEquals("아수라파천무", dto.ultimateSkill?.name)
        assertEquals("궁극 그리마", dto.outerSkill?.name)
        assertEquals(listOf(1,3,5),dto.outerSkill?.levels?.map { it.manifestStep })
        assertEquals("암흑",dto.outerSkill?.element)
        assertNull(dto.outerSkill?.levels?.first()?.tpCost)
    }

    @Test
    fun `ordinary character has no outer skill`() {
        val c=Character(characterId=1,name="일반",grade=Grade.legend,faction=Faction.geysir,element=Element.dark)
        `when`(characters.findDetailById(1)).thenReturn(c)
        assertNull(service.getCharacterDetail(1).outerSkill)
    }
}
