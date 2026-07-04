import { useState } from 'react'
import { chat } from '../api.js'

const SUGGEST = ['Why kill the losers?', 'What if I 2x the winners?', 'Which platform is most efficient?']

export default function ChatBox({ context }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)

  const send = async (text) => {
    const question = (text ?? input).trim()
    if (!question || busy) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setBusy(true)
    try {
      const { answer } = await chat(question, context)
      setMessages((prev) => [...prev, { role: 'bot', text: answer }])
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'bot', text: e.message || 'Error.' }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="chat fade fade-delay-3">
      <div className="micro">Ask the co-pilot</div>
      <div className="msgs">
        {messages.length === 0 && (
          <div className="suggest">
            {SUGGEST.map((s) => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}
          </div>
        )}
        {messages.map((m, i) => <div key={i} className={`msg ${m.role}`}>{m.text}</div>)}
        {busy && <div className="msg bot">Thinking…</div>}
      </div>
      <div className="composer">
        <input
          value={input}
          placeholder="Ask about any call…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') send() }}
        />
        <button className="btn" onClick={() => send()} disabled={busy}>Send</button>
      </div>
    </div>
  )
}
