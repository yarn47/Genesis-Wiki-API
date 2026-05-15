package com.genesis.wiki

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class WikiApiApplication

fun main(args: Array<String>) {
    runApplication<WikiApiApplication>(*args)
}
