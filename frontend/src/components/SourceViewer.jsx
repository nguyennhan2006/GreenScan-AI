import { useEffect, useState } from 'react'
import { documentMeta, documentPageUrl, documentUrl } from '../api.js'
import { RELATIONS } from '../lib/claims.js'

/**
 * The audit surface: the cited page, rendered from the stored original, with the
 * quoted passage highlighted.
 *
 * The page image comes from the server rather than a browser PDF engine — the
 * same path then works for scanned reports, where a text-layer highlight would
 * find nothing to mark. The raw file stays one click away for full context.
 */
export default function SourceViewer({ evidence, onClose }) {
  const [page, setPage] = useState(evidence?.page || 1)
  const [meta, setMeta] = useState(null)
  const [state, setState] = useState('loading')

  useEffect(() => { setPage(evidence?.page || 1) }, [evidence])

  useEffect(() => {
    if (!evidence?.doc_id) return
    let alive = true
    documentMeta(evidence.doc_id)
      .then((m) => alive && setMeta(m))
      .catch(() => alive && setMeta(null))
    return () => { alive = false }
  }, [evidence?.doc_id])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft') setPage((p) => Math.max(1, p - 1))
      if (e.key === 'ArrowRight') setPage((p) => (meta?.page_count ? Math.min(meta.page_count, p + 1) : p + 1))
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose, meta?.page_count])

  if (!evidence) return null

  const missingId = !evidence.doc_id
  const rel = RELATIONS[evidence.relation] || RELATIONS.CONTEXT
  const isOriginalPage = page === evidence.page

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="flex max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-xl bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Tài liệu nguồn"
      >
        <header className="flex flex-wrap items-center gap-2 border-b border-slate-200 px-4 py-3">
          <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${rel.className}`}>
            {rel.label}
          </span>
          <span className="min-w-0 truncate text-sm font-medium text-slate-900">
            {evidence.source_name}
          </span>
          <span className="text-xs text-slate-500">
            trang {page}
            {meta?.page_count ? ` / ${meta.page_count}` : ''}
            {evidence.is_table ? ' · bảng' : ''}
            {!isOriginalPage && (
              <span className="ml-1 text-amber-700">(trích dẫn ở trang {evidence.page})</span>
            )}
          </span>

          <div className="ml-auto flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="rounded border border-slate-300 px-2 py-1 text-xs disabled:opacity-40"
            >
              ←
            </button>
            <button
              type="button"
              onClick={() => setPage((p) => (meta?.page_count ? Math.min(meta.page_count, p + 1) : p + 1))}
              disabled={Boolean(meta?.page_count) && page >= meta.page_count}
              className="rounded border border-slate-300 px-2 py-1 text-xs disabled:opacity-40"
            >
              →
            </button>
            {!missingId && (
              <a
                href={documentUrl(evidence.doc_id, page)}
                target="_blank"
                rel="noreferrer"
                className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                Mở PDF gốc
              </a>
            )}
            <button
              type="button"
              onClick={onClose}
              className="rounded bg-slate-900 px-2.5 py-1 text-xs font-semibold text-white"
            >
              Đóng
            </button>
          </div>
        </header>

        <div className="grid min-h-0 flex-1 lg:grid-cols-[1fr_300px]">
        <div className="min-h-0 overflow-auto bg-slate-100 p-4">
          {missingId ? (
            <p className="mx-auto max-w-md rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
              Bằng chứng này không kèm mã tài liệu, nên không mở được bản gốc. Trường hợp
              thường gặp: tuyên bố nhập trực tiếp bằng text thay vì tải file lên.
            </p>
          ) : (
            <>
              {state === 'error' ? (
                <div className="mx-auto max-w-2xl rounded-lg border border-slate-300 bg-white p-4 text-sm">
                  <p className="text-xs text-slate-500">Không dựng được ảnh trang {page} (tệp không phải PDF, hoặc bản gốc không còn trong kho). Trích dẫn vẫn hợp lệ theo tên tài liệu và vị trí; dưới đây là đoạn văn bản đã dùng.</p>
                  <pre className="mt-3 whitespace-pre-wrap rounded bg-amber-50 p-3 font-sans leading-relaxed text-slate-800">{evidence.text}</pre>
                </div>
              ) : (
                <img
                  key={`${evidence.doc_id}-${page}`}
                  src={documentPageUrl(evidence.doc_id, page, evidence.text)}
                  alt={`${evidence.source_name} trang ${page}`}
                  onLoad={() => setState('ready')}
                  onError={() => setState('error')}
                  className="mx-auto max-w-full rounded border border-slate-300 bg-white shadow-sm"
                />
              )}
              {state === 'loading' && (
                <p className="mt-3 text-center text-xs text-slate-500">Đang dựng trang…</p>
              )}
            </>
          )}
        </div>
        <aside className="hidden min-h-0 overflow-auto border-l border-slate-200 p-4 text-xs lg:block">
          <h4 className="text-sm font-semibold text-slate-900">Thông tin bằng chứng</h4>
          <dl className="mt-2 space-y-1.5">
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Tài liệu</dt><dd className="truncate text-right text-slate-900" title={evidence.source_name}>{evidence.source_name}</dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Trang</dt><dd className="font-mono">{evidence.page ?? '—'}</dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Vị trí</dt><dd className="font-mono">{evidence.is_table ? 'bảng' : 'khối văn bản'}</dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Loại nguồn</dt><dd>{evidence.source_type}</dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Lập trường</dt><dd>{rel.labelVi} · <span className="font-mono">{evidence.relation_method}</span></dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Điểm truy xuất</dt><dd className="font-mono">{(evidence.score ?? 0).toFixed(2)}</dd></div>
            <div className="flex justify-between gap-2"><dt className="text-slate-500">Từ khoá / ngữ nghĩa</dt><dd className="font-mono">{Math.round((evidence.lexical_score || 0) * 100)}% / {Math.round((evidence.semantic_score || 0) * 100)}%</dd></div>
            {meta?.sha256 && <div className="flex justify-between gap-2"><dt className="text-slate-500">sha256</dt><dd className="font-mono" title={meta.sha256}>{meta.sha256.slice(0, 4)}…{meta.sha256.slice(-4)}</dd></div>}
          </dl>
          {evidence.relation_reason && <p className="mt-3 rounded-lg bg-slate-50 px-2.5 py-2 text-slate-700">{evidence.relation_reason}</p>}
          <h5 className="mt-3 text-[11px] font-semibold uppercase tracking-wide text-slate-500">Đoạn trích</h5>
          <blockquote className="mt-1 max-h-48 overflow-auto border-l-2 border-amber-400 bg-amber-50/60 py-1 pl-2 leading-relaxed text-slate-800">“{evidence.text}”</blockquote>
          {(evidence.source_qualifiers || []).length > 0 && (
            <ul className="mt-3 space-y-1">
              {evidence.source_qualifiers.map((q, i) => <li key={i} className="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-amber-900">🛡 {typeof q === 'string' ? q : q.label || JSON.stringify(q)}</li>)}
            </ul>
          )}
        </aside>
        </div>

        <footer className="border-t border-slate-200 px-4 py-2">
          <p className="text-xs text-slate-500">
            Phần được tô vàng là đoạn hệ thống trích dẫn. Nếu không thấy vùng tô, đoạn trích
            có thể trải qua nhiều khối bố cục hoặc trang là bản scan — mở PDF gốc để đối chiếu.
          </p>
        </footer>
      </div>
    </div>
  )
}
