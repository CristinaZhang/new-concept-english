/**
 * Free Dictionary API — fetches phonetic, definition, examples for an English word.
 * No API key needed.
 * https://dictionaryapi.dev/
 */

const DICT_API = 'https://api.dictionaryapi.dev/api/v2/entries/en'

export async function lookupWord(word) {
  const res = await fetch(`${DICT_API}/${encodeURIComponent(word.toLowerCase())}`)
  if (!res.ok) return null

  const data = await res.json()
  const entry = data[0]
  if (!entry) return null

  // Extract phonetic (first available)
  const phonetic = entry.phonetic
    || entry.phonetics?.find(p => p.text)?.text
    || ''

  // Extract first definition + example
  const meaning = entry.meanings?.[0]
  const definition = meaning?.definitions?.[0]?.definition || ''
  const example = meaning?.definitions?.[0]?.example || ''

  return {
    word: entry.word || word,
    phonetic: phonetic ? phonetic.replace(/^\s*\/|\/\s*$/g, '') : '',
    meaning: definition,
    partOfSpeech: meaning?.partOfSpeech || '',
    example: example,
  }
}
