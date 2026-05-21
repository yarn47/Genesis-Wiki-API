package com.genesis.wiki.controller

import com.genesis.wiki.dto.ClassDetailDto
import com.genesis.wiki.dto.ClassRequest
import com.genesis.wiki.dto.ClassSummaryDto
import com.genesis.wiki.service.ClassService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/classes")
@CrossOrigin(origins = ["http://localhost:5173"])
class ClassController(
    private val classService: ClassService
) {
    // 전체 목록
    @GetMapping
    fun getAllClasses(): ResponseEntity<List<ClassSummaryDto>> =
        ResponseEntity.ok(classService.getAllClasses())

    // 이름 검색
    @GetMapping("/search")
    fun searchClasses(@RequestParam name: String): ResponseEntity<List<ClassSummaryDto>> =
        ResponseEntity.ok(classService.searchClasses(name))

    // 상세
    @GetMapping("/{id}")
    fun getClassDetail(@PathVariable id: Int): ResponseEntity<ClassDetailDto> =
        ResponseEntity.ok(classService.getClassDetail(id))

    // 생성
    @PostMapping
    fun createClass(@RequestBody req: ClassRequest): ResponseEntity<ClassDetailDto> =
        ResponseEntity.ok(classService.createClass(req))

    // 수정
    @PutMapping("/{id}")
    fun updateClass(
        @PathVariable id: Int,
        @RequestBody req: ClassRequest
    ): ResponseEntity<ClassDetailDto> =
        ResponseEntity.ok(classService.updateClass(id, req))

    // 삭제
    @DeleteMapping("/{id}")
    fun deleteClass(@PathVariable id: Int): ResponseEntity<Void> {
        classService.deleteClass(id)
        return ResponseEntity.noContent().build()
    }
}