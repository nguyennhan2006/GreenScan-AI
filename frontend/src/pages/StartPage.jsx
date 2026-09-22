import { useState } from 'react'
import { Leaf } from '../components/Shell.jsx'

/**
 * Entry screen (mockup #1), honest version.
 *
 * There is no account system in the backend: the review API only needs a
 * reviewer name, which it writes into the append-only decision trail. So this
 * screen asks for exactly that and says so — a password field or a Google
 * button would promise an identity check nothing performs.
 */
export default function StartPage({ reviewer, onStart }) {
  const [name, setName] = useState(reviewer || '')
  const [remember, setRemember] = useState(true)

  const submit = (e) => {
    e.preventDefault()
    if (!name.trim()) return
    onStart(name.trim(), remember)
  }

  return (
    <div className="grid min-h-screen bg-slate-50 lg:grid-cols-2">
      <div className="flex items-center justify-center px-6 py-12">
        <form onSubmit={submit} className="w-full max-w-sm">
          <div className="flex items-center gap-2">
            <Leaf className="h-9 w-9 text-emerald-700" />
            <span className="text-3xl font-bold tracking-tight text-[#0F3D2E]">GreenScan</span>
          </div>
          <p className="mt-3 text-base font-medium leading-snug text-slate-700">
            Từ tuyên bố đến bằng chứng,<br />vì một tương lai minh bạch hơn.
          </p>

          <label className="mt-8 block text-sm font-semibold text-slate-700">
            Tên người xem xét
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ví dụ: Quỳnh, Thảo, Nhân"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
            />
          </label>
          <label className="mt-3 flex items-center gap-2 text-xs text-slate-600">
            <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
            Ghi nhớ trên máy này
          </label>

          <button
            type="submit"
            disabled={!name.trim()}
            className="mt-5 w-full rounded-lg bg-[#0F3D2E] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-900 disabled:opacity-40"
          >
            Bắt đầu phiên làm việc
          </button>

          <p className="mt-6 text-xs leading-relaxed text-slate-500">
            Không có tài khoản hay mật khẩu: tên chỉ dùng để ghi vào nhật ký quyết định
            (ai xác nhận / ghi đè tuyên bố nào, lúc nào). Nhật ký này là nguồn của bộ dữ liệu
            gold, nên hãy dùng đúng tên thật trong nhóm.
          </p>
        </form>
      </div>

      <div className="relative hidden overflow-hidden bg-[#0F3D2E] lg:block">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_rgba(52,211,153,0.35),_transparent_55%),radial-gradient(ellipse_at_bottom_right,_rgba(16,185,129,0.25),_transparent_50%)]" />
        <div className="relative flex h-full flex-col justify-between p-12 text-emerald-50">
          <div className="space-y-3">
            <p className="text-sm font-semibold uppercase tracking-widest text-emerald-300">Evidence-first</p>
            <p className="max-w-md text-2xl font-semibold leading-snug text-white">
              “Dữ liệu minh bạch cho những quyết định tốt hơn.”
            </p>
          </div>
          <ul className="space-y-2 text-sm text-emerald-50/85">
            <li>· Mỗi tuyên bố được kiểm theo 5 thuộc tính bắt buộc</li>
            <li>· Mọi kết luận kèm đoạn trích và số trang</li>
            <li>· “Chưa đủ bằng chứng” là một kết quả hợp lệ</li>
            <li>· Người xem xét chốt, AI chỉ đề xuất</li>
          </ul>
          <p className="text-xs text-emerald-50/60">
            GreenScan AI — kiểm chứng tuyên bố môi trường bằng bằng chứng, không cáo buộc.
          </p>
        </div>
      </div>
    </div>
  )
}
