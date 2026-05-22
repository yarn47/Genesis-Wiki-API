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
    private val classRepository: ClassRepository,
    private val exclusiveWeaponRepository: ExclusiveWeaponRepository,
    private val ultimateSkillRepository: UltimateSkillRepository,
    private val buffRepository: BuffRepository,
    private val debuffRepository: DebuffRepository
) {

    // ─── 조회 ───────────────────────────────────────────────

    fun getCharacterList(): List<CharacterSummaryDto> =
        characterRepository.findAllByIsPublishedTrue().map { it.toSummaryDto() }

    // 관리자용 전체 목록 (비발행 포함)
    fun getAdminCharacterList(): List<CharacterSummaryDto> =
        characterRepository.findAllByOrderByCreatedAtDesc().map { it.toSummaryDto() }

    fun getCharacterDetail(id: Int): CharacterDetailDto {
        val character = characterRepository.findDetailById(id)
            ?: throw NoSuchElementException("캐릭터를 찾을 수 없습니다: $id")
        return buildDetailDto(character)
    }

    // 관리자용 상세 (비발행도 조회)
    fun getAdminCharacterDetail(id: Int): CharacterDetailDto {
        val character = characterRepository.findAdminDetailById(id)
            ?: throw NoSuchElementException("캐릭터를 찾을 수 없습니다: $id")
        return buildDetailDto(character)
    }

    // ─── 생성 ───────────────────────────────────────────────

    @Transactional
    fun createCharacter(req: CharacterRequest): CharacterDetailDto {
        val weapon = req.exclusiveWeaponId?.let {
            exclusiveWeaponRepository.findById(it).orElseThrow { NoSuchElementException("전용무기 없음: $it") }
        }

        val character = Character(
            name = req.name,
            grade = Grade.valueOf(req.grade),
            faction = Faction.valueOf(req.faction),
            element = Element.valueOf(req.element),
            exclusiveWeapon = weapon,
            birthYear = req.birthYear,
            height = req.height,
            cv = req.cv,
            profileText = req.profileText,
            thumbnailUrl = req.thumbnailUrl,
            portraitUrl = req.portraitUrl,
            fullImageUrl = req.fullImageUrl,
            isPublished = req.isPublished
        )
        val saved = characterRepository.save(character)

        // 스탯
        req.stats?.let { s ->
            saved.stats = CharacterStats(
                character = saved, hp = s.hp, attack = s.attack, defense = s.defense,
                critRate = s.critRate, critDamage = s.critDamage,
                physPen = s.physPen, magicPen = s.magicPen, effectResist = s.effectResist
            )
        }

        // 클래스 트리
        req.classTreeIds.forEach { node ->
            val clazz = classRepository.findById(node.classId)
                .orElseThrow { NoSuchElementException("클래스 없음: ${node.classId}") }
            saved.classTree.add(CharacterClassTree(character = saved, clazz = clazz, orderInTier = node.orderInTier))
        }

        // 고유 패시브
        val passive = req.passive?.let { p ->
            val cp = CharacterPassive(character = saved, name = p.name, iconUrl = p.iconUrl)
            p.levels.forEach { lvl ->
                cp.levels.add(CharacterPassiveLevel(passive = cp, unlockType = UnlockType.valueOf(lvl.unlockType), unlockStep = lvl.unlockStep, effectText = lvl.effectText))
            }
            saved.passives.add(cp)
            cp
        }

        // 필살기
        val ultimate = req.ultimate?.let { u ->
            val ult = UltimateSkill(name = u.name, iconUrl = u.iconUrl)
            u.levels.forEach { lvl ->
                ult.levels.add(UltimateSkillLevel(ultimate = ult, manifestStep = lvl.manifestStep, tpCost = lvl.tpCost, rangeMin = lvl.rangeMin, rangeMax = lvl.rangeMax, cooldown = lvl.cooldown, effectText = lvl.effectText))
            }
            ultimateSkillRepository.save(ult)
        }

        // 아티팩트
        val artifactMap = mutableMapOf<Int, Artifact>()
        req.artifacts.forEach { artReq ->
            val art = Artifact(character = saved, name = artReq.name, artifactOrder = artReq.artifactOrder, iconUrl = artReq.iconUrl)
            artReq.levels.forEach { lvl ->
                art.levels.add(ArtifactLevel(artifact = art, manifestStep = lvl.manifestStep, effectText = lvl.effectText))
            }
            saved.artifacts.add(art)
            artifactMap[artReq.artifactOrder] = art
        }

        characterRepository.saveAndFlush(saved)

        // 발현 허브 (3~6단)
        listOf(3, 4, 5, 6).forEach { level ->
            saved.manifestations.add(
                CharacterManifestation(
                    character = saved,
                    manifestLevel = level,
                    ultimate = if (level == 3 || level == 5) ultimate else null,
                    passive = if (level == 4 || level == 6) passive else null,
                    artifact1 = artifactMap[1],
                    artifact2 = artifactMap[2],
                    artifact3 = artifactMap[3],
                    artifact4 = artifactMap[4]
                )
            )
        }

        characterRepository.saveAndFlush(saved)
        return getAdminCharacterDetail(saved.characterId)
    }

    // ─── 수정 ───────────────────────────────────────────────

    @Transactional
    fun updateCharacter(id: Int, req: CharacterRequest): CharacterDetailDto {
        val character = characterRepository.findAdminDetailById(id)
            ?: throw NoSuchElementException("캐릭터를 찾을 수 없습니다: $id")

        val weapon = req.exclusiveWeaponId?.let {
            exclusiveWeaponRepository.findById(it).orElseThrow { NoSuchElementException("전용무기 없음: $it") }
        }

        character.name = req.name
        character.grade = Grade.valueOf(req.grade)
        character.faction = Faction.valueOf(req.faction)
        character.element = Element.valueOf(req.element)
        character.exclusiveWeapon = weapon
        character.birthYear = req.birthYear
        character.height = req.height
        character.cv = req.cv
        character.profileText = req.profileText
        character.thumbnailUrl = req.thumbnailUrl
        character.portraitUrl = req.portraitUrl
        character.fullImageUrl = req.fullImageUrl
        character.isPublished = req.isPublished

        // 스탯
        req.stats?.let { s ->
            val stats = character.stats ?: CharacterStats(character = character).also { character.stats = it }
            stats.hp = s.hp; stats.attack = s.attack; stats.defense = s.defense
            stats.critRate = s.critRate; stats.critDamage = s.critDamage
            stats.physPen = s.physPen; stats.magicPen = s.magicPen; stats.effectResist = s.effectResist
        }

        // 클래스 트리 교체
        character.classTree.clear()
        characterRepository.saveAndFlush(character)
        req.classTreeIds.forEach { node ->
            val clazz = classRepository.findById(node.classId)
                .orElseThrow { NoSuchElementException("클래스 없음: ${node.classId}") }
            character.classTree.add(CharacterClassTree(character = character, clazz = clazz, orderInTier = node.orderInTier))
        }

        // 패시브 교체
        character.passives.clear()
        characterRepository.saveAndFlush(character)
        val passive = req.passive?.let { p ->
            val cp = CharacterPassive(character = character, name = p.name, iconUrl = p.iconUrl)
            p.levels.forEach { lvl ->
                cp.levels.add(CharacterPassiveLevel(passive = cp, unlockType = UnlockType.valueOf(lvl.unlockType), unlockStep = lvl.unlockStep, effectText = lvl.effectText))
            }
            character.passives.add(cp)
            cp
        }

        // 필살기: 기존 manifestations에서 ultimate 추출해서 교체
        val existingUltimate = character.manifestations.firstOrNull()?.ultimate
        val ultimate = req.ultimate?.let { u ->
            val ult = existingUltimate ?: UltimateSkill(name = u.name, iconUrl = u.iconUrl)
            ult.name = u.name; ult.iconUrl = u.iconUrl
            ult.levels.clear()
            u.levels.forEach { lvl ->
                ult.levels.add(UltimateSkillLevel(ultimate = ult, manifestStep = lvl.manifestStep, tpCost = lvl.tpCost, rangeMin = lvl.rangeMin, rangeMax = lvl.rangeMax, cooldown = lvl.cooldown, effectText = lvl.effectText))
            }
            ultimateSkillRepository.save(ult)
        }

        // 아티팩트 교체
        character.artifacts.clear()
        character.manifestations.clear()
        characterRepository.saveAndFlush(character)

        val artifactMap = mutableMapOf<Int, Artifact>()
        req.artifacts.forEach { artReq ->
            val art = Artifact(character = character, name = artReq.name, artifactOrder = artReq.artifactOrder, iconUrl = artReq.iconUrl)
            artReq.levels.forEach { lvl ->
                art.levels.add(ArtifactLevel(artifact = art, manifestStep = lvl.manifestStep, effectText = lvl.effectText))
            }
            character.artifacts.add(art)
            artifactMap[artReq.artifactOrder] = art
        }

        characterRepository.saveAndFlush(character)

        // 발현 허브 재생성
        listOf(3, 4, 5, 6).forEach { level ->
            character.manifestations.add(
                CharacterManifestation(
                    character = character, manifestLevel = level,
                    ultimate = if (level == 3 || level == 5) ultimate else null,
                    passive = if (level == 4 || level == 6) passive else null,
                    artifact1 = artifactMap[1], artifact2 = artifactMap[2],
                    artifact3 = artifactMap[3], artifact4 = artifactMap[4]
                )
            )
        }

        characterRepository.saveAndFlush(character)
        return getAdminCharacterDetail(id)
    }

    // ─── 삭제 ───────────────────────────────────────────────

    @Transactional
    fun deleteCharacter(id: Int) {
        val character = characterRepository.findById(id)
            .orElseThrow { NoSuchElementException("캐릭터를 찾을 수 없습니다: $id") }
        // UltimateSkill은 cascade 없으니 따로 삭제
        character.manifestations.firstOrNull()?.ultimate?.let {
            ultimateSkillRepository.delete(it)
        }
        characterRepository.delete(character)
    }

    // ─── DTO 빌더 ───────────────────────────────────────────

    private fun buildDetailDto(character: Character): CharacterDetailDto {
        val allTexts = collectAllEffectTexts(character)
        val buffNames = TextTagUtil.extractAllBuffNames(allTexts)
        val debuffNames = TextTagUtil.extractAllDebuffNames(allTexts)

        val relatedBuffs = if (buffNames.isNotEmpty())
            buffRepository.findAllWithDetailByNameIn(buffNames).map { mapBuffToDto(it) }
        else emptyList()

        val relatedDebuffs = if (debuffNames.isNotEmpty())
            debuffRepository.findAllWithDetailByNameIn(debuffNames).map { mapDebuffToDto(it) }
        else emptyList()

        return mapCharacterToDetailDto(character, relatedBuffs, relatedDebuffs)
    }

    private fun Character.toSummaryDto() = CharacterSummaryDto(
        characterId = characterId, name = name, grade = grade.name,
        faction = faction.name, element = element.name, thumbnailUrl = thumbnailUrl
    )

    private fun collectAllEffectTexts(character: Character): List<String?> {
        val texts = mutableListOf<String?>()
        character.passives.forEach { passive -> passive.levels.forEach { texts.add(it.effectText) } }
        character.manifestations.forEach { manifest -> manifest.ultimate?.levels?.forEach { texts.add(it.effectText) } }
        character.artifacts.forEach { artifact -> artifact.levels.forEach { texts.add(it.effectText) } }
        character.exclusiveWeapon?.effects?.forEach { effect ->
            texts.add(effect.baseEffect)
            effect.levels.forEach { texts.add(it.effectText) }
        }
        character.classTree.forEach { node -> node.clazz.classSkills.forEach { texts.add(it.skill.effectText) } }
        return texts
    }

    private fun mapCharacterToDetailDto(character: Character, relatedBuffs: List<BuffDto>, relatedDebuffs: List<DebuffDto>): CharacterDetailDto {
        val stats = character.stats?.let { s ->
            CharacterStatsDto(s.hp, s.attack, s.defense, s.critRate, s.critDamage, s.physPen, s.magicPen, s.effectResist)
        }
        val skins = character.skins.map { skin ->
            CharacterSkinDto(skin.skinId, skin.skinName, skin.isDefault, skin.thumbnailUrl, skin.portraitUrl, skin.fullImageUrl, skin.howToObtain, skin.releaseDate?.toString())
        }
        val classTree = character.classTree.sortedWith(compareBy({ it.clazz.tier }, { it.orderInTier })).map { node ->
            ClassTreeNodeDto(
                classId = node.clazz.classId, name = node.clazz.name, tier = node.clazz.tier,
                weaponType = node.clazz.weaponType, defenseType = node.clazz.defenseType?.name,
                attackRange = node.clazz.attackRange, moveRange = node.clazz.moveRange,
                baseHp = node.clazz.baseHp, baseAttack = node.clazz.baseAttack,
                parentClassId = node.clazz.parentClass?.classId, orderInTier = node.orderInTier,
                iconUrl = node.clazz.iconUrl, passive1Name = node.clazz.passive1Name,
                passive1Lv1 = node.clazz.passive1Lv1, passive1Lv2 = node.clazz.passive1Lv2,
                skills = node.clazz.classSkills.sortedBy { it.unlockOrder }.map { cs ->
                    SkillDto(cs.skill.skillId, cs.skill.name, cs.skill.type.name, cs.skill.tpCost, cs.skill.rangeMin, cs.skill.rangeMax, cs.skill.area, cs.skill.cooldown, cs.skill.effectText, cs.skill.iconUrl)
                }
            )
        }
        val passive = character.passives.firstOrNull()?.let { p ->
            CharacterPassiveDto(p.passiveId, p.name, p.iconUrl,
                p.levels.sortedWith(compareBy({ it.unlockType.name }, { it.unlockStep })).map { CharacterPassiveLevelDto(it.unlockType.name, it.unlockStep, it.effectText) })
        }
        val ultimateSkill = character.manifestations.firstOrNull()?.ultimate?.let { u ->
            UltimateSkillDto(u.ultimateId, u.name, u.iconUrl,
                u.levels.sortedBy { it.manifestStep }.map { UltimateSkillLevelDto(it.manifestStep, it.tpCost, it.rangeMin, it.rangeMax, it.cooldown, it.effectText) })
        }
        val artifacts = character.artifacts.sortedBy { it.artifactOrder }.map { art ->
            ArtifactDto(art.artifactId, art.name, art.artifactOrder, art.iconUrl,
                art.levels.sortedBy { it.manifestStep }.map { ArtifactLevelDto(it.manifestStep, it.effectText) })
        }
        val manifestations = character.manifestations.sortedBy { it.manifestLevel }.map { m ->
            CharacterManifestationDto(m.manifestLevel, m.ultimate?.ultimateId, m.passive?.passiveId, m.artifact1?.artifactId, m.artifact2?.artifactId, m.artifact3?.artifactId, m.artifact4?.artifactId)
        }
        val exclusiveWeapon = character.exclusiveWeapon?.let { w ->
            ExclusiveWeaponDto(w.weaponId, w.name, w.weaponType, w.grade.name, w.baseStats, w.extraStats, w.description, w.iconUrl,
                w.effects.map { effect ->
                    ExclusiveWeaponEffectDto(effect.effectId, effect.effectName, effect.effectType.name, effect.baseEffect, effect.iconUrl,
                        effect.levels.sortedBy { it.breakthroughStep }.map { WeaponEffectLevelDto(it.breakthroughStep, it.effectText) })
                })
        }
        return CharacterDetailDto(
            characterId = character.characterId, name = character.name,
            grade = character.grade.name, faction = character.faction.name, element = character.element.name,
            birthYear = character.birthYear, height = character.height, cv = character.cv,
            profileText = character.profileText, thumbnailUrl = character.thumbnailUrl,
            portraitUrl = character.portraitUrl, fullImageUrl = character.fullImageUrl,
            stats = stats, skins = skins, classTree = classTree, passive = passive,
            ultimateSkill = ultimateSkill, artifacts = artifacts, manifestations = manifestations,
            exclusiveWeapon = exclusiveWeapon, relatedBuffs = relatedBuffs, relatedDebuffs = relatedDebuffs
        )
    }

    fun mapBuffToDto(buff: Buff): BuffDto = BuffDto(
        buffId = buff.buffId, name = buff.name, description = buff.description, iconUrl = buff.iconUrl,
        duration = buff.duration, maxStack = buff.maxStack, hasLevels = buff.hasLevels,
        levels = buff.levels.sortedBy { it.level }.map { BuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack) },
        tags = buff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = buff.sources.map { BuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )

    fun mapDebuffToDto(debuff: Debuff): DebuffDto = DebuffDto(
        debuffId = debuff.debuffId, name = debuff.name, description = debuff.description, iconUrl = debuff.iconUrl,
        duration = debuff.duration, maxStack = debuff.maxStack, hasLevels = debuff.hasLevels,
        levels = debuff.levels.sortedBy { it.level }.map { DebuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack) },
        tags = debuff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = debuff.sources.map { DebuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )
}