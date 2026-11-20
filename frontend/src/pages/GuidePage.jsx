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
    doIt: 'Dưới khung tải tệp, bấm ô “Hòa Phát (báo cáo thật)”. Hai tệp của Hòa Phát hiện ra: báo cáo phát triển bền vững 2025 và báo cáo thường niên 2024. Bấm “Bắt đầu phân tích”.',
    look: 'Cột vai trò của từng tệp, và nhãn “Ngoại tuyến — không gửi tài liệu ra ngoài”.',
    mean: 'Báo cáo bền vững là tài liệu cần kiểm. Báo cáo thường niên là tài liệu đối chiếu, nơi máy đi tìm bằng chứng. Máy chạy ngay trên máy tính này, mất khoảng 2–3 phút.',
  },
  {
    title: 'Đọc hàng đợi',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở bước 2 · Hàng đợi',
    doIt: 'Xem thẻ “Cần soát” (7 mục với bộ mẫu), rồi thẻ “Ngoài hàng đợi” và “Mẫu kiểm ngẫu nhiên”.',
    look: 'Mỗi mục có câu gốc, tên tệp và số trang. Cuối dòng có con số nhỏ như “61/90”.',
    mean: 'Hàng đợi là danh sách nên mở trước, mỗi mục ghi lý do. “61/90” là điểm để xếp thứ tự mở, không phải mức vi phạm. Mục ngoài hàng đợi không bị bỏ quên: mỗi mục ghi rõ vì sao lượt này chưa soát.',
  },
  {
    title: 'Mở một tuyên bố',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở hàng đợi để chọn mục số 1',
    doIt: 'Bấm “Mở” ở mục số 1 (câu “mức độ tự chủ điện năng rất cao”, trang 7).',
    look: 'Nhãn kết luận có màu ở trên cùng. Bấm “Xem đầy đủ” ở góc phải để thấy bảng “Thuộc tính bắt buộc”.',
    mean: 'Máy xem câu có đủ năm thông tin không: chỉ số (nói về cái gì), giá trị (con số và đơn vị), kỳ báo cáo (năm nào), năm gốc (so với năm nào) và phạm vi (nhà máy, công ty hay cả tập đoàn). Năm gốc chỉ cần khi câu nói tăng, giảm hoặc đặt mục tiêu. Mỗi thông tin hiện “Có”, “Thiếu” hoặc “Không áp dụng”; chỗ thiếu có “Việc cần làm”. Câu này nói giảm phát thải nhưng không có con số, không nói năm nào và không có năm gốc để so (thiếu 3 trên 5). Bằng chứng tìm được chỉ khớp về chủ đề, nên máy ghi “Ủng hộ một phần”.',
  },
  {
    title: 'Xem bằng chứng ở trang gốc',
    needsRun: true,
    doIt: 'Trong tuyên bố đang mở, ở khung “Bằng chứng”, bấm “Mở nguồn” ở đoạn báo cáo thường niên trang 86. Chưa thấy đoạn đó thì bấm “Xem thêm … đoạn chỉ liên quan”.',
    look: 'Trang gốc với đoạn được tô vàng, tên tệp, số trang, dòng “nguồn” và mã băm.',
    mean: 'Mỗi đoạn bằng chứng có nhãn quan hệ: Ủng hộ, Một phần, Mâu thuẫn hoặc Chỉ liên quan. Dòng “nguồn” cho biết ai viết đoạn đó: “Tài liệu của chính doanh nghiệp” chỉ cho thấy các báo cáo nói giống nhau, chưa phải xác minh độc lập. Mã băm là dấu vân tay của tệp: đổi một chữ là mã đổi, nên biết chắc đã kiểm đúng bản nào.',
  },
  {
    title: 'Xem phép kiểm tra số',
    to: (id) => `/runs/${id}`, needsRun: true, button: 'Mở hàng đợi',
    doIt: 'Trên trang hàng đợi, cuộn tới khung “Thủ tục trên số liệu công bố”.',
    look: 'Phép cộng bảng khí nhà kính trang 39: phát thải phạm vi 1 cộng phạm vi 2, so với tổng doanh nghiệp công bố.',
    mean: 'Máy chỉ cộng hai số khi chúng cùng bảng, cùng năm, cùng đơn vị. Phép tính hiện trên màn hình để bạn tự bấm máy kiểm lại, không phải máy đoán.',
  },
  {
    title: 'Ra quyết định',
    needsRun: true,
    doIt: 'Ở cuối trang tuyên bố, ghi lý do rồi chọn một trong: “Xác nhận gợi ý của máy”, “Máy sai, tôi sửa”, “Chưa kết luận”, hoặc “Yêu cầu thêm bằng chứng”.',
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

// Who does what: the machine reads and proposes, the reviewer decides.
const ROLES = [
  ['Máy làm', 'Đọc tài liệu (cả trang quét), tách các câu nói về môi trường, tìm đoạn đối chiếu trong tài liệu khác, so con số, cộng lại bảng số, rồi gợi ý kết luận và thứ tự nên xem.'],
  ['Bạn làm', 'Mở từng mục theo thứ tự, đọc trang gốc, xác nhận hoặc sửa kết luận, ghi lý do.'],
  ['Bạn nhận được', 'Danh sách cần soát kèm trang bằng chứng, và một giấy làm việc để ký. Không phải lời kết tội doanh nghiệp.'],
]

const VERDICT_MEANING = [
  ['SUPPORTED', 'Một tài liệu khác nêu đúng con số, hoặc xác nhận rõ, khớp cả chỉ số, kỳ và phạm vi. Xem dòng “nguồn”: nếu tài liệu đó cũng do chính doanh nghiệp viết thì mới là các báo cáo nói giống nhau.'],
  ['PARTIALLY_SUPPORTED', 'Tìm được đoạn cùng chủ đề, nhưng thiếu con số, năm hoặc phạm vi để so cho chắc. Đây là kết luận hay gặp nhất với câu viết chung chung.'],
  ['UNSUPPORTED', 'Có tài liệu liên quan nhưng không tài liệu nào chứng minh được.'],
  ['CONTRADICTED', 'Có đoạn nói khác tuyên bố, ví dụ con số lệch quá sai số cho phép. Cần bạn đọc kỹ trang gốc.'],
  ['INSUFFICIENT_EVIDENCE', 'Các tài liệu đã nạp chưa có gì để so. Không có nghĩa là tuyên bố sai: có thể cần nạp thêm tài liệu.'],
]

const TERMS = [
  ['Tuyên bố', 'Câu doanh nghiệp tự nói về môi trường, cần kiểm.'],
  ['Bằng chứng', 'Đoạn văn, bảng số hoặc văn bản dùng để đối chiếu với tuyên bố.'],
  ['Kết luận', 'Máy gợi ý tuyên bố được bằng chứng ủng hộ tới đâu. Bạn xác nhận hoặc ghi đè.'],
  ['Hàng đợi', 'Danh sách mục nên mở trước, mỗi mục có lý do.'],
  ['Điểm ưu tiên', 'Con số dùng để xếp thứ tự mở. Không phải mức vi phạm.'],
  ['Thuộc tính', 'Năm thông tin một tuyên bố nên có: chỉ số, giá trị, kỳ báo cáo, năm gốc, phạm vi.'],
  ['Không áp dụng', 'Thông tin đó không cần cho câu này, ví dụ năm gốc với câu không nói tăng, giảm hay mục tiêu.'],
  ['Giá trị', 'Con số kèm đơn vị đo, ví dụ 23.474.480 tCO₂e.'],
  ['Năm gốc', 'Năm dùng để so sánh, ví dụ “giảm 20% so với năm 2020”.'],
  ['Kỳ báo cáo', 'Số liệu thuộc năm nào, hoặc năm tài chính nào.'],
  ['Phạm vi', 'Tuyên bố nói về một nhà máy, công ty mẹ hay cả tập đoàn.'],
  ['Phát thải phạm vi 1, 2, 3', 'Phạm vi 1 là phát thải trực tiếp. Phạm vi 2 là từ điện, hơi mua vào. Phạm vi 3 là trong chuỗi giá trị.'],
  ['tCO₂e', 'Tấn CO₂ tương đương: đơn vị chung để cộng các loại khí nhà kính với nhau.'],
  ['Đọc ảnh chữ (OCR)', 'Cách máy đọc trang quét. Số đọc chưa chắc được đánh dấu, và kết luận dựa trên số đó bị hạ xuống “Ủng hộ một phần” để bạn xem trang gốc.'],
  ['Mã băm', 'Dấu vân tay của tệp: đổi một chữ là mã đổi.'],
  ['Nguồn độc lập', 'Tài liệu không do chính doanh nghiệp viết, ví dụ báo cáo kiểm toán, quyết định của cơ quan nhà nước.'],
  ['Giấy làm việc', 'Bản ghi những gì đã kiểm, chưa kiểm và quyết định của bạn, để ký.'],
  ['Máy gợi ý', 'Kết quả do máy tạo, chưa có người xem.'],
  ['Bộ quy tắc nội bộ', 'Quy định riêng của tổ chức bạn (tính năng thử nghiệm). Không bao giờ đổi kết luận kiểm chứng.'],
]

// Questions a first-time user asks after the first run.
const FAQ = [
  ['Vì sao gần như mọi câu đều là “Ủng hộ một phần”?',
    'Phần lớn câu trong báo cáo bền vững là câu mô tả chung, không có con số hay năm. Không có số thì không có gì để so cho chắc, nên máy chỉ ghi “một phần”. Hãy dùng hàng đợi để chọn câu nên xem; đừng dùng tỷ lệ kết luận để chấm điểm doanh nghiệp.'],
  ['Tài liệu có bị gửi ra ngoài không?',
    'Không, khi nhãn ghi “Ngoại tuyến”: mọi bước chạy trên máy này. Mô hình ngôn ngữ trên mạng chỉ dùng khi đơn vị bật trong Cài đặt, và chỉ đọc những câu quy tắc không tự quyết được.'],
  ['Máy kết luận sai thì làm gì?',
    'Chọn “Ghi đè”, chọn kết luận đúng và ghi lý do. Quyết định của bạn được lưu kèm tên và thời điểm; kết luận của máy vẫn giữ lại để so.'],
  ['Mục ngoài hàng đợi có bị bỏ qua không?',
    'Không. Mỗi mục ghi lý do chưa soát ở lượt này, và giấy làm việc liệt kê chúng trong phần “chưa kiểm”.'],
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
          Báo cáo của doanh nghiệp có nhiều câu nói về môi trường, ví dụ “giảm 20% phát thải so với năm 2020”. GreenScan tìm những câu đó,
          tìm đoạn trong tài liệu khác để đối chiếu, rồi xếp câu nào nên xem trước. Bạn là người quyết định.
        </p>
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-3">
          {ROLES.map(([t, d]) => (
            <div key={t} className="rounded-lg bg-white/70 p-3"><dt className="font-semibold text-emerald-950">{t}</dt><dd className="mt-0.5 text-emerald-900">{d}</dd></div>
          ))}
        </dl>
        <p className="mt-3 text-sm text-emerald-900">Làm lần lượt bảy bước dưới đây trên bộ mẫu Hòa Phát. Xong bước nào thì đánh dấu bước đó.</p>
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
                    : <Link to={s.to(runId)} className="mt-3 inline-block rounded-lg bg-[#047857] px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-900">{s.button}</Link>)}
                </div>
              </div>
            </li>
          )
        })}
      </ol>

      <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
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

      <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
        <h3 className="text-base font-semibold text-slate-900">Giải thích từ ngữ</h3>
        <dl className="mt-2 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          {TERMS.map(([t, d]) => (
            <div key={t}><dt className="font-semibold text-slate-800">{t}</dt><dd className="text-slate-700">{d}</dd></div>
          ))}
        </dl>
      </section>

      <section className="rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4">
        <h3 className="text-base font-semibold text-slate-900">Câu hỏi hay gặp</h3>
        <dl className="mt-2 space-y-3 text-sm">
          {FAQ.map(([q, a]) => (
            <div key={q}><dt className="font-semibold text-slate-800">{q}</dt><dd className="mt-0.5 text-slate-700">{a}</dd></div>
          ))}
        </dl>
      </section>

      <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
        <h3 className="text-base font-semibold">GreenScan không làm những việc này</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Không kết luận doanh nghiệp vi phạm hay “tẩy xanh”. Máy chỉ chỉ ra chỗ cần người xem.</li>
          <li>Không thay người soát xét. Mọi kết luận cần bạn xác nhận hoặc ghi đè.</li>
          <li>Không đọc đúng mọi câu: khoảng 3 trên 10 câu máy tách ra không phải tuyên bố (đo trên 146 câu, 05/11/2026). Bạn vẫn cần lọc.</li>
          <li>Chưa đối chiếu hoá đơn, chứng từ; chưa đọc báo cáo kiểm toán tài chính đính kèm; chưa so với dữ liệu ngành.</li>
          <li>Chưa so cùng một chỉ số giữa các năm một cách tự động, và chưa xác định nghĩa vụ pháp lý cụ thể (chỉ tìm văn bản cùng chủ đề).</li>
          <li>Chưa kiểm tờ xác nhận đảm bảo của bên thứ ba (đang làm).</li>
        </ul>
      </section>
    </div>
  )
}
