package com.genesis.wiki.controller

import com.genesis.wiki.dto.CharacterDetailDto
import com.genesis.wiki.dto.CharacterSummaryDto
import com.genesis.wiki.service.CharacterService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/characters")
@CrossOrigin(origins = ["http://localhost:5173"])
class CharacterController(
    private val characterService: CharacterService
) {
    // 캐릭터 목록
    @GetMapping
    fun getCharacterList(): ResponseEntity<List<CharacterSummaryDto>> =
        ResponseEntity.ok(characterService.getCharacterList())

    // 캐릭터 상세
    @GetMapping("/{id}")
    fun getCharacterDetail(@PathVariable id: Int): ResponseEntity<CharacterDetailDto> =
        ResponseEntity.ok(characterService.getCharacterDetail(id))
}