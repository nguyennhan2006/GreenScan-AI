import { useEffect, useRef, useState } from 'react'
import { setModelMode, testModel } from '../api.js'
import { STATIC } from '../staticApi.js'
import { Chip } from './badges.jsx'

/**
 * The run-time switch for the language-model stages (model-mode-v1): rules only, a model on this
 * machine, or a hosted model for published documents. It changes the runs started from now on;
 * the verdict stays with the rules in every mode.
 */
export default function ModelModeSwitch({ runtime, onRuntime, compact = false }) {
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [test, setTest] = useState(null)
  const [seconds, setSeconds] = useState(0)
  const timer = useRef(null)
  useEffect(() => () => clearInterval(timer.current), [])

  const modes = runtime?.model_modes || []
  if (!modes.length) return null
  const current = runtime.model_mode

  const choose = async (id) => {
    if (STATIC || id === current || busy) return
    setBusy(id); setError(''); setTest(null)
    try {
      onRuntime?.(await setModelMode(id))
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy('')
    }
  }
  const runTest = async () => {
    setTest({ waiting: true }); setSeconds(0)
    const started = Date.now()
    timer.current = setInterval(() => setSeconds(Math.round((Date.now() - started) / 1000)), 500)
    try {
      setTest(await testModel())
    } catch (e) {
      setTest({ ok: false, detail: e.message })
    } finally {
      clearInterval(timer.current)
    }
  }

  return (
    <div data-testid="model-mode">
      <ul className={`grid gap-2 ${compact ? 'sm:grid-cols-3' : 'sm:grid-cols-3'}`}>
        {modes.map((m) => {
          const on = m.id === current
          const off = STATIC || !m.available
          return (
            <li key={m.id}>
              <button
                type="button" disabled={off || !!busy} onClick={() => choose(m.id)} aria-pressed={on}
                data-mode={m.id}
                className={`h-full w-full rounded-lg border p-3 text-left text-xs transition ${on ? 'border-emerald-600 bg-emerald-50 ring-1 ring-emerald-600' : 'border-slate-200 bg-white hover:border-slate-400'} ${off && !on ? 'cursor-not-allowed opacity-60' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${on ? 'bg-emerald-600' : 'bg-slate-300'}`} />
                  <span className="font-semibold text-slate-900">{m.label}</span>
                  {on && <Chip tone="emerald">đang bật</Chip>}
                  {busy === m.id && <span className="text-slate-500">đang đổi…</span>}
                </span>
                {!compact && <span className="mt-1 block text-slate-600">{m.detail}</span>}
                {m.model && m.id !== 'rules' && <span className="mt-1 block font-mono text-xs text-slate-500">{m.model}</span>}
                {!m.available && <span className="mt-1 block text-amber-700">{m.reason}</span>}
              </button>
            </li>
          )
        })}
      </ul>
      <p className="mt-2 text-xs text-slate-500">
        {STATIC
          ? 'Bản xem trên web là bản tĩnh: công tắc này hoạt động khi chạy GreenScan trên máy.'
          : compact
            ? 'Mô hình chỉ đọc thêm và viết lời giải thích. Nó không tự kết luận “ủng hộ” hay “mâu thuẫn”.'
            : 'Áp dụng cho các phiên phân tích bắt đầu từ lúc này. Ở mọi chế độ, mô hình không tự kết luận “ủng hộ” hay “mâu thuẫn”: hai mức này chỉ do luật và phép tính đưa ra. Mô hình đọc thêm, viết lời giải thích, và khi nó đọc khác luật thì tuyên bố được chuyển cho người xác nhận.'}
      </p>
      {current === 'cloud' && !STATIC && (
        <p className="mt-2 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-900">
          Đoạn tuyên bố và đoạn bằng chứng của các cặp khó sẽ được gửi tới nhà cung cấp mô hình. <b>Chỉ dùng cho tài liệu đã công bố.</b>
        </p>
      )}
      {error && <p className="mt-2 rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-800">{error}</p>}
      {current !== 'rules' && !STATIC && (
        <div className="mt-3">
          <button type="button" onClick={runTest} disabled={test?.waiting} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-500">
            {test?.waiting ? `Đang hỏi mô hình… ${seconds} giây` : 'Thử mô hình trên một cặp mẫu'}
          </button>
          {test && !test.waiting && (
            test.ok ? (
              <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs" data-testid="model-test">
                <p className="text-slate-500">Tuyên bố: <span className="text-slate-800">{test.claim}</span></p>
                <p className="mt-1 text-slate-500">Bằng chứng: <span className="text-slate-800">{test.evidence}</span></p>
                <p className="mt-2 text-slate-900"><b>Mô hình trả lời:</b> {test.answer}</p>
                <p className="mt-1 font-mono text-xs text-slate-500">{test.model} · {String(test.seconds).replace('.', ',')} giây</p>
              </div>
            ) : <p className="mt-2 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-900">Không gọi được mô hình: {test.detail}</p>
          )}
        </div>
      )}
    </div>
  )
}
