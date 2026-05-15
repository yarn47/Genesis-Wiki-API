package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDateTime

// ─── WikiClass ────────────────────────────────────────────
@Entity
@Table(name = "classes")
class WikiClass(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val classId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(nullable = false)
    var tier: Int,

    @Column(length = 100)
    var weaponType: String? = null,

    @Enumerated(EnumType.STRING)
    var defenseType: DefenseType? = null,

    var attackRange: Int? = null,
    var moveRange: Int? = null,
    var baseHp: Int? = null,
    var baseAttack: Int? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_class_id")
    var parentClass: WikiClass? = null,

    @Column(columnDefinition = "TEXT")
    var description: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null,

    @Column(length = 100)
    var passive1Name: String? = null,

    @Column(columnDefinition = "TEXT")
    var passive1Lv1: String? = null,

    @Column(columnDefinition = "TEXT")
    var passive1Lv2: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "clazz", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val classSkills: MutableList<ClassSkill> = mutableListOf()
}

// ─── Skill ────────────────────────────────────────────────
@Entity
@Table(name = "skills")
class Skill(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val skillId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var type: SkillType,

    var tpCost: Int? = null,
    var rangeMin: Int? = null,
    var rangeMax: Int? = null,

    @Column(length = 50)
    var area: String? = null,

    var cooldown: Int? = null,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

// ─── ClassSkill ───────────────────────────────────────────
@Entity
@Table(name = "class_skills")
class ClassSkill(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val classSkillId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "class_id", nullable = false)
    var clazz: WikiClass,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "skill_id", nullable = false)
    var skill: Skill,

    var unlockOrder: Int? = null
)

// ─── UltimateSkill ────────────────────────────────────────
@Entity
@Table(name = "ultimate_skills")
class UltimateSkill(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val ultimateId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "ultimate", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val levels: MutableList<UltimateSkillLevel> = mutableListOf()
}

@Entity
@Table(name = "ultimate_skill_levels")
class UltimateSkillLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val ultLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ultimate_id", nullable = false)
    var ultimate: UltimateSkill,

    @Column(nullable = false)
    var manifestStep: Int,

    var tpCost: Int? = null,
    var rangeMin: Int? = null,
    var rangeMax: Int? = null,
    var cooldown: Int? = null,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)