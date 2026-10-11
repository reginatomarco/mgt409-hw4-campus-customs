// Lets any page open the chat widget with a suggested question already typed in.

const EVENT = 'cc-open-chat'

export function openChat(draft?: string) {
  window.dispatchEvent(new CustomEvent<string | undefined>(EVENT, { detail: draft }))
}

export function onOpenChat(handler: (draft?: string) => void): () => void {
  const listener = (e: Event) => handler((e as CustomEvent<string | undefined>).detail)
  window.addEventListener(EVENT, listener)
  return () => window.removeEventListener(EVENT, listener)
}
