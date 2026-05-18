package com.genesis.wiki.controller

import com.genesis.wiki.dto.ClassDetailDto
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
    // 클래스 검색 (ClassTreeModal용)
    @GetMapping("/search")
    fun searchClasses(@RequestParam name: String): ResponseEntity<List<ClassSummaryDto>> =
        ResponseEntity.ok(classService.searchClasses(name))

    // 클래스 상세
    @GetMapping("/{id}")
    fun getClassDetail(@PathVariable id: Int): ResponseEntity<ClassDetailDto> =
        ResponseEntity.ok(classService.getClassDetail(id))
}