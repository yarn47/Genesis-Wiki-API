package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "debuffs")
class Debuff(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val debuffId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Column(columnDefinition = "TEXT")
    var description: String? = null,

    @Column(length = 255)
    var iconUrl: String? = null,

    var duration: Int? = null,
    var maxStack: Int = 1,
    var hasLevels: Boolean = false,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "debuff", cascade = [CascadeType.ALL], fetch = FetchType.LAZY, orphanRemoval = true)
    val levels: MutableList<DebuffLevel> = mutableListOf()

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "debuff_tag_map",
        joinColumns = [JoinColumn(name = "debuff_id")],
        inverseJoinColumns = [JoinColumn(name = "tag_id")]
    )
    val tags: MutableList<Tag> = mutableListOf()

    @OneToMany(mappedBy = "debuff", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val sources: MutableList<DebuffSource> = mutableListOf()
}

@Entity
@Table(name = "debuff_levels")
class DebuffLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val debuffLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "debuff_id", nullable = false)
    var debuff: Debuff,

    @Column(nullable = false)
    var level: Int,

    @Column(length = 100)
    var levelName: String? = null,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null,

    var duration: Int? = null,

    var maxStack: Int? = null
)

@Entity
@Table(name = "debuff_sources")
class DebuffSource(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val debuffSourceId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "debuff_id", nullable = false)
    var debuff: Debuff,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var sourceType: SourceType,

    @Column(nullable = false)
    var sourceId: Int,

    @Column(columnDefinition = "TEXT")
    var briefDesc: String? = null
)