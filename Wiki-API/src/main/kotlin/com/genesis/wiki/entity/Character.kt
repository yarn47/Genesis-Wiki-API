package com.genesis.wiki.entity

import jakarta.persistence.*
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
    val skins: MutableList<CharacterSkin> = mutableListOf()

    @OneToOne(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    var stats: CharacterStats? = null

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val classTree: MutableList<CharacterClassTree> = mutableListOf()

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val passives: MutableList<CharacterPassive> = mutableListOf()

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val artifacts: MutableList<Artifact> = mutableListOf()

    @OneToMany(mappedBy = "character", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val manifestations: MutableList<CharacterManifestation> = mutableListOf()
}