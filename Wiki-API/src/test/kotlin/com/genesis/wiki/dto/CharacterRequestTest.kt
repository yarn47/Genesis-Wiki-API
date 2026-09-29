package com.genesis.wiki.dto

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class CharacterRequestTest {
    private fun junior() = CharacterRequest(
        name = "아리아나 위버 Jr.", grade = "rare", faction = "curtis", element = "crystal",
        hasManifestation = false,
        passive = PassiveRequest("신궁의 혈족", levels = (1..6).map { PassiveLevelRequest("awaken", it) }),
        ultimate = UltimateRequest("화염인", levels = listOf(UltimateLevelRequest(0)))
    )

    @Test
    fun `supports six awakenings and base ultimate without manifestation`() {
        val req = junior()
        assertFalse(req.hasManifestation)
        assertEquals((1..6).toList(), req.passive!!.levels.map { it.unlockStep })
        assertEquals(0, req.ultimate!!.levels.single().manifestStep)
    }

    @Test
    fun `rejects manifestation effects when disabled`() {
        assertThrows(IllegalArgumentException::class.java) {
            junior().copy(ultimate = UltimateRequest("화염인", levels = listOf(UltimateLevelRequest(1))))
        }
        assertThrows(IllegalArgumentException::class.java) {
            junior().copy(passive = PassiveRequest("신궁의 혈족", levels = listOf(PassiveLevelRequest("manifest", 2))))
        }
        assertThrows(IllegalArgumentException::class.java) {
            junior().copy(artifacts = listOf(ArtifactRequest("질풍의 깃", 1)))
        }
    }

    @Test
    fun `existing requests retain manifestation by default`() {
        assertTrue(CharacterRequest(name = "아리아나 위버", grade = "legend", faction = "curtis", element = "nature").hasManifestation)
    }
}
