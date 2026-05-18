package com.genesis.wiki.controller

import com.genesis.wiki.dto.EquipmentDetailDto
import com.genesis.wiki.dto.EquipmentSummaryDto
import com.genesis.wiki.dto.ExclusiveWeaponDto
import com.genesis.wiki.service.ItemService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/items")
@CrossOrigin(origins = ["http://localhost:5173"])
class ItemController(
    private val itemService: ItemService
) {
    // 장비 목록
    @GetMapping
    fun getEquipmentList(): ResponseEntity<List<EquipmentSummaryDto>> =
        ResponseEntity.ok(itemService.getEquipmentList())

    // 장비 상세
    @GetMapping("/{id}")
    fun getEquipmentDetail(@PathVariable id: Int): ResponseEntity<EquipmentDetailDto> =
        ResponseEntity.ok(itemService.getEquipmentDetail(id))

    // 전용무기 검색 (캐릭터 연결용)
    @GetMapping("/weapons/search")
    fun searchWeapons(@RequestParam name: String): ResponseEntity<List<ExclusiveWeaponDto>> =
        ResponseEntity.ok(itemService.searchExclusiveWeapons(name))

    // 전용무기 상세
    @GetMapping("/weapons/{id}")
    fun getWeaponDetail(@PathVariable id: Int): ResponseEntity<ExclusiveWeaponDto> =
        ResponseEntity.ok(itemService.getExclusiveWeaponDetail(id))
}