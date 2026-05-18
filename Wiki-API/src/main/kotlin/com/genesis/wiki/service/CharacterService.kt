package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.*
import com.genesis.wiki.repository.*
import com.genesis.wiki.util.TextTagUtil
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
@Transactional(readOnly = true)
class CharacterService(
    private val characterRepository: CharacterRepository,
    private val buffRepository: BuffRepository,
    private val debuffRepository: DebuffRepository
) {

    fun getCharacterList(): List<CharacterSummaryDto> =
        characterRepository.findAllByIsPublishedTrue().map { character ->
            CharacterSummaryDto(
                characterId = character.characterId,
                name = character.name,
                grade = character.grade.name,
                faction = character.faction.name,
                element = character.element.name,
                thumbnailUrl = character.thumbnailUrl
            )
        }

    fun getCharacterDetail(id: Int): CharacterDetailDto {
        val character = characterRepository.findDetailById(id)
            ?: throw NoSuchElementException("캐릭터를 찾을 수 없습니다: $id")

        val allTexts = collectAllEffectTexts(character)
        val buffNames = TextTagUtil.extractAllBuffNames(allTexts)
        val debuffNames = TextTagUtil.extractAllDebuffNames(allTexts)

        val relatedBuffs: List<BuffDto> = if (buffNames.isNotEmpty())
            buffRepository.findAllWithDetailByNameIn(buffNames).map { buff -> mapBuffToDto(buff) }
        else emptyList()

        val relatedDebuffs: List<DebuffDto> = if (debuffNames.isNotEmpty())
            debuffRepository.findAllWithDetailByNameIn(debuffNames).map { debuff -> mapDebuffToDto(debuff) }
        else emptyList()

        return mapCharacterToDetailDto(character, relatedBuffs, relatedDebuffs)
    }

    private fun collectAllEffectTexts(character: Character): List<String?> {
        val texts = mutableListOf<String?>()
        character.passives.forEach { passive ->
            passive.levels.forEach { texts.add(it.effectText) }
        }
        character.manifestations.forEach { manifest ->
            manifest.ultimate?.levels?.forEach { texts.add(it.effectText) }
        }
        character.artifacts.forEach { artifact ->
            artifact.levels.forEach { texts.add(it.effectText) }
        }
        character.exclusiveWeapon?.effects?.forEach { effect ->
            texts.add(effect.baseEffect)
            effect.levels.forEach { texts.add(it.effectText) }
        }
        character.classTree.forEach { node ->
            node.clazz.classSkills.forEach { texts.add(it.skill.effectText) }
        }
        return texts
    }

    private fun mapCharacterToDetailDto(
        character: Character,
        relatedBuffs: List<BuffDto>,
        relatedDebuffs: List<DebuffDto>
    ): CharacterDetailDto {
        val stats = character.stats?.let { s ->
            CharacterStatsDto(
                hp = s.hp, attack = s.attack, defense = s.defense,
                critRate = s.critRate, critDamage = s.critDamage,
                physPen = s.physPen, magicPen = s.magicPen, effectResist = s.effectResist
            )
        }

        val skins: List<CharacterSkinDto> = character.skins.map { skin ->
            CharacterSkinDto(
                skinId = skin.skinId, skinName = skin.skinName, isDefault = skin.isDefault,
                thumbnailUrl = skin.thumbnailUrl, portraitUrl = skin.portraitUrl,
                fullImageUrl = skin.fullImageUrl, howToObtain = skin.howToObtain,
                releaseDate = skin.releaseDate?.toString()
            )
        }

        val classTree: List<ClassTreeNodeDto> = character.classTree
            .sortedWith(compareBy({ it.clazz.tier }, { it.orderInTier }))
            .map { node ->
                ClassTreeNodeDto(
                    classId = node.clazz.classId,
                    name = node.clazz.name,
                    tier = node.clazz.tier,
                    weaponType = node.clazz.weaponType,
                    defenseType = node.clazz.defenseType?.name,
                    attackRange = node.clazz.attackRange,
                    moveRange = node.clazz.moveRange,
                    baseHp = node.clazz.baseHp,
                    baseAttack = node.clazz.baseAttack,
                    parentClassId = node.clazz.parentClass?.classId,
                    orderInTier = node.orderInTier,
                    iconUrl = node.clazz.iconUrl,
                    passive1Name = node.clazz.passive1Name,
                    passive1Lv1 = node.clazz.passive1Lv1,
                    passive1Lv2 = node.clazz.passive1Lv2,
                    skills = node.clazz.classSkills.sortedBy { it.unlockOrder }.map { cs ->
                        SkillDto(
                            skillId = cs.skill.skillId, name = cs.skill.name,
                            type = cs.skill.type.name, tpCost = cs.skill.tpCost,
                            rangeMin = cs.skill.rangeMin, rangeMax = cs.skill.rangeMax,
                            area = cs.skill.area, cooldown = cs.skill.cooldown,
                            effectText = cs.skill.effectText, iconUrl = cs.skill.iconUrl
                        )
                    }
                )
            }

        val passive: CharacterPassiveDto? = character.passives.firstOrNull()?.let { p ->
            CharacterPassiveDto(
                passiveId = p.passiveId, name = p.name, iconUrl = p.iconUrl,
                levels = p.levels.sortedWith(compareBy({ it.unlockType.name }, { it.unlockStep }))
                    .map { lvl ->
                        CharacterPassiveLevelDto(lvl.unlockType.name, lvl.unlockStep, lvl.effectText)
                    }
            )
        }

        val ultimateSkill: UltimateSkillDto? = character.manifestations.firstOrNull()?.ultimate?.let { u ->
            UltimateSkillDto(
                ultimateId = u.ultimateId, name = u.name, iconUrl = u.iconUrl,
                levels = u.levels.sortedBy { it.manifestStep }.map { lvl ->
                    UltimateSkillLevelDto(
                        lvl.manifestStep, lvl.tpCost, lvl.rangeMin, lvl.rangeMax,
                        lvl.cooldown, lvl.effectText
                    )
                }
            )
        }

        val artifacts: List<ArtifactDto> = character.artifacts.sortedBy { it.artifactOrder }.map { art ->
            ArtifactDto(
                artifactId = art.artifactId, name = art.name,
                artifactOrder = art.artifactOrder, iconUrl = art.iconUrl,
                levels = art.levels.sortedBy { it.manifestStep }.map { lvl ->
                    ArtifactLevelDto(lvl.manifestStep, lvl.effectText)
                }
            )
        }

        val manifestations: List<CharacterManifestationDto> = character.manifestations
            .sortedBy { it.manifestLevel }.map { m ->
                CharacterManifestationDto(
                    manifestLevel = m.manifestLevel,
                    ultimateId = m.ultimate?.ultimateId,
                    passiveId = m.passive?.passiveId,
                    artifact1Id = m.artifact1?.artifactId,
                    artifact2Id = m.artifact2?.artifactId,
                    artifact3Id = m.artifact3?.artifactId,
                    artifact4Id = m.artifact4?.artifactId
                )
            }

        val exclusiveWeapon: ExclusiveWeaponDto? = character.exclusiveWeapon?.let { w ->
            ExclusiveWeaponDto(
                weaponId = w.weaponId, name = w.name, weaponType = w.weaponType,
                grade = w.grade.name, baseStats = w.baseStats, extraStats = w.extraStats,
                description = w.description, iconUrl = w.iconUrl,
                effects = w.effects.map { effect ->
                    ExclusiveWeaponEffectDto(
                        effectId = effect.effectId, effectName = effect.effectName,
                        effectType = effect.effectType.name, baseEffect = effect.baseEffect,
                        iconUrl = effect.iconUrl,
                        levels = effect.levels.sortedBy { it.breakthroughStep }.map { lvl ->
                            WeaponEffectLevelDto(lvl.breakthroughStep, lvl.effectText)
                        }
                    )
                }
            )
        }

        return CharacterDetailDto(
            characterId = character.characterId,
            name = character.name,
            grade = character.grade.name,
            faction = character.faction.name,
            element = character.element.name,
            birthYear = character.birthYear,
            height = character.height,
            cv = character.cv,
            profileText = character.profileText,
            thumbnailUrl = character.thumbnailUrl,
            portraitUrl = character.portraitUrl,
            fullImageUrl = character.fullImageUrl,
            stats = stats,
            skins = skins,
            classTree = classTree,
            passive = passive,
            ultimateSkill = ultimateSkill,
            artifacts = artifacts,
            manifestations = manifestations,
            exclusiveWeapon = exclusiveWeapon,
            relatedBuffs = relatedBuffs,
            relatedDebuffs = relatedDebuffs
        )
    }

    fun mapBuffToDto(buff: Buff): BuffDto = BuffDto(
        buffId = buff.buffId,
        name = buff.name,
        description = buff.description,
        iconUrl = buff.iconUrl,
        duration = buff.duration,
        maxStack = buff.maxStack,
        hasLevels = buff.hasLevels,
        levels = buff.levels.sortedBy { it.level }.map { BuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack) },
        tags = buff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = buff.sources.map { BuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )

    fun mapDebuffToDto(debuff: Debuff): DebuffDto = DebuffDto(
        debuffId = debuff.debuffId,
        name = debuff.name,
        description = debuff.description,
        iconUrl = debuff.iconUrl,
        duration = debuff.duration,
        maxStack = debuff.maxStack,
        hasLevels = debuff.hasLevels,
        levels = debuff.levels.sortedBy { it.level }.map { DebuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack)  },
        tags = debuff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = debuff.sources.map { DebuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )
}