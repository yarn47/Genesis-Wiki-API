package com.genesis.wiki.repository

import com.genesis.wiki.entity.*
import org.springframework.data.jpa.repository.JpaRepository

interface TagRepository : JpaRepository<Tag, Int> {
    fun findByName(name: String): Tag?
    fun findAllByNameContaining(name: String): List<Tag>
}

interface UltimateSkillRepository : JpaRepository<UltimateSkill, Int> {
    fun findAllByNameContaining(name: String): List<UltimateSkill>
}

interface SkillRepository : JpaRepository<Skill, Int> {
    fun findAllByNameContaining(name: String): List<Skill>
    fun findAllByType(type: SkillType): List<Skill>
}

interface CharacterPassiveRepository : JpaRepository<CharacterPassive, Int> {
    fun findAllByCharacterCharacterId(characterId: Int): List<CharacterPassive>
}

interface ArtifactRepository : JpaRepository<Artifact, Int> {
    fun findAllByCharacterCharacterIdOrderByArtifactOrder(characterId: Int): List<Artifact>
}

interface CharacterManifestationRepository : JpaRepository<CharacterManifestation, Int> {
    fun findAllByCharacterCharacterIdOrderByManifestLevel(characterId: Int): List<CharacterManifestation>
}