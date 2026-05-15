package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime

// ─── CharacterSkin ───────────────────────────────────────
@Entity
@Table(name = "character_skins")
class CharacterSkin(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val skinId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    @Column(nullable = false, length = 100)
    var skinName: String,

    @Column(nullable = false)
    var isDefault: Boolean = false,

    @Column(length = 255)
    var thumbnailUrl: String? = null,

    @Column(length = 255)
    var portraitUrl: String? = null,

    @Column(length = 255)
    var fullImageUrl: String? = null,

    @Column(columnDefinition = "TEXT")
    var howToObtain: String? = null,

    var releaseDate: LocalDate? = null
)

// ─── CharacterStats ──────────────────────────────────────
@Entity
@Table(name = "character_stats")
class CharacterStats(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val statId: Int = 0,

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    var hp: Long? = null,
    var attack: Int? = null,
    var defense: Int? = null,
    var critRate: Int? = null,
    var critDamage: Int? = null,
    var physPen: Int? = null,
    var magicPen: Int? = null,
    var effectResist: Int? = null
)

// ─── CharacterClassTree ───────────────────────────────────
@Entity
@Table(name = "character_class_tree")
class CharacterClassTree(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "class_id", nullable = false)
    var clazz: WikiClass,

    var orderInTier: Int? = null
)

// ─── CharacterPassive ─────────────────────────────────────
@Entity
@Table(name = "character_passives")
class CharacterPassive(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val passiveId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "passive", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val levels: MutableList<CharacterPassiveLevel> = mutableListOf()
}

@Entity
@Table(name = "character_passive_levels")
class CharacterPassiveLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val passiveLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "passive_id", nullable = false)
    var passive: CharacterPassive,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var unlockType: UnlockType,

    @Column(nullable = false)
    var unlockStep: Int,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)


// ─── Artifact ─────────────────────────────────────────────
@Entity
@Table(name = "artifacts")
class Artifact(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val artifactId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(nullable = false)
    var artifactOrder: Int,

    @Column(length = 255)
    var iconUrl: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "artifact", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val levels: MutableList<ArtifactLevel> = mutableListOf()
}

@Entity
@Table(name = "artifact_levels")
class ArtifactLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val artifactLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "artifact_id", nullable = false)
    var artifact: Artifact,

    @Column(nullable = false)
    var manifestStep: Int,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)

// ─── CharacterManifestation ───────────────────────────────
@Entity
@Table(name = "character_manifestation")
class CharacterManifestation(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val manifestId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    var character: Character,

    @Column(nullable = false)
    var manifestLevel: Int,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ultimate_id")
    var ultimate: UltimateSkill? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "passive_id")
    var passive: CharacterPassive? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "artifact1_id")
    var artifact1: Artifact? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "artifact2_id")
    var artifact2: Artifact? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "artifact3_id")
    var artifact3: Artifact? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "artifact4_id")
    var artifact4: Artifact? = null
)