package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "equipment")
class Equipment(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val equipmentId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var type: EquipmentType,

    @Enumerated(EnumType.STRING)
    var defenseType: DefenseType? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var grade: EquipmentGrade,

    @Column(columnDefinition = "JSON")
    var baseStats: String? = null,

    @Column(columnDefinition = "TEXT")
    var extraStats: String? = null,

    @Column(length = 100)
    var setName: String? = null,

    @Column(name = "set_effect_2", columnDefinition = "TEXT")
    var setEffect2: String? = null,

    @Column(name = "set_effect_4", columnDefinition = "TEXT")
    var setEffect4: String? = null,

    @Column(columnDefinition = "TEXT")
    var description: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "equipment", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val effects: MutableList<EquipmentEffect> = mutableListOf()
}

@Entity
@Table(name = "equipment_effects")
class EquipmentEffect(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val eqEffectId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "equipment_id", nullable = false)
    var equipment: Equipment,

    @Column(nullable = false, length = 100)
    var effectName: String,

    @Enumerated(EnumType.STRING)
    var effectType: EffectType = EffectType.normal,

    @Column(columnDefinition = "TEXT")
    var baseEffect: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null
) {
    @OneToMany(mappedBy = "effect", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val levels: MutableList<EquipmentEffectLevel> = mutableListOf()
}

@Entity
@Table(name = "equipment_effect_levels")
class EquipmentEffectLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val eqEffectLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "eq_effect_id", nullable = false)
    var effect: EquipmentEffect,

    @Column(nullable = false)
    var breakthroughStep: Int,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)