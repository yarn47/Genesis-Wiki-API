package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "buffs")
class Buff(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val buffId: Int = 0,

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
    @OneToMany(mappedBy = "buff", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val levels: MutableList<BuffLevel> = mutableListOf()

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "buff_tag_map",
        joinColumns = [JoinColumn(name = "buff_id")],
        inverseJoinColumns = [JoinColumn(name = "tag_id")]
    )
    val tags: MutableList<Tag> = mutableListOf()

    @OneToMany(mappedBy = "buff", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val sources: MutableList<BuffSource> = mutableListOf()
}

@Entity
@Table(name = "buff_levels")
class BuffLevel(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val buffLevelId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "buff_id", nullable = false)
    var buff: Buff,

    @Column(nullable = false)
    var level: Int,

    @Column(columnDefinition = "TEXT")
    var effectText: String? = null
)

@Entity
@Table(name = "buff_sources")
class BuffSource(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val buffSourceId: Int = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "buff_id", nullable = false)
    var buff: Buff,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var sourceType: SourceType,

    @Column(nullable = false)
    var sourceId: Int,

    @Column(columnDefinition = "TEXT")
    var briefDesc: String? = null
)