package com.genesis.wiki.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpMethod
import org.springframework.http.HttpStatus
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.HttpStatusEntryPoint
import org.springframework.security.web.context.HttpSessionSecurityContextRepository
import org.springframework.security.web.context.SecurityContextRepository
import org.springframework.web.cors.CorsConfiguration
import org.springframework.web.cors.CorsConfigurationSource
import org.springframework.web.cors.UrlBasedCorsConfigurationSource

@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun filterChain(http: HttpSecurity, securityContextRepository: SecurityContextRepository): SecurityFilterChain {
        http
            .csrf { it.disable() }
            .cors { it.configurationSource(corsConfigurationSource()) }
            .formLogin { it.disable() }     // 스프링 기본 로그인 폼 꺼버리기
            .httpBasic { it.disable() }     // 기본 HTTP Basic 인증창 끄기
            .securityContext { it.securityContextRepository(securityContextRepository) }
            .authorizeHttpRequests { auth ->
                auth
                    .requestMatchers("/error").permitAll()
                    .requestMatchers("/api/auth/**").permitAll()
                    // 비발행 데이터가 포함된 관리자 조회
                    .requestMatchers("/api/characters/admin/**").hasRole("ADMIN")
                    // 공개 조회
                    .requestMatchers(HttpMethod.GET, "/api/**").permitAll()
                    // 생성/수정/삭제 등 나머지는 관리자만
                    .anyRequest().hasRole("ADMIN")
            }
            // 미로그인 요청은 403 대신 401로 응답
            .exceptionHandling { it.authenticationEntryPoint(HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)) }
            .sessionManagement { session ->
                session.maximumSessions(5)
            }

        return http.build()
    }

    @Bean
    fun securityContextRepository(): SecurityContextRepository = HttpSessionSecurityContextRepository()

    @Bean
    fun passwordEncoder(): PasswordEncoder = BCryptPasswordEncoder()

    @Bean
    fun corsConfigurationSource(): CorsConfigurationSource {
        val config = CorsConfiguration()
        config.allowedOrigins = listOf("http://localhost:5173", "http://64.176.231.172", "https://wiki.jan-azhidahaka.com")
        config.allowedMethods = listOf("GET", "POST", "PUT", "DELETE", "OPTIONS")
        config.allowedHeaders = listOf("*")
        config.allowCredentials = true
        val source = UrlBasedCorsConfigurationSource()
        source.registerCorsConfiguration("/**", config)
        return source
    }
}
