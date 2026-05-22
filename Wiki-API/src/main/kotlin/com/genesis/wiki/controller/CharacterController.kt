package com.genesis.wiki.controller

import com.genesis.wiki.dto.*
import com.genesis.wiki.service.CharacterService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/characters")
@CrossOrigin(origins = ["http://localhost:5173"])
class CharacterController(
    private val characterService: CharacterService
) {
    // 공개 목록
    @GetMapping
    fun getCharacterList(): ResponseEntity<List<CharacterSummaryDto>> =
        ResponseEntity.ok(characterService.getCharacterList())

    // 관리자 전체 목록 (비발행 포함)
    @GetMapping("/admin")
    fun getAdminCharacterList(): ResponseEntity<List<CharacterSummaryDto>> =
        ResponseEntity.ok(characterService.getAdminCharacterList())

    // 공개 상세
    @GetMapping("/{id}")
    fun getCharacterDetail(@PathVariable id: Int): ResponseEntity<CharacterDetailDto> =
        ResponseEntity.ok(characterService.getCharacterDetail(id))

    // 관리자 상세 (비발행 포함)
    @GetMapping("/admin/{id}")
    fun getAdminCharacterDetail(@PathVariable id: Int): ResponseEntity<CharacterDetailDto> =
        ResponseEntity.ok(characterService.getAdminCharacterDetail(id))

    // 생성
    @PostMapping
    fun createCharacter(@RequestBody req: CharacterRequest): ResponseEntity<CharacterDetailDto> =
        ResponseEntity.ok(characterService.createCharacter(req))

    // 수정
    @PutMapping("/{id}")
    fun updateCharacter(@PathVariable id: Int, @RequestBody req: CharacterRequest): ResponseEntity<CharacterDetailDto> =
        ResponseEntity.ok(characterService.updateCharacter(id, req))

    // 삭제
    @DeleteMapping("/{id}")
    fun deleteCharacter(@PathVariable id: Int): ResponseEntity<Void> {
        characterService.deleteCharacter(id)
        return ResponseEntity.noContent().build()
    }
}