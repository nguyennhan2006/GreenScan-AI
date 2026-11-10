import { useState } from 'react'
import { Link } from '../lib/router.jsx'
import { STATUS_LABELS } from '../components/badges.jsx'

/**
 * Hướng dẫn cho người mới: kịch bản làm quen 10 phút trên bộ mẫu Hòa Phát.
 * Nội dung khớp docs/05-ui/KICH_BAN_HUONG_DAN_NGUOI_MOI.md; từ ngữ theo CHUAN_NGON_NGU_GIAO_DIEN.md.
 * Tiến độ từng bước lưu trong trình duyệt (gs.guide.done), không gửi đi đâu.
 */

const KEY = 'gs.guide.done'
const load = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]') } catch { return [] } }
const save = (v) => { try { localStorage.setItem(KEY, JSON.stringify(v)); localStorage.setItem('gs.guide.seen', '1') } catch { /* không lưu được thì thôi */ } }

const STEPS = [
  {
    title: 'Tải bộ mẫu và bắt đầu',
    to: () => '/new', button: 'Mở bước 1 · Tải tài liệu',
    doIt: 'Bấm “Nạp bộ mẫu để thử”. Hai tệp của Hòa Phát hiện ra: báo cáo phát triển bền vững 2025 và báo cáo thường niên 2024. Bấm “Bắt đầu”.',
    look: 'Cột vai trò của từng tệp, và nhãn xanh “Ngoại tuyến — không gửi tài liệu ra ngoài” ở góc trên.',
    mean: 'Báo cáo bền vững là tài liệu cần kiểm. Báo cáo thường niên là tài liệu đối chiếu, nơi máy đi tìm bằng chứng. Máy chạy ngay trên máy tính này, khoảng 2–3 phút.',
  },
  {
    title: 'Đọc hàng đợi',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở bước 2 · Hàng đợi',
    doIt: 'Xem thẻ “Cần soát” (khoảng 9 mục) rồi thẻ “Ngoài hàng đợi”.',
    look: 'Mỗi mục có câu gốc, tên tệp và số trang. Con số nhỏ như “61/90” ở cuối dòng.',
    mean: 'Hàng đợi là danh sách nên mở trước, có ghi lý do. “61/90” là điểm ưu tiên để mở trước, không phải mức vi phạm. Mục ngoài hàng đợi không bị bỏ quên: mỗi mục ghi rõ vì sao lượt này chưa soát.',
  },
  {
    title: 'Mở một tuyên bố',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở hàng đợi để chọn mục số 2',
    doIt: 'Bấm “Mở” ở mục số 2 (câu “mức độ tự chủ điện năng rất cao”, trang 7).',
    look: 'Nhãn kết luận màu ở trên cùng, rồi bảng “Thuộc tính bắt buộc”.',
    mean: 'Máy kiểm năm thuộc tính: chỉ số, năm gốc, kỳ báo cáo, phạm vi, bằng chứng và phương pháp. Mỗi thuộc tính là Có, Một phần hoặc Thiếu, kèm “Việc cần làm”. Câu này thiếu năm gốc và kỳ báo cáo, nên chỉ “Ủng hộ một phần”.',
  },
  {
    title: 'Xem bằng chứng ở trang gốc',
    needsRun: true,
    doIt: 'Trong tuyên bố đang mở, chọn thẻ “Bằng chứng”, rồi bấm “Mở nguồn” ở đoạn báo cáo thường niên trang 86.',
    look: 'Trang gốc với đoạn được tô vàng, tên tệp, số trang và mã băm.',
    mean: 'Mỗi đoạn bằng chứng có nhãn quan hệ: Ủng hộ, Một phần, Mâu thuẫn hoặc Chỉ liên quan. Mã băm là dấu vân tay của tệp: đổi một chữ là mã đổi, nên biết chắc đã kiểm đúng bản nào.',
  },
  {
    title: 'Xem phép kiểm tra số',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở hàng đợi',
    doIt: 'Trên trang hàng đợi, cuộn tới khung “Thủ tục trên số liệu công bố”.',
    look: 'Phép cộng bảng khí nhà kính trang 39: phát thải phạm vi 1 cộng phạm vi 2, so với tổng doanh nghiệp công bố.',
    mean: 'Máy chỉ cộng hai số khi chúng cùng bảng, cùng năm, cùng đơn vị. Phép tính hiện trên màn hình để bạn tự kiểm lại, không phải máy đoán.',
  },
  {
    title: 'Ra quyết định',
    needsRun: true,
    doIt: 'Ở cuối trang tuyên bố, chọn một trong: Xác nhận, Ghi đè, Yêu cầu thêm bằng chứng, hoặc Chưa kết luận. Ghi lý do rồi lưu.',
    look: 'Dòng “Lịch sử” hiện tên bạn và thời điểm.',
    mean: 'Kết luận của máy chỉ là gợi ý; người quyết định là bạn. Quyết định chỉ ghi thêm, không xoá được, nên người sau đọc lại được vì sao bạn chọn như vậy.',
  },
  {
    title: 'Xem và in giấy làm việc',
    to: (id) => `/runs/${id}/export`, needsRun: true, button: 'Mở bước 4 · Giấy làm việc',
    doIt: 'Mở giấy làm việc, đọc lướt các mục, rồi bấm in hoặc lưu PDF.',
    look: 'Phạm vi tài liệu kèm mã băm, các thủ tục đã chạy, kết quả từng mục kèm trang, những gì KHÔNG được kiểm, quyết định của bạn, và chỗ ký.',
    mean: 'Đây là bản ghi để ký duyệt. Nó nói rõ cả phần chưa kiểm, để không ai hiểu nhầm là đã kiểm hết.',
  },
]

