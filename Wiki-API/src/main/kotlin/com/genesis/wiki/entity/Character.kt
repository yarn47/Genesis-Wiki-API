package com.genesis.wiki.entity

import jakarta.persistence.*
import java.time.LocalDate
import java.time.LocalDateTime

@Entity
@Table(name = "characters")
class Character(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val characterId: Int = 0,

    @Column(nullable = false, length = 100)
    var name: String,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var grade: Grade,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var faction: Faction,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var element: Element,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "exclusive_weapon_id")
    var exclusiveWeapon: ExclusiveWeapon? = null,

    @Column(length = 50)
    var birthYear: String? = null,

    @Column(length = 50)
    var height: String? = null,

    @Column(length = 100)
    var cv: String? = null,

    @Column(name = "release_date")
    var releaseDate: LocalDate? = null,

    @Column(length = 100)
    var appearedIn: String? = null,

    @Column(columnDefinition = "TEXT")
    var profileText: String? = null,

    @Column(length = 255)
    var thumbnailUrl: String? = null,

    @Column(length = 255)
    var portraitUrl: String? = null,

    @Column(length = 255)
    var fullImageUrl: String? = null,

    @Column(nullable = false)
    var isPublished: Boolean = false,

    @Column(updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val skins: MutableSet<CharacterSkin> = mutableSetOf()

    @OneToOne(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    var stats: CharacterStats? = null

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val classTree: MutableSet<CharacterClassTree> = mutableSetOf()

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val passives: MutableSet<CharacterPassive> = mutableSetOf()

    // 아티팩트는 공용 목록이라 연결만 들고 있는다
    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY, orphanRemoval = true)
    val characterArtifacts: MutableSet<CharacterArtifact> = mutableSetOf()

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val manifestations: MutableSet<CharacterManifestation> = mutableSetOf()
}