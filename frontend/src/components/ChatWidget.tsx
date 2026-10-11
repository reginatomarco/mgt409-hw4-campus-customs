import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { getJson, imageUrl, postJson, type ChatMessage, type ChatResponse } from '../api'
import { useAuth } from '../authContext'
import { onOpenChat } from '../chatEvents'
import { setChatResults, useChatResults } from '../chatResults'
import { buildPageContext } from '../pageContext'

const SUGGESTIONS = ['What hoodies yall got?', 'Cheapest hoodie?', 'Anything with Handsome Dan?', 'Gift for a Yale mom', 'Saybrook gear']

function greeting(firstName?: string): ChatMessage {
  const hi = firstName ? `Yo ${firstName}.` : 'Yo.'
  const memory = firstName ? '' : ' Log in and I will remember our chats.'
  return {
    role: 'assistant',
    content: `${hi} I'm the Campus Customs assistant. Ask me about gear, sizes or prices.${memory}`,
    products: [],
  }
}

// Renders the small bit of Markdown the agent uses: **bold** and "- " bullet lines.
// Built from React elements (no raw HTML), so a reply can't inject markup.
function renderMarkdown(text: string): ReactNode[] {
  return text.split('\n').map((line, i) => {
    const bullet = /^\s*[-*•]\s+/.test(line)
    const body = line.replace(/^\s*[-*•]\s+/, '')
    const parts = body.split(/\*\*(.+?)\*\*/g).map((part, j) => (j % 2 ? <strong key={j}>{part}</strong> : part))
    return (
      <div key={i} className={bullet ? 'md-bullet' : undefined}>
        {bullet && '• '}
        {parts}
      </div>
    )
  })
}

export default function ChatWidget() {
  const { user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  // The conversation belongs to one account (null = guest). Logging in or out shows a fresh one.
  const [thread, setThread] = useState<{ userId: number | null; messages: ChatMessage[] }>({
    userId: null,
    messages: [greeting()],
  })
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const chatResults = useChatResults()

  const userId = user?.id ?? null
  const messages = thread.userId === userId ? thread.messages : [greeting(user?.first_name)]

  function addMessage(message: ChatMessage) {
    setThread((t) => ({
      userId,
      messages: [...(t.userId === userId ? t.messages : [greeting(user?.first_name)]), message],
    }))
  }

  // Load a logged-in shopper's saved conversation.
  useEffect(() => {
    if (!user) return
    getJson<ChatMessage[]>('/api/chat/history')
      .then((history) => setThread({ userId: user.id, messages: [greeting(user.first_name), ...history] }))
      .catch(() => setThread({ userId: user.id, messages: [greeting(user.first_name)] }))
  }, [user])

  // Other pages (e.g. "Ask the assistant" on a product page) can open the chat with a draft question.
  useEffect(
    () =>
      onOpenChat((draft) => {
        setOpen(true)
        if (draft) setInput(draft)
        setTimeout(() => inputRef.current?.focus(), 50)
      }),
    [],
  )

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, thread, open, sending])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return
    addMessage({ role: 'user', content: text, products: [] })
    setInput('')
    setSending(true)
    try {
      const res = await postJson<ChatResponse>('/api/chat', {
        message: text,
        // What's on screen, so the assistant knows what "this" or "these" means.
        page: buildPageContext(location.pathname, location.search, chatResults),
      })
      addMessage({
        role: 'assistant',
        content: res.reply,
        products: res.products,
        pageResultsTotal: res.page_results?.total,
      })
      // Search results go to the Products page as full product cards.
      if (res.page_results && res.page_results.products.length > 0) {
        setChatResults({ ...res.page_results, question: text })
        navigate('/products?view=chat')
      }
    } catch (err) {
      addMessage({ role: 'assistant', content: `⚠️ ${(err as Error).message}`, products: [] })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel" role="dialog" aria-label="Campus Customs chat">
          <div className="chat-header">
            <span className="chat-avatar">🐶</span>
            <div className="chat-title">
              <strong>Campus Customs Assistant</strong>
              <span><i className="status-dot" /> Online · knows every hoodie</span>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-turn ${m.role}`}>
                <div className={`chat-bubble ${m.role}`}>
                  {m.role === 'assistant' ? renderMarkdown(m.content) : m.content}
                </div>
                {m.pageResultsTotal !== undefined && (
                  <Link to="/products?view=chat" className="chat-page-link">
                    ▦ {m.pageResultsTotal} {m.pageResultsTotal === 1 ? 'result' : 'results'} on the page →
                  </Link>
                )}
                {m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat-product">
                        <img src={imageUrl(p.image_file_path)} alt="" loading="lazy" />
                        <span className="chat-product-name">{p.name}</span>
                        <span className="chat-product-price">${p.price.toFixed(2)}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {messages.length === 1 && !sending && (
              <div className="chat-suggestions">
                {SUGGESTIONS.map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => {
                      setInput(q)
                      inputRef.current?.focus()
                    }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
            {sending && (
              <div className="chat-bubble assistant typing" aria-label="Assistant is typing">
                <span /><span /><span />
              </div>
            )}
            <div ref={endRef} />
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about hoodies, sizes, prices..."
              aria-label="Message"
              maxLength={1000}
            />
            <button type="submit" disabled={sending || !input.trim()}>Send</button>
          </form>
        </div>
      )}
      <button
        type="button"
        className={`chat-toggle ${open ? 'is-open' : ''}`}
        onClick={() => setOpen(!open)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : '💬'}
        {!open && <span className="chat-toggle-label">Ask the Bulldog</span>}
      </button>
    </div>
  )
}