const VERDICT_MEANING = [
  ['SUPPORTED', 'Có bằng chứng khớp đủ chỉ số, phạm vi và kỳ.'],
  ['PARTIALLY_SUPPORTED', 'Có bằng chứng cùng chủ đề nhưng thiếu số, kỳ hoặc phạm vi để so.'],
  ['UNSUPPORTED', 'Có tài liệu liên quan nhưng không tài liệu nào chứng minh được.'],
  ['CONTRADICTED', 'Có bằng chứng nói khác với tuyên bố. Cần bạn đọc kỹ nguồn.'],
  ['INSUFFICIENT_EVIDENCE', 'Kho tài liệu chưa có gì để so. Không có nghĩa là tuyên bố sai.'],
]

const TERMS = [
  ['Tuyên bố', 'Câu doanh nghiệp tự nói về môi trường, cần kiểm.'],
  ['Bằng chứng', 'Đoạn văn, bảng số hoặc văn bản dùng để đối chiếu với tuyên bố.'],
  ['Kết luận', 'Máy gợi ý tuyên bố được bằng chứng ủng hộ tới đâu. Bạn xác nhận hoặc ghi đè.'],
  ['Hàng đợi', 'Danh sách mục nên mở trước, mỗi mục có lý do.'],
  ['Điểm ưu tiên', 'Con số dùng để xếp thứ tự mở. Không phải mức vi phạm.'],
  ['Năm gốc', 'Năm dùng để so sánh, ví dụ “giảm 20 % so với năm 2020”.'],
  ['Kỳ báo cáo', 'Số liệu thuộc năm nào, hoặc năm tài chính nào.'],
  ['Phạm vi', 'Tuyên bố nói về một nhà máy, công ty mẹ hay cả tập đoàn.'],
  ['Phát thải phạm vi 1, 2, 3', 'Phạm vi 1 là phát thải trực tiếp. Phạm vi 2 là từ năng lượng mua vào. Phạm vi 3 là trong chuỗi giá trị.'],
  ['Mã băm', 'Dấu vân tay của tệp: đổi một chữ là mã đổi.'],
  ['Nguồn độc lập', 'Tài liệu không do chính doanh nghiệp viết, ví dụ báo cáo kiểm toán, quyết định của cơ quan nhà nước.'],
  ['Giấy làm việc', 'Bản ghi những gì đã kiểm, chưa kiểm và quyết định của bạn, để ký.'],
  ['Máy gợi ý', 'Kết quả do máy tạo, chưa có người xem.'],
  ['Bộ quy tắc nội bộ', 'Quy định riêng của tổ chức bạn (tính năng thử nghiệm). Không bao giờ đổi kết luận kiểm chứng.'],
]

export default function GuidePage({ runId }) {
  const [done, setDone] = useState(load)
  const toggle = (i) => {
    const next = done.includes(i) ? done.filter((x) => x !== i) : [...done, i]
    setDone(next); save(next)
  }
  const reset = () => { setDone([]); save([]) }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
        <h2 className="text-lg font-semibold text-emerald-950">Làm quen GreenScan trong khoảng 10 phút</h2>
        <p className="mt-1 text-sm text-emerald-900">
          GreenScan giúp bạn soát các tuyên bố môi trường trong báo cáo doanh nghiệp. Máy đọc và tìm bằng chứng, quy tắc kiểm tra, bạn là người quyết định.
          Kết quả là thứ tự cần soát kèm trang bằng chứng, không phải lời kết tội.
        </p>
        <p className="mt-2 text-sm text-emerald-900">Làm lần lượt bảy bước dưới đây trên bộ mẫu Hòa Phát. Xong bước nào thì đánh dấu bước đó.</p>
        <div className="mt-3 flex items-center gap-3 text-sm">
          <span className="font-semibold text-emerald-950">Đã xong {done.length}/{STEPS.length} bước</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-emerald-100"><div className="h-full bg-emerald-600" style={{ width: `${(done.length / STEPS.length) * 100}%` }} /></div>
          <button type="button" onClick={reset} className="text-xs text-emerald-800 underline">Làm lại từ đầu</button>
        </div>
      </section>

      <ol className="space-y-3">
        {STEPS.map((s, i) => {
          const ok = done.includes(i)
          const blocked = s.needsRun && !runId
          return (
            <li key={s.title} className={`rounded-xl border bg-white p-4 ${ok ? 'border-emerald-300' : 'border-slate-200'}`}>
              <div className="flex items-start gap-3">
                <button type="button" onClick={() => toggle(i)} aria-label={ok ? 'Bỏ đánh dấu' : 'Đánh dấu đã xong'}
                  className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${ok ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
                  {ok ? '✓' : i + 1}
                </button>
                <div className="min-w-0 flex-1">
                  <h3 className="text-base font-semibold text-slate-900">{s.title}</h3>
                  <dl className="mt-2 grid gap-1.5 text-sm">
                    <div><dt className="inline font-semibold text-slate-700">Làm gì: </dt><dd className="inline text-slate-800">{s.doIt}</dd></div>
                    <div><dt className="inline font-semibold text-slate-700">Nhìn vào đâu: </dt><dd className="inline text-slate-800">{s.look}</dd></div>
                    <div><dt className="inline font-semibold text-slate-700">Hiểu thế nào: </dt><dd className="inline text-slate-800">{s.mean}</dd></div>
                  </dl>
                  {s.to && (blocked
                    ? <p className="mt-2 text-xs text-slate-500">Làm bước 1 trước để có phiên phân tích.</p>
                    : <Link to={s.to(runId)} className="mt-3 inline-block rounded-lg bg-[#0F3D2E] px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-900">{s.button}</Link>)}
                </div>
              </div>
            </li>
          )
        })}
      </ol>

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-base font-semibold text-slate-900">Năm loại kết luận</h3>
        <table className="mt-2 w-full text-sm">
          <tbody>
            {VERDICT_MEANING.map(([k, m]) => (
              <tr key={k} className="border-t border-slate-100 align-top">
                <td className="w-56 py-2 pr-3 font-semibold text-slate-800">{STATUS_LABELS[k]}</td>
                <td className="py-2 text-slate-700">{m}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-base font-semibold text-slate-900">Giải thích từ ngữ</h3>
        <dl className="mt-2 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          {TERMS.map(([t, d]) => (
            <div key={t}><dt className="font-semibold text-slate-800">{t}</dt><dd className="text-slate-700">{d}</dd></div>
          ))}
        </dl>
      </section>

      <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
        <h3 className="text-base font-semibold">GreenScan không làm những việc này</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Không kết luận doanh nghiệp vi phạm hay “tẩy xanh”. Máy chỉ chỉ ra chỗ cần người xem.</li>
          <li>Không thay người soát xét. Mọi kết luận cần bạn xác nhận hoặc ghi đè.</li>
          <li>Không đọc đúng mọi câu: khoảng 3 trên 10 câu máy tách ra không phải tuyên bố (đo trên 146 câu, 05/11/2026). Bạn vẫn cần lọc.</li>
        </ul>
      </section>
    </div>
  )
}
