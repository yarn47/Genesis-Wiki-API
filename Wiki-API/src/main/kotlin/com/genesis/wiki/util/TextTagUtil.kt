package com.genesis.wiki.util

/**
 * [버프명]{색상} 형태의 태그에서 이름만 추출
 * 예: "공격력의 [150%]{red} 피해. [아찔한 회피]{green} 획득"
 * → ["아찔한 회피"] (숫자/수치 제외, green 태그만)
 */
object TextTagUtil {

    private val TAG_PATTERN = Regex("""\[([^\]]+)]\{(\w+)}""")

    // 모든 태그에서 이름 추출
    fun extractAllTagNames(text: String?): List<String> {
        if (text.isNullOrBlank()) return emptyList()
        return TAG_PATTERN.findAll(text).map { it.groupValues[1] }.toList()
    }

    // 특정 색상의 태그만 추출 (버프/디버프는 green/orange)
    fun extractTagNamesByColor(text: String?, color: String): List<String> {
        if (text.isNullOrBlank()) return emptyList()
        return TAG_PATTERN.findAll(text)
            .filter { it.groupValues[2] == color }
            .map { it.groupValues[1] }
            .toList()
    }

    // 버프 이름 추출 (green 태그)
    fun extractBuffNames(text: String?): List<String> =
        extractTagNamesByColor(text, "green")

    // 디버프 이름 추출 (orange 태그)
    fun extractDebuffNames(text: String?): List<String> =
        extractTagNamesByColor(text, "orange")

    // 여러 텍스트에서 버프/디버프 이름 한번에 추출
    fun extractAllBuffNames(texts: List<String?>): List<String> =
        texts.flatMap { extractBuffNames(it) }.distinct()

    fun extractAllDebuffNames(texts: List<String?>): List<String> =
        texts.flatMap { extractDebuffNames(it) }.distinct()
}