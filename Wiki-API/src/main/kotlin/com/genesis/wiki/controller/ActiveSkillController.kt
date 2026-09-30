package com.genesis.wiki.controller

import com.genesis.wiki.service.ActiveSkillService
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/skills")
class ActiveSkillController(private val service: ActiveSkillService) {
    @GetMapping
    fun getActiveSkills() = service.getActiveSkills()
}
