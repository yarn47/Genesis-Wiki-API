package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.*
import com.genesis.wiki.repository.ClassRepository
import com.genesis.wiki.repository.SkillRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
@Transactional(readOnly = true)
class ClassService(
    private val classRepository: ClassRepository,
    private val skillRepository: SkillRepository
) {
    // ─── 조회 ───────────────────────────────────────────────

    fun getAllClasses(): List<ClassSummaryDto> =
        classRepository.findAll().map { it.toSummaryDto() }

    fun searchClasses(name: String): List<ClassSummaryDto> =
        classRepository.findAllByNameContaining(name).map { it.toSummaryDto() }

    fun getClassDetail(id: Int): ClassDetailDto =
        classRepository.findDetailById(id)?.toDetailDto()
            ?: throw NoSuchElementException("클래스를 찾을 수 없습니다: $id")

    // ─── 생성 ───────────────────────────────────────────────

    @Transactional
    fun createClass(req: ClassRequest): ClassDetailDto {
        val parentClass = req.parentClassId?.let {
            classRepository.findById(it).orElseThrow { NoSuchElementException("부모 클래스 없음: $it") }
        }

        val wikiClass = WikiClass(
            name = req.name,
            tier = req.tier,
            weaponType = req.weaponType,
            defenseType = req.defenseType?.let { DefenseType.valueOf(it) },
            attackRange = req.attackRange,
            moveRange = req.moveRange,
            baseHp = req.baseHp,
            baseAttack = req.baseAttack,
            parentClass = parentClass,
            description = req.description,
            iconUrl = req.iconUrl,
            passive1Name = req.passive1Name,
            passive1Lv1 = req.passive1Lv1,
            passive1Lv2 = req.passive1Lv2
        )

        val saved = classRepository.save(wikiClass)

        req.skills.forEachIndexed { idx, skillReq ->
            val skill = Skill(
                name = skillReq.name,
                type = SkillType.valueOf(skillReq.type),
                tpCost = skillReq.tpCost,
                rangeMin = skillReq.rangeMin,
                rangeMax = skillReq.rangeMax,
                area = skillReq.area,
                cooldown = skillReq.cooldown,
                effectText = skillReq.effectText,
                iconUrl = skillReq.iconUrl
            )
            val savedSkill = skillRepository.save(skill)
            saved.classSkills.add(
                ClassSkill(
                    clazz = saved,
                    skill = savedSkill,
                    unlockOrder = skillReq.unlockOrder ?: (idx + 1)
                )
            )
        }

        classRepository.saveAndFlush(saved)
        return classRepository.findDetailById(saved.classId)!!.toDetailDto()
    }

    // ─── 수정 ───────────────────────────────────────────────

    @Transactional
    fun updateClass(id: Int, req: ClassRequest): ClassDetailDto {
        val wikiClass = classRepository.findDetailById(id)
            ?: throw NoSuchElementException("클래스를 찾을 수 없습니다: $id")

        val parentClass = req.parentClassId?.let {
            classRepository.findById(it).orElseThrow { NoSuchElementException("부모 클래스 없음: $it") }
        }

        wikiClass.name = req.name
        wikiClass.tier = req.tier
        wikiClass.weaponType = req.weaponType
        wikiClass.defenseType = req.defenseType?.let { DefenseType.valueOf(it) }
        wikiClass.attackRange = req.attackRange
        wikiClass.moveRange = req.moveRange
        wikiClass.baseHp = req.baseHp
        wikiClass.baseAttack = req.baseAttack
        wikiClass.parentClass = parentClass
        wikiClass.description = req.description
        wikiClass.iconUrl = req.iconUrl
        wikiClass.passive1Name = req.passive1Name
        wikiClass.passive1Lv1 = req.passive1Lv1
        wikiClass.passive1Lv2 = req.passive1Lv2

        // 기존 스킬 전부 삭제 후 재등록
        val oldSkills = wikiClass.classSkills.map { it.skill }
        wikiClass.classSkills.clear()
        classRepository.saveAndFlush(wikiClass)
        skillRepository.deleteAll(oldSkills)

        req.skills.forEachIndexed { idx, skillReq ->
            val skill = Skill(
                name = skillReq.name,
                type = SkillType.valueOf(skillReq.type),
                tpCost = skillReq.tpCost,
                rangeMin = skillReq.rangeMin,
                rangeMax = skillReq.rangeMax,
                area = skillReq.area,
                cooldown = skillReq.cooldown,
                effectText = skillReq.effectText,
                iconUrl = skillReq.iconUrl
            )
            val savedSkill = skillRepository.save(skill)
            wikiClass.classSkills.add(
                ClassSkill(
                    clazz = wikiClass,
                    skill = savedSkill,
                    unlockOrder = skillReq.unlockOrder ?: (idx + 1)
                )
            )
        }

        classRepository.saveAndFlush(wikiClass)
        return classRepository.findDetailById(id)!!.toDetailDto()
    }

    // ─── 삭제 ───────────────────────────────────────────────

    @Transactional
    fun deleteClass(id: Int) {
        val wikiClass = classRepository.findDetailById(id)
            ?: throw NoSuchElementException("클래스를 찾을 수 없습니다: $id")
        val oldSkills = wikiClass.classSkills.map { it.skill }
        wikiClass.classSkills.clear()
        classRepository.saveAndFlush(wikiClass)
        skillRepository.deleteAll(oldSkills)
        classRepository.delete(wikiClass)
    }

    // ─── Entity → DTO ───────────────────────────────────────

    private fun WikiClass.toSummaryDto() = ClassSummaryDto(
        classId = classId, name = name, tier = tier,
        weaponType = weaponType, defenseType = defenseType?.name,
        iconUrl = iconUrl, parentClassId = parentClass?.classId
    )

    private fun WikiClass.toDetailDto() = ClassDetailDto(
        classId = classId, name = name, tier = tier,
        weaponType = weaponType, defenseType = defenseType?.name,
        attackRange = attackRange, moveRange = moveRange,
        baseHp = baseHp, baseAttack = baseAttack,
        parentClassId = parentClass?.classId,
        description = description, iconUrl = iconUrl,
        passive1Name = passive1Name,
        passive1Lv1 = passive1Lv1,
        passive1Lv2 = passive1Lv2,
        skills = classSkills.sortedBy { it.unlockOrder }.map { cs ->
            SkillDto(
                skillId = cs.skill.skillId,
                name = cs.skill.name,
                type = cs.skill.type.name,
                tpCost = cs.skill.tpCost,
                rangeMin = cs.skill.rangeMin,
                rangeMax = cs.skill.rangeMax,
                area = cs.skill.area,
                cooldown = cs.skill.cooldown,
                effectText = cs.skill.effectText,
                iconUrl = cs.skill.iconUrl
            )
        }
    )
}