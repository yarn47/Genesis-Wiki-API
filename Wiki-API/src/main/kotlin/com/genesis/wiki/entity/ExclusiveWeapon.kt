package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "exclusive_weapons")
class ExclusiveWeapon(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val weaponId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(length = 100)
    var weaponType: String? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var grade: EquipmentGrade,

    @Column(columnDefinition = "JSON")
    var baseStats: String? = null,

    @Column(columnDefinition = "TEXT")
    var extraStats: String? = null,

    @Column(columnDefinition = "TEXT")
    var description: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "weapon", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val effects: MutableList<ExclusiveWeaponEffect> = mutableListOf()
}

@Entity
@Table(name = "exclusive_weapon_effects")
class ExclusiveWeaponEffect(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val effectId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "weapon_id", nullable = false)
    var weapon: ExclusiveWeapon,

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
    val levels: MutableList<ExclusiveWeaponEffectLevel> = mutableListOf()
}

@Entity
@Table(name = "exclusive_weapon_effect_levels")
class ExclusiveWeaponEffectLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val ewEffectLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "effect_id", nullable = false)
    var effect: ExclusiveWeaponEffect,

    @Column(nullable = false)
    var breakthroughStep: Int,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)