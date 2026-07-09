/**
 * Free translation API for English → Chinese.
 * No API key needed. Uses MyMemory Translation API.
 * https://mymemory.translated.net/doc/spec.php
 */

const TRANSLATE_API = 'https://api.mymemory.translated.net/get'

export async function translateWord(word) {
  const url = `${TRANSLATE_API}?q=${encodeURIComponent(word.toLowerCase())}&langpair=en|zh-CN`
  const res = await fetch(url)
  if (!res.ok) return null

  const data = await res.json()
  const translated = data.responseData?.translatedText

  if (!translated || translated.toLowerCase() === word.toLowerCase()) return null

  return {
    word: word,
    meaning: translated,
  }
}

/**
 * Combined lookup: English dictionary for phonetic + translation for Chinese meaning.
 */
const DICT_API = 'https://api.dictionaryapi.dev/api/v2/entries/en'

export async function lookupWord(word) {
  // Parallel: fetch phonetic + Chinese translation
  const [dictRes, transRes] = await Promise.all([
    fetch(`${DICT_API}/${encodeURIComponent(word.toLowerCase())}`),
    translateWord(word),
  ])

  const phonetic = dictRes.ok
    ? await dictRes.json().then(d => {
        const entry = d[0]
        if (!entry) return ''
        return entry.phonetic
          || entry.phonetics?.find(p => p.text)?.text
          || ''
      }).catch(() => '')
    : ''

  const meaning = transRes?.meaning || ''

  if (!meaning && !phonetic) return null

  return {
    word: word,
    phonetic: phonetic ? phonetic.replace(/^\s*\/|\/\s*$/g, '') : '',
    meaning: meaning,
    partOfSpeech: '',
    example: '',
  }
}
