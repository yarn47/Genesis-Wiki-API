package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.WikiClass
import com.genesis.wiki.repository.ClassRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
@Transactional(readOnly = true)
class ClassService(
    private val classRepository: ClassRepository
) {
    // 클래스 목록 (검색용)
    fun searchClasses(name: String): List<ClassSummaryDto> =
        classRepository.findAllByNameContaining(name).map { it.toSummaryDto() }

    // 클래스 상세
    fun getClassDetail(id: Int): ClassDetailDto =
        classRepository.findDetailById(id)?.toDetailDto()
            ?: throw NoSuchElementException("클래스를 찾을 수 없습니다: $id")

    // ─── Entity → DTO ───────────────────────────────────

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