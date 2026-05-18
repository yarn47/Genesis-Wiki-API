package com.genesis.wiki.controller

import com.genesis.wiki.dto.*
import com.genesis.wiki.service.BuffService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = ["http://localhost:5173"])
class BuffController(
    private val buffService: BuffService
) {
    // ─── 버프 ──────────────────────────────────────────────
    @GetMapping("/buffs")
    fun getBuffList(): ResponseEntity<List<BuffDto>> =
        ResponseEntity.ok(buffService.getBuffList())

    @GetMapping("/buffs/{id}")
    fun getBuffDetail(@PathVariable id: Int): ResponseEntity<BuffDto> =
        ResponseEntity.ok(buffService.getBuffDetail(id))

    @PostMapping("/buffs")
    fun createBuff(@RequestBody request: BuffRequest): ResponseEntity<BuffDto> =
        ResponseEntity.ok(buffService.createBuff(request))

    @PutMapping("/buffs/{id}")
    fun updateBuff(@PathVariable id: Int, @RequestBody request: BuffRequest): ResponseEntity<BuffDto> =
        ResponseEntity.ok(buffService.updateBuff(id, request))

    @DeleteMapping("/buffs/{id}")
    fun deleteBuff(@PathVariable id: Int): ResponseEntity<Void> {
        buffService.deleteBuff(id)
        return ResponseEntity.noContent().build()
    }

    // ─── 디버프 ─────────────────────────────────────────────
    @GetMapping("/debuffs")
    fun getDebuffList(): ResponseEntity<List<DebuffDto>> =
        ResponseEntity.ok(buffService.getDebuffList())

    @GetMapping("/debuffs/{id}")
    fun getDebuffDetail(@PathVariable id: Int): ResponseEntity<DebuffDto> =
        ResponseEntity.ok(buffService.getDebuffDetail(id))

    @PostMapping("/debuffs")
    fun createDebuff(@RequestBody request: DebuffRequest): ResponseEntity<DebuffDto> =
        ResponseEntity.ok(buffService.createDebuff(request))

    @PutMapping("/debuffs/{id}")
    fun updateDebuff(@PathVariable id: Int, @RequestBody request: DebuffRequest): ResponseEntity<DebuffDto> =
        ResponseEntity.ok(buffService.updateDebuff(id, request))

    @DeleteMapping("/debuffs/{id}")
    fun deleteDebuff(@PathVariable id: Int): ResponseEntity<Void> {
        buffService.deleteDebuff(id)
        return ResponseEntity.noContent().build()
    }

    // ─── 태그 ──────────────────────────────────────────────
    @GetMapping("/tags")
    fun getTagList(): ResponseEntity<List<TagDto>> =
        ResponseEntity.ok(buffService.getTagList())

    @PostMapping("/tags")
    fun createTag(@RequestBody request: TagRequest): ResponseEntity<TagDto> =
        ResponseEntity.ok(buffService.createTag(request))

    @DeleteMapping("/tags/{id}")
    fun deleteTag(@PathVariable id: Int): ResponseEntity<Void> {
        buffService.deleteTag(id)
        return ResponseEntity.noContent().build()
    }
}