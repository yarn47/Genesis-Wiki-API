package com.genesis.wiki.controller

import com.genesis.wiki.dto.LoginRequest
import com.genesis.wiki.dto.LoginResponse
import com.genesis.wiki.service.AuthService
import jakarta.servlet.http.HttpSession
import org.springframework.http.ResponseEntity
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = ["http://localhost:5173"], allowCredentials = "true")
class AuthController(
    private val authService: AuthService,
    private val passwordEncoder: PasswordEncoder
) {
    @PostMapping("/login")
    fun login(@RequestBody req: LoginRequest, session: HttpSession): ResponseEntity<LoginResponse> {
        return if (authService.login(req.username, req.password)) {
            session.setAttribute("isAdmin", true)
            session.maxInactiveInterval = 60 * 60 * 8 // 8시간
            ResponseEntity.ok(LoginResponse(true, "로그인 성공"))
        } else {
            ResponseEntity.status(401).body(LoginResponse(false, "아이디 또는 비밀번호가 틀렸습니다"))
        }
    }

    @PostMapping("/logout")
    fun logout(session: HttpSession): ResponseEntity<LoginResponse> {
        session.invalidate()
        return ResponseEntity.ok(LoginResponse(true, "로그아웃 완료"))
    }

    @GetMapping("/check")
    fun check(session: HttpSession): ResponseEntity<LoginResponse> {
        val isAdmin = session.getAttribute("isAdmin") as? Boolean ?: false
        return if (isAdmin) {
            ResponseEntity.ok(LoginResponse(true, "인증됨"))
        } else {
            ResponseEntity.status(401).body(LoginResponse(false, "미인증"))
        }
    }

    @GetMapping("/encode")
    fun encode(): String? = passwordEncoder.encode("1234")
}