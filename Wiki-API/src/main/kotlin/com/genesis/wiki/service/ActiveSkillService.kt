package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.SkillType
import com.genesis.wiki.repository.CharacterRepository
import com.genesis.wiki.repository.ClassRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

data class ActiveSkillClassDto(val classId: Int, val name: String)
data class ActiveSkillDto(
    val skill: SkillDto,
    val classes: List<ActiveSkillClassDto>,
    val attackTypes: List<String>,
    val usedBy: List<EffectOwnerDto>
)

@Service
@Transactional(readOnly = true)
class ActiveSkillService(
    private val classRepository: ClassRepository,
    private val characterRepository: CharacterRepository
) {
    fun getActiveSkills(): List<ActiveSkillDto> {
        val ownersByClass = characterRepository.findAllByIsPublishedTrue()
            .flatMap { character ->
                character.classTree.map { node ->
                    node.clazz.classId to EffectOwnerDto("character", character.characterId, character.name, character.thumbnailUrl)
                }
            }.groupBy({ it.first }, { it.second })
        return classRepository.findAllWithSkills()
            .flatMap { clazz -> clazz.classSkills.filter { it.skill.type == SkillType.active }.map { clazz to it.skill } }
            .groupBy { it.second.skillId }
            .values.map { entries ->
                val skill = entries.first().second
                val classes = entries.map { it.first }.distinctBy { it.classId }.sortedBy { it.classId }
                ActiveSkillDto(
                    SkillDto(skill.skillId, skill.name, skill.type.name, skill.tpCost, skill.rangeMin, skill.rangeMax,
                        skill.area, skill.attackType, skill.element, skill.allowedWeapon, skill.cooldown, skill.effectText,
                        skill.iconUrl, skill.tags.sortedBy { it.tagId }.map { TagDto(it.tagId, it.name, it.color) }),
                    classes.map { ActiveSkillClassDto(it.classId, it.name) },
                    classes.mapNotNull { skill.attackType?.takeIf(String::isNotBlank) ?: it.attackType?.takeIf(String::isNotBlank) }.distinct().sorted(),
                    classes.flatMap { ownersByClass[it.classId].orEmpty() }.distinctBy { it.id }.sortedBy { it.id }
                )
            }.sortedWith(compareBy({ it.skill.name }, { it.skill.skillId }))
    }
}
