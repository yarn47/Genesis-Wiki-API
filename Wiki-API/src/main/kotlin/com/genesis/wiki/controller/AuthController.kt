package com.genesis.wiki.controller

import com.genesis.wiki.dto.LoginRequest
import com.genesis.wiki.dto.LoginResponse
import com.genesis.wiki.service.AuthService
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.http.ResponseEntity
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.authority.SimpleGrantedAuthority
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.web.context.SecurityContextRepository
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/auth")
class AuthController(
    private val authService: AuthService,
    private val securityContextRepository: SecurityContextRepository
) {
    @PostMapping("/login")
    fun login(
        @RequestBody req: LoginRequest,
        request: HttpServletRequest,
        response: HttpServletResponse
    ): ResponseEntity<LoginResponse> {
        if (!authService.login(req.username, req.password)) {
            return ResponseEntity.status(401).body(LoginResponse(false, "아이디 또는 비밀번호가 틀렸습니다"))
        }

        // 세션 고정 공격 방지: 로그인 시 세션 ID 교체
        request.getSession(true).maxInactiveInterval = 60 * 60 * 8 // 8시간
        request.changeSessionId()

        // 스프링 시큐리티에 관리자 권한으로 로그인 상태 저장
        val context = SecurityContextHolder.createEmptyContext()
        context.authentication = UsernamePasswordAuthenticationToken.authenticated(
            req.username, null, listOf(SimpleGrantedAuthority("ROLE_ADMIN"))
        )
        SecurityContextHolder.setContext(context)
        securityContextRepository.saveContext(context, request, response)

        return ResponseEntity.ok(LoginResponse(true, "로그인 성공"))
    }

    @PostMapping("/logout")
    fun logout(request: HttpServletRequest): ResponseEntity<LoginResponse> {
        request.getSession(false)?.invalidate()
        SecurityContextHolder.clearContext()
        return ResponseEntity.ok(LoginResponse(true, "로그아웃 완료"))
    }

    @GetMapping("/check")
    fun check(): ResponseEntity<LoginResponse> {
        val isAdmin = SecurityContextHolder.getContext().authentication
            ?.authorities?.any { it.authority == "ROLE_ADMIN" } ?: false
        return if (isAdmin) {
            ResponseEntity.ok(LoginResponse(true, "인증됨"))
        } else {
            ResponseEntity.status(401).body(LoginResponse(false, "미인증"))
        }
    }
}
