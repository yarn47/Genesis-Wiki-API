package com.genesis.wiki.entity

import jakarta.persistence.*

@Entity
@Table(name = "tags")
class Tag(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val tagId: Int = 0,

    @Column(nullable = false, unique = true, length = 50)
    var name: String,

    @Column(length = 20)
    var color: String = "gray"
)