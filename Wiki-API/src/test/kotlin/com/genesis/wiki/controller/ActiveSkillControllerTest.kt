package com.genesis.wiki.controller

import com.genesis.wiki.config.SecurityConfig
import com.genesis.wiki.service.ActiveSkillService
import org.junit.jupiter.api.Test
import org.mockito.BDDMockito.given
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest
import org.springframework.context.annotation.Import
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*

@WebMvcTest(controllers = [ActiveSkillController::class])
@Import(SecurityConfig::class)
class ActiveSkillControllerTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean lateinit var service: ActiveSkillService

    @Test
    fun `active skill catalog is publicly readable`() {
        given(service.getActiveSkills()).willReturn(emptyList())
        mvc.perform(get("/api/skills"))
            .andExpect(status().isOk)
            .andExpect(content().json("[]"))
    }
}
