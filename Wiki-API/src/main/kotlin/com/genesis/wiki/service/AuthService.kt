package com.genesis.wiki.service

import com.genesis.wiki.repository.AdminUserRepository
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service

@Service
class AuthService(
    private val adminUserRepository: AdminUserRepository,
    private val passwordEncoder: PasswordEncoder
) {
    fun login(username: String, password: String): Boolean {
        val user = adminUserRepository.findByUsername(username) ?: return false
        return passwordEncoder.matches(password, user.password)
    }
}