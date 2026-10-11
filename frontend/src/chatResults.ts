// Holds the latest search results the chat assistant sent to the page.
// The chat widget writes them; the Products page reads them. Kept in sessionStorage so a
// refresh, or going back from a product page, still shows the same results.

import { useSyncExternalStore } from 'react'
import type { PageResults } from './api'

export interface ChatResults extends PageResults {
  question: string // the shopper message that produced these results
}

const KEY = 'cc-chat-results'
const listeners = new Set<() => void>()
let current: ChatResults | null = load()

function load(): ChatResults | null {
  try {
    const raw = sessionStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as ChatResults) : null
  } catch {
    return null
  }
}

function emit() {
  listeners.forEach((l) => l())
}

export function setChatResults(results: ChatResults) {
  current = results
  sessionStorage.setItem(KEY, JSON.stringify(results))
  emit()
}

export function clearChatResults() {
  current = null
  sessionStorage.removeItem(KEY)
  emit()
}

export function useChatResults(): ChatResults | null {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    () => current,
  )
}
