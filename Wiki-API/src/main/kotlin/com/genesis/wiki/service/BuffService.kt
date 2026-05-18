package com.genesis.wiki.service

import com.genesis.wiki.dto.*
import com.genesis.wiki.entity.*
import com.genesis.wiki.repository.*
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class BuffService(
    private val buffRepository: BuffRepository,
    private val debuffRepository: DebuffRepository,
    private val tagRepository: TagRepository
) {

    @Transactional(readOnly = true)
    fun getBuffList(): List<BuffDto> =
        buffRepository.findAll().map { mapBuffToDto(it) }

    @Transactional(readOnly = true)
    fun getBuffDetail(id: Int): BuffDto =
        buffRepository.findDetailById(id)?.let { mapBuffToDto(it) }
            ?: throw NoSuchElementException("버프를 찾을 수 없습니다: $id")

    @Transactional(readOnly = true)
    fun getDebuffList(): List<DebuffDto> =
        debuffRepository.findAll().map { mapDebuffToDto(it) }

    @Transactional(readOnly = true)
    fun getDebuffDetail(id: Int): DebuffDto =
        debuffRepository.findDetailById(id)?.let { mapDebuffToDto(it) }
            ?: throw NoSuchElementException("디버프를 찾을 수 없습니다: $id")

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

    fun mapBuffToDto(buff: Buff): BuffDto = BuffDto(
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
        tags = buff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = buff.sources.map { BuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )

    fun mapDebuffToDto(debuff: Debuff): DebuffDto = DebuffDto(
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
        tags = debuff.tags.map { TagDto(it.tagId, it.name, it.color) },
        sources = debuff.sources.map { DebuffSourceDto(it.sourceType.name, it.sourceId, it.briefDesc) }
    )
}