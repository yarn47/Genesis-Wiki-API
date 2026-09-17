package com.genesis.wiki.config

import com.genesis.wiki.controller.AuthController
import com.genesis.wiki.controller.CharacterController
import com.genesis.wiki.service.AuthService
import com.genesis.wiki.service.CharacterService
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.BDDMockito.given
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest
import org.springframework.context.annotation.Import
import org.springframework.http.MediaType
import org.springframework.mock.web.MockHttpSession
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.status

@WebMvcTest(controllers = [AuthController::class, CharacterController::class])
@Import(SecurityConfig::class)
class SecurityConfigTest {

    @Autowired
    lateinit var mockMvc: MockMvc

    @MockitoBean
    lateinit var authService: AuthService

    @MockitoBean
    lateinit var characterService: CharacterService

    private fun login(): MockHttpSession {
        given(authService.login("admin", "pw")).willReturn(true)
        val result = mockMvc.perform(
            post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"username":"admin","password":"pw"}""")
        ).andExpect(status().isOk).andReturn()
        return result.request.getSession(false) as MockHttpSession
    }

    @Test
    fun `공개 조회는 로그인 없이 가능`() {
        mockMvc.perform(get("/api/characters")).andExpect(status().isOk)
    }

    @Test
    fun `미로그인 상태에서 관리자 조회와 수정 요청은 401`() {
        mockMvc.perform(get("/api/characters/admin")).andExpect(status().isUnauthorized)
        mockMvc.perform(get("/api/characters/admin/1")).andExpect(status().isUnauthorized)
        mockMvc.perform(delete("/api/characters/1")).andExpect(status().isUnauthorized)
        mockMvc.perform(get("/api/auth/check")).andExpect(status().isUnauthorized)
    }

    @Test
    fun `로그인 실패 시 401`() {
        given(authService.login("admin", "wrong")).willReturn(false)
        mockMvc.perform(
            post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"username":"admin","password":"wrong"}""")
        ).andExpect(status().isUnauthorized)
    }

    @Test
    fun `로그인 후 관리자 요청 가능, 로그아웃 후 다시 차단`() {
        val session = login()

        mockMvc.perform(get("/api/auth/check").session(session)).andExpect(status().isOk)
        mockMvc.perform(get("/api/characters/admin").session(session)).andExpect(status().isOk)
        mockMvc.perform(delete("/api/characters/1").session(session)).andExpect(status().isNoContent)

        mockMvc.perform(post("/api/auth/logout").session(session)).andExpect(status().isOk)
        assertTrue(session.isInvalid)
    }
}
