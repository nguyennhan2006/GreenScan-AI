import { useState } from 'react'
import { labelOf } from '../lib/labels.js'
import { RELATIONS, locationOf } from '../lib/claims.js'

/** Contradictions first — they change the conclusion, so they must not be scrolled to. */
const ORDER = { CONTRADICTS: 0, SUPPORTS: 1, PARTIAL: 2, CONTEXT: 3 }

function RelationBadge({ relation }) {
  const r = RELATIONS[relation] || RELATIONS.CONTEXT
  return (
    <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${r.className}`}>
      {r.label}
    </span>
  )
}

function AbstainNotice() {
  return (
    <div className="rounded-lg border border-slate-300 bg-slate-50 p-4">
      <p className="text-sm font-semibold text-slate-900">Chưa đủ bằng chứng để kết luận</p>
      <p className="mt-1 text-xs leading-relaxed text-slate-600">
        Đây là một trạng thái hợp lệ của quy trình, ngang hàng với “ủng hộ” hay “mâu thuẫn” —
        không phải lỗi hệ thống. Nó cũng không có nghĩa doanh nghiệp vi phạm; nó có nghĩa là
        tài liệu hiện có chưa đủ để kiểm chứng.
      </p>
      <p className="mt-2 text-xs text-slate-600">
        Bước tiếp theo: bổ sung tài liệu nguồn, hoặc chuyển cho người xem xét.
      </p>
    </div>
  )
}

export default function EvidencePanel({ evidence, onJumpToSource, compact = false }) {
  const [showAll, setShowAll] = useState(false)
  if (!evidence.length) return <AbstainNotice />

  const sorted = [...evidence].sort(
    (a, b) => (ORDER[a.relation] ?? 9) - (ORDER[b.relation] ?? 9),
  )
  // Compact view: the passages that carry a reading; when none does, the two closest ones.
  const deciding = sorted.filter((e) => e.relation && e.relation !== 'CONTEXT')
  const shown = !compact || showAll ? sorted : (deciding.length ? deciding : sorted.slice(0, 2))
  const folded = sorted.length - shown.length

  return (
    <div className="space-y-2.5">
      {shown.map((e, i) => (
        <article
          key={e.chunk_id || i}
          className={`rounded-lg border bg-white p-3 ${
            e.relation === 'CONTRADICTS' ? 'border-red-300' : 'border-slate-200'
          }`}
        >
          <header className="flex flex-wrap items-center gap-2">
            <RelationBadge relation={e.relation} />
            <span className="text-xs text-slate-600">{locationOf(e)}</span>
            <button
              type="button"
              onClick={() => onJumpToSource?.(e)}
              disabled={!onJumpToSource}
              title={
                onJumpToSource
                  ? 'Mở tài liệu gốc tại vị trí này'
                  : 'Máy chủ chưa phục vụ tài liệu gốc nên chưa mở được đúng trang'
              }
              className="ml-auto rounded border border-slate-300 px-2 py-0.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Mở nguồn →
            </button>
          </header>

          {e.relation_reason && (
            <p className="mt-1.5 text-xs font-medium text-slate-700">{e.relation_reason}</p>
          )}

          {e.suspicious_instruction && (
            <p className="mt-2 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs text-red-800">
              Đoạn này chứa văn bản giống chỉ thị điều khiển mô hình. Đã đánh dấu và không dùng
              làm căn cứ tự động.
            </p>
          )}

          <p className="mt-2 max-h-32 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
            {e.text}
          </p>

          {/* Retrieval scores explain ordering, not truth — smallest type on the card. */}
          <p className="mt-1.5 text-xs text-slate-400">
            nguồn: {labelOf('source_type', e.source_type)}
            {!compact && <> · khớp từ khóa {Math.round((e.lexical_score || 0) * 100)}% · ngữ nghĩa {Math.round((e.semantic_score || 0) * 100)}%</>}
          </p>
        </article>
      ))}
      {compact && folded > 0 && (
        <button type="button" onClick={() => setShowAll(true)} className="text-xs font-semibold text-emerald-800 hover:underline" data-testid="more-evidence">
          Xem thêm {folded} đoạn chỉ liên quan
        </button>
      )}
    </div>
  )
}
