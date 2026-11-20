import { Component, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Keys this app keeps in the browser (reviewer name, web-demo decisions, tips, tours).
const STORE_PREFIXES = ['gs.', 'greenscan.']

/**
 * Last line of defence: a page that throws must never leave a blank screen. The reviewer sees what
 * happened and two ways out: reload, or clear what this app stored in the browser (an older visit can
 * leave data a newer version does not expect) and reload.
 */
class CrashScreen extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('GreenScan: lỗi hiển thị', error, info?.componentStack)
  }

  clearAndReload = () => {
    try {
      Object.keys(localStorage).filter((k) => STORE_PREFIXES.some((p) => k.startsWith(p))).forEach((k) => localStorage.removeItem(k))
    } catch { /* trình duyệt chặn bộ nhớ: chỉ tải lại */ }
    window.location.hash = ''
    window.location.reload()
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-canvas)] p-6">
        <div className="max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-lg font-semibold text-slate-900">Trang này chưa hiển thị được</p>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            Thường do trình duyệt còn giữ dữ liệu của một lần mở bản cũ. Bấm <b>Xoá dữ liệu cũ và tải lại</b>: chỉ xoá tên người soát và các quyết định thử trên trình duyệt này, không ảnh hưởng gì khác.
          </p>
          <p className="mt-3 rounded-lg bg-slate-50 px-3 py-2 font-mono text-xs text-slate-500">{String(this.state.error?.message || this.state.error).slice(0, 300)}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" onClick={this.clearAndReload} className="rounded-xl bg-[#047857] px-4 py-2 text-sm font-semibold text-white hover:bg-[#065f46]">Xoá dữ liệu cũ và tải lại</button>
            <button type="button" onClick={() => window.location.reload()} className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Chỉ tải lại</button>
          </div>
        </div>
      </div>
    )
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CrashScreen>
      <App />
    </CrashScreen>
  </StrictMode>,
)
