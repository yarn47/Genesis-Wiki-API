package com.genesis.wiki.controller

import com.genesis.wiki.dto.*
import com.genesis.wiki.service.ItemService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/items")
@CrossOrigin(origins = ["http://localhost:5173"])
class ItemController(
    private val itemService: ItemService
) {
    // ─── 장비 ────────────────────────────────────────────────

    @GetMapping
    fun getEquipmentList(): ResponseEntity<List<EquipmentSummaryDto>> =
        ResponseEntity.ok(itemService.getEquipmentList())

    @GetMapping("/{id}")
    fun getEquipmentDetail(@PathVariable id: Int): ResponseEntity<EquipmentDetailDto> =
        ResponseEntity.ok(itemService.getEquipmentDetail(id))

    @PostMapping
    fun createEquipment(@RequestBody req: EquipmentRequest): ResponseEntity<EquipmentDetailDto> =
        ResponseEntity.ok(itemService.createEquipment(req))

    @PutMapping("/{id}")
    fun updateEquipment(@PathVariable id: Int, @RequestBody req: EquipmentRequest): ResponseEntity<EquipmentDetailDto> =
        ResponseEntity.ok(itemService.updateEquipment(id, req))

    @DeleteMapping("/{id}")
    fun deleteEquipment(@PathVariable id: Int): ResponseEntity<Void> {
        itemService.deleteEquipment(id)
        return ResponseEntity.noContent().build()
    }

    // ─── 전용무기 ─────────────────────────────────────────────

    @GetMapping("/weapons")
    fun getWeaponList(): ResponseEntity<List<ExclusiveWeaponDto>> =
        ResponseEntity.ok(itemService.getExclusiveWeaponList())

    @GetMapping("/weapons/search")
    fun searchWeapons(@RequestParam name: String): ResponseEntity<List<ExclusiveWeaponDto>> =
        ResponseEntity.ok(itemService.searchExclusiveWeapons(name))

    @GetMapping("/weapons/{id}")
    fun getWeaponDetail(@PathVariable id: Int): ResponseEntity<ExclusiveWeaponDto> =
        ResponseEntity.ok(itemService.getExclusiveWeaponDetail(id))

    @PostMapping("/weapons")
    fun createWeapon(@RequestBody req: ExclusiveWeaponRequest): ResponseEntity<ExclusiveWeaponDto> =
        ResponseEntity.ok(itemService.createExclusiveWeapon(req))

    @PutMapping("/weapons/{id}")
    fun updateWeapon(@PathVariable id: Int, @RequestBody req: ExclusiveWeaponRequest): ResponseEntity<ExclusiveWeaponDto> =
        ResponseEntity.ok(itemService.updateExclusiveWeapon(id, req))

    @DeleteMapping("/weapons/{id}")
    fun deleteWeapon(@PathVariable id: Int): ResponseEntity<Void> {
        itemService.deleteExclusiveWeapon(id)
        return ResponseEntity.noContent().build()
    }
}