import { useState } from 'react'
import { approveOrgPack, draftOrgPack, previewOrgPack, retireOrgPack, uploadOrgPack } from '../api.js'

/**
 * Org pack gửi qua giao diện (org-pack-v1): tải lên, duyệt (bốn mắt), thu hồi, thử trên một câu,
 * và soạn bản nháp từ văn bản chính sách. Gói tải lên luôn là bản nháp; người duyệt phải khác người tải lên.
 */

const STATUS = {
  draft: ['Bản nháp: chưa áp dụng', 'bg-amber-100 text-amber-900'],
  approved: ['Đã duyệt: chọn được khi phân tích', 'bg-emerald-100 text-emerald-800'],
  retired: ['Đã thu hồi', 'bg-slate-100 text-slate-500'],
}

function reviewerName() {
  try { return localStorage.getItem('greenscan.reviewer') || '' } catch { return '' }
}

export default function OrgPackManager({ uploaded = [], onChanged }) {
  const [name, setName] = useState(reviewerName)
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)
  const [draft, setDraft] = useState({ orgId: '', orgName: '', policyText: '', useLlm: false })
  const [preview, setPreview] = useState({ pack: '', text: '', result: null })

  const act = async (fn, ok) => {
    if (!name.trim()) { setMessage({ error: 'Cần tên người thao tác (vết kiểm toán).' }); return }
    setBusy(true)
    setMessage(null)
    try {
      const result = await fn()
      setMessage({ ok: ok(result) })
      onChanged?.()
    } catch (e) {
      setMessage({ error: e.message })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-4 rounded-2xl border border-slate-200/70 bg-white shadow-sm p-4 text-xs">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-sm font-semibold text-slate-900">Gửi bộ quy tắc của tổ chức bạn</h3>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Tên người thao tác"
          className="ml-auto w-48 rounded-lg border border-slate-300 px-2 py-1" />
      </div>
      <p className="text-slate-600">
        Gói tải lên luôn vào kho dưới dạng <b>bản nháp</b> (tên người duyệt ghi sẵn trong tệp bị xoá). Người duyệt phải
        <b> khác</b> người tải lên. Chỉ bản đã duyệt mới chọn được khi phân tích, và quy tắc nội bộ không bao giờ đổi kết luận kiểm chứng.
      </p>

      {message?.error && <p className="rounded-lg bg-red-50 px-3 py-2 text-red-800">{message.error}</p>}
      {message?.ok && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-emerald-800">{message.ok}</p>}

      <div className="rounded-lg border border-slate-200 p-3">
        <p className="font-semibold text-slate-800">1. Tải lên</p>
        <p className="mt-1 text-slate-500">Một tệp .zip của thư mục pack, hoặc <code>pack.yaml</code> cùng các tài liệu nó dẫn chiếu (.md, .txt, .pdf, .docx).</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <input type="file" multiple accept=".zip,.yaml,.yml,.md,.txt,.pdf,.docx" onChange={(e) => setFiles([...e.target.files])} />
          <button type="button" disabled={busy || !files.length}
            onClick={() => act(() => uploadOrgPack(files, name.trim()), (r) => `Đã lưu ${r.org_id} ${r.version} (bản nháp, ${r.n_rules} quy tắc)${r.self_approval_removed ? '; tên người duyệt trong tệp đã được xoá' : ''}.`)}
            className="rounded-lg bg-emerald-600 px-3 py-1.5 font-semibold text-white disabled:opacity-40">Tải lên</button>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 p-3">
        <p className="font-semibold text-slate-800">2. Soạn nháp từ văn bản chính sách</p>
        <p className="mt-1 text-slate-500">Mỗi câu nêu nghĩa vụ (“phải”, “không được”, “bắt buộc”…) thành một quy tắc dẫn đúng điều khoản. Kiểu kiểm máy không nhận ra thành quy tắc “người soát tự xem”.</p>
        <div className="mt-2 grid gap-2 sm:grid-cols-2">
          <input value={draft.orgId} onChange={(e) => setDraft({ ...draft, orgId: e.target.value })} placeholder="org_id (vd ngan_hang_abc)" className="rounded-lg border border-slate-300 px-2 py-1" />
          <input value={draft.orgName} onChange={(e) => setDraft({ ...draft, orgName: e.target.value })} placeholder="Tên tổ chức" className="rounded-lg border border-slate-300 px-2 py-1" />
        </div>
        <textarea value={draft.policyText} onChange={(e) => setDraft({ ...draft, policyText: e.target.value })} rows={5}
          placeholder="Dán văn bản chính sách (đánh số §1, §2.1… để quy tắc dẫn chiếu được)" className="mt-2 w-full rounded-lg border border-slate-300 px-2 py-1.5" />
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-1.5"><input type="checkbox" checked={draft.useLlm} onChange={(e) => setDraft({ ...draft, useLlm: e.target.checked })} /> Để mô hình soạn (cần mạng; luôn qua cùng bộ kiểm lược đồ)</label>
          <button type="button" disabled={busy || !draft.orgId.trim() || !draft.orgName.trim() || !draft.policyText.trim()}
            onClick={() => act(() => draftOrgPack({ orgId: draft.orgId.trim(), orgName: draft.orgName.trim(), uploadedBy: name.trim(), policyText: draft.policyText, useLlm: draft.useLlm }),
              (r) => r.status === 'invalid' ? `Bản nháp chưa hợp lệ: ${r.errors.join('; ')}` : `Đã soạn ${r.pack.rules.length} quy tắc (${r.method}) và lưu ${r.stored?.org_id} ${r.stored?.version} dưới dạng bản nháp. ${(r.notes || []).join(' ')}`)}
            className="rounded-lg border border-slate-400 px-3 py-1.5 font-semibold text-slate-800 disabled:opacity-40">Soạn nháp</button>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 p-3">
        <p className="font-semibold text-slate-800">3. Kho đã tải lên: duyệt, thu hồi, thử</p>
        {uploaded.length === 0 && <p className="mt-1 text-slate-500">Chưa có gói nào.</p>}
        <ul className="mt-2 divide-y divide-slate-100">
          {uploaded.map((p) => {
            const [label, cls] = STATUS[p.status] || [p.status, 'bg-slate-100']
            return (
              <li key={`${p.org_id}@${p.version}`} className="flex flex-wrap items-center gap-2 py-2">
                <span className="font-semibold text-slate-900">{p.org_name || p.org_id}</span>
                <span className="font-mono text-xs text-slate-500">{p.org_id}@{p.version}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>{label}</span>
                <span className="text-slate-500">tải lên: {p.uploaded_by}{p.approved_by ? ` · duyệt: ${p.approved_by}` : ''} · {p.n_rules} quy tắc</span>
                <span className="ml-auto flex gap-1.5">
                  {p.status === 'draft' && (
                    <button type="button" disabled={busy}
                      onClick={() => act(() => approveOrgPack(p.org_id, p.version, name.trim()), () => `Đã duyệt ${p.org_id}@${p.version}.`)}
                      className="rounded border border-emerald-500 px-2 py-0.5 text-emerald-700">Duyệt</button>
                  )}
                  {p.status !== 'retired' && (
                    <button type="button" disabled={busy}
                      onClick={() => act(() => retireOrgPack(p.org_id, p.version, name.trim()), () => `Đã thu hồi ${p.org_id}@${p.version}.`)}
                      className="rounded border border-slate-300 px-2 py-0.5 text-slate-600">Thu hồi</button>
                  )}
                  <button type="button" onClick={() => setPreview({ ...preview, pack: `${p.org_id}@${p.version}`, result: null })}
                    className="rounded border border-slate-300 px-2 py-0.5 text-slate-600">Thử</button>
                </span>
              </li>
            )
          })}
        </ul>
        {preview.pack && (
          <div className="mt-2 rounded-lg bg-slate-50 p-2.5">
            <p className="font-mono text-xs text-slate-500">Thử {preview.pack} trên một câu (không có bằng chứng; bản nháp được xem như đã duyệt)</p>
            <div className="mt-1 flex gap-2">
              <input value={preview.text} onChange={(e) => setPreview({ ...preview, text: e.target.value })} placeholder="Năm 2024, công ty giảm 8% phát thải CO2 trên mỗi tấn thép."
                className="flex-1 rounded-lg border border-slate-300 px-2 py-1" />
              <button type="button" disabled={!preview.text.trim()}
                onClick={async () => { try { setPreview({ ...preview, result: await previewOrgPack(preview.pack, preview.text) }) } catch (e) { setPreview({ ...preview, result: { error: e.message } }) } }}
                className="rounded-lg border border-slate-400 px-3 py-1 font-semibold">Chạy</button>
            </div>
            {preview.result?.error && <p className="mt-1 text-red-700">{preview.result.error}</p>}
            {preview.result?.lines && (
              <pre className="mt-2 whitespace-pre-wrap font-mono text-xs text-slate-700">{preview.result.attributes}{'\n\n'}{preview.result.lines.join('\n')}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
