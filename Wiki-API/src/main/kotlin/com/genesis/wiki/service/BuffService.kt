package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.*
import com.genesis.wiki.repository.*
import com.genesis.wiki.util.TextTagUtil
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class BuffService(
    private val buffRepository: BuffRepository,
    private val debuffRepository: DebuffRepository,
    private val tagRepository: TagRepository
) {

    @Transactional(readOnly = true)
    fun getBuffList(): List<BuffDto> {
        val usage = buildUsage()
        return buffRepository.findAll().map { mapBuffToDto(it, usage[EffectKey.buff(it.buffId)].orEmpty()) }
    }

    @Transactional(readOnly = true)
    fun getBuffDetail(id: Int): BuffDto =
        buffRepository.findDetailById(id)?.let { mapBuffToDto(it, buildUsage()[EffectKey.buff(id)].orEmpty()) }
            ?: throw NoSuchElementException("버프를 찾을 수 없습니다: $id")

    @Transactional(readOnly = true)
    fun getDebuffList(): List<DebuffDto> {
        val usage = buildUsage()
        return debuffRepository.findAll().map { mapDebuffToDto(it, usage[EffectKey.debuff(it.debuffId)].orEmpty()) }
    }

    @Transactional(readOnly = true)
    fun getDebuffDetail(id: Int): DebuffDto =
        debuffRepository.findDetailById(id)?.let { mapDebuffToDto(it, buildUsage()[EffectKey.debuff(id)].orEmpty()) }
            ?: throw NoSuchElementException("디버프를 찾을 수 없습니다: $id")

    // ─── 사용자(캐릭터) 찾기 ────────────────────────────────
    // 캐릭터 텍스트에 이름이 박힌 버프뿐 아니라, 그 버프가 다시 걸어주는 버프까지 따라간다
    // (예: 자드 → 우아한 리듬 → 치명적인 비트)

    private data class EffectKey(val kind: String, val id: Int) {
        companion object {
            fun buff(id: Int) = EffectKey("B", id)
            fun debuff(id: Int) = EffectKey("D", id)
        }
    }

    private fun buildUsage(): Map<EffectKey, List<CharacterBriefDto>> {
        val users = mutableMapOf<EffectKey, MutableSet<CharacterBriefDto>>()
        buffRepository.findUsingCharacters().forEach {
            users.getOrPut(EffectKey.buff(it.effectId)) { mutableSetOf() }
                .add(CharacterBriefDto(it.characterId, it.characterName, it.thumbnailUrl))
        }
        debuffRepository.findUsingCharacters().forEach {
            users.getOrPut(EffectKey.debuff(it.effectId)) { mutableSetOf() }
                .add(CharacterBriefDto(it.characterId, it.characterName, it.thumbnailUrl))
        }

        val buffs = buffRepository.findAll()
        val debuffs = debuffRepository.findAll()

        val byName = mutableMapOf<String, EffectKey>()
        buffs.forEach { byName[it.name] = EffectKey.buff(it.buffId) }
        debuffs.forEach { byName[it.name] = EffectKey.debuff(it.debuffId) }
        // "관능의 아라베스크 5" 처럼 레벨이 붙은 이름도 본체로
        fun keyOf(label: String) = byName[label] ?: byName[label.replace(Regex("\\s*\\d+$"), "")]

        val links = mutableMapOf<EffectKey, MutableSet<EffectKey>>()
        fun addLinks(key: EffectKey, texts: List<String?>) {
            (TextTagUtil.extractAllBuffNames(texts) + TextTagUtil.extractAllDebuffNames(texts))
                .mapNotNull { keyOf(it) }
                .filter { it != key }
                .forEach { links.getOrPut(key) { mutableSetOf() }.add(it) }
        }
        buffs.forEach { addLinks(EffectKey.buff(it.buffId), it.levels.map { l -> l.effectText } + it.description) }
        debuffs.forEach { addLinks(EffectKey.debuff(it.debuffId), it.levels.map { l -> l.effectText } + it.description) }

        // 연쇄가 깊어야 서너 단계라 몇 번만 돌려도 충분
        repeat(5) {
            var changed = false
            links.forEach { (from, tos) ->
                val src = users[from] ?: return@forEach
                tos.forEach { to -> if (users.getOrPut(to) { mutableSetOf() }.addAll(src)) changed = true }
            }
            if (!changed) return@repeat
        }

        return users.mapValues { (_, v) -> v.sortedBy { it.characterId } }
    }

    @Transactional(readOnly = true)
    fun getTagList(): List<TagDto> =
        tagRepository.findAll().map { TagDto(it.tagId, it.name, it.color) }

    @Transactional
    fun createBuff(request: BuffRequest): BuffDto {
        val buff = Buff(
            name = request.name,
            description = request.description,
            iconUrl = request.iconUrl,
            duration = request.duration,
            maxStack = request.maxStack,
            hasLevels = request.hasLevels
        )
        request.levels.forEach { lvl ->
            buff.levels.add(BuffLevel(
                buff = buff, level = lvl.level,
                levelName = lvl.levelName ?: "${request.name} ${lvl.level}",
                effectText = lvl.effectText,
                duration = lvl.duration,
                maxStack = lvl.maxStack
            ))
        }
        buff.tags.addAll(tagRepository.findAllById(request.tagIds))
        return mapBuffToDto(buffRepository.save(buff))
    }

    @Transactional
    fun updateBuff(id: Int, request: BuffRequest): BuffDto {
        val buff = buffRepository.findById(id)
            .orElseThrow { NoSuchElementException("버프를 찾을 수 없습니다: $id") }
        buff.name = request.name
        buff.description = request.description
        buff.iconUrl = request.iconUrl
        buff.duration = request.duration
        buff.maxStack = request.maxStack
        buff.hasLevels = request.hasLevels
        buff.levels.clear()
        buffRepository.saveAndFlush(buff)
        request.levels.forEach { lvl ->
            // updateBuff
            buff.levels.add(BuffLevel(
                buff = buff, level = lvl.level,
                levelName = lvl.levelName ?: "${request.name} ${lvl.level}",
                effectText = lvl.effectText,
                duration = lvl.duration,   // 추가
                maxStack = lvl.maxStack    // 추가
            ))
        }
        buff.tags.clear()
        buff.tags.addAll(tagRepository.findAllById(request.tagIds))
        return mapBuffToDto(buffRepository.save(buff))
    }

    @Transactional
    fun deleteBuff(id: Int) = buffRepository.deleteById(id)

    @Transactional
    fun createDebuff(request: DebuffRequest): DebuffDto {
        val debuff = Debuff(
            name = request.name,
            description = request.description,
            iconUrl = request.iconUrl,
            duration = request.duration,
            maxStack = request.maxStack,
            hasLevels = request.hasLevels
        )
        request.levels.forEach { lvl ->
            debuff.levels.add(DebuffLevel(
                debuff = debuff, level = lvl.level,
                levelName = lvl.levelName ?: "${request.name} ${lvl.level}",
                effectText = lvl.effectText
            ))
        }
        debuff.tags.addAll(tagRepository.findAllById(request.tagIds))
        return mapDebuffToDto(debuffRepository.save(debuff))
    }

    @Transactional
    fun updateDebuff(id: Int, request: DebuffRequest): DebuffDto {
        val debuff = debuffRepository.findById(id)
            .orElseThrow { NoSuchElementException("디버프를 찾을 수 없습니다: $id") }
        debuff.name = request.name
        debuff.description = request.description
        debuff.iconUrl = request.iconUrl
        debuff.duration = request.duration
        debuff.maxStack = request.maxStack
        debuff.hasLevels = request.hasLevels
        debuff.levels.clear()
        debuffRepository.saveAndFlush(debuff)
        request.levels.forEach { lvl ->
            // updateDebuff
            debuff.levels.add(DebuffLevel(
                debuff = debuff, level = lvl.level,
                levelName = lvl.levelName ?: "${request.name} ${lvl.level}",
                effectText = lvl.effectText,
                duration = lvl.duration,   // 추가
                maxStack = lvl.maxStack    // 추가
            ))
        }
        debuff.tags.clear()
        debuff.tags.addAll(tagRepository.findAllById(request.tagIds))
        return mapDebuffToDto(debuffRepository.save(debuff))
    }

    @Transactional
    fun deleteDebuff(id: Int) = debuffRepository.deleteById(id)

    @Transactional
    fun createTag(request: TagRequest): TagDto {
        val tag = tagRepository.save(Tag(name = request.name, color = request.color))
        return TagDto(tag.tagId, tag.name, tag.color)
    }

    @Transactional
    fun deleteTag(id: Int) = tagRepository.deleteById(id)

    fun mapBuffToDto(buff: Buff, usedBy: List<CharacterBriefDto> = emptyList()): BuffDto = BuffDto(
        buffId = buff.buffId,
        name = buff.name,
        description = buff.description,
        iconUrl = buff.iconUrl,
        duration = buff.duration,
        maxStack = buff.maxStack,
        hasLevels = buff.hasLevels,
        levels = buff.levels.sortedBy { it.level }.map {
            BuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack)
        },
        tags = buff.tags.sortedBy { it.tagId }.map { TagDto(it.tagId, it.name, it.color) },
        sources = buff.sources.map { BuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) },
        usedBy = usedBy
    )

    fun mapDebuffToDto(debuff: Debuff, usedBy: List<CharacterBriefDto> = emptyList()): DebuffDto = DebuffDto(
        debuffId = debuff.debuffId,
        name = debuff.name,
        description = debuff.description,
        iconUrl = debuff.iconUrl,
        duration = debuff.duration,
        maxStack = debuff.maxStack,
        hasLevels = debuff.hasLevels,
        levels = debuff.levels.sortedBy { it.level }.map {
            DebuffLevelDto(it.level, it.levelName, it.effectText, it.duration, it.maxStack)
        },
        tags = debuff.tags.sortedBy { it.tagId }.map { TagDto(it.tagId, it.name, it.color) },
        sources = debuff.sources.map { DebuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) },
        usedBy = usedBy
    )
}