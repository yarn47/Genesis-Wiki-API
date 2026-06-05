package com.genesis.wiki.repository

import com.genesis.wiki.entity.AdminUser
import org.springframework.data.jpa.repository.JpaRepository

interface AdminUserRepository : JpaRepository<AdminUser, Long> {
    fun findByUsername(username: String): AdminUser?
}