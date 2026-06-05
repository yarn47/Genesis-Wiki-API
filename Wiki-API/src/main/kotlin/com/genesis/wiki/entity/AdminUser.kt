package com.genesis.wiki.entity

import jakarta.persistence.*

@Entity
@Table(name = "admin_users")
class AdminUser(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false, length = 50)
    val username: String,

    @Column(nullable = false)
    var password: String
)