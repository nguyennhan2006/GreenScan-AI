/**
 * CodeMirror 6 set-up for GreenScan Studio: the report as lines, claims as lint diagnostics.
 *
 * Claims live in our own state field (`claimsField`), mapped through every edit,
 * so the Inspector and the Problems panel always know where a claim is now. The
 * lint layer (wavy underline, gutter dot, hover card with actions) is derived
 * from that field whenever the set of open claims changes; between those moments
 * the lint extension maps its own ranges through edits.
 */
import { Compartment, EditorState, RangeSet, StateEffect, StateField } from '@codemirror/state'
import {
  Decoration, EditorView, GutterMarker, drawSelection, gutter, highlightActiveLine, keymap, lineNumbers,
} from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { lintGutter, nextDiagnostic, previousDiagnostic, setDiagnostics } from '@codemirror/lint'
import {
  SearchQuery, findNext, findPrevious, highlightSelectionMatches, search, searchKeymap, setSearchQuery,
} from '@codemirror/search'

// ---------- claims ----------

export const setClaims = StateEffect.define()
export const flashRange = StateEffect.define()

export const claimsField = StateField.define({
  create: () => [],
  update(claims, tr) {
    for (const e of tr.effects) if (e.is(setClaims)) return e.value
    if (!tr.docChanged) return claims
    return claims.map((c) => {
      const from = tr.changes.mapPos(c.from, 1)
      const to = Math.max(from, tr.changes.mapPos(c.to, -1))
      return from === c.from && to === c.to ? c : { ...c, from, to }
    })
  },
})

/** Claim under a position, preferring the shortest range. */
export function claimAt(state, pos) {
  let best = null
  for (const c of state.field(claimsField)) {
    if (pos >= c.from && pos <= c.to && (!best || c.to - c.from < best.to - best.from)) best = c
  }
  return best
}

// ---------- flash highlight (hovering a Problems row) ----------

const flashMark = Decoration.mark({ class: 'cm-flash' })
const flashField = StateField.define({
  create: () => Decoration.none,
  update(deco, tr) {
    deco = deco.map(tr.changes)
    for (const e of tr.effects) {
      if (e.is(flashRange)) deco = e.value ? Decoration.set([flashMark.range(e.value.from, e.value.to)]) : Decoration.none
    }
    return deco
  },
  provide: (f) => EditorView.decorations.from(f),
})

// ---------- active claim (the one under the cursor) ----------

const activeMark = Decoration.mark({ class: 'cm-claim-active' })
const activeField = StateField.define({
  create: () => Decoration.none,
  update(deco, tr) {
    if (!tr.selection && !tr.docChanged && !tr.effects.some((e) => e.is(setClaims))) return deco
    const c = claimAt(tr.state, tr.state.selection.main.head)
    return c && !c.resolved && c.to > c.from ? Decoration.set([activeMark.range(c.from, c.to)]) : Decoration.none
  },
  provide: (f) => EditorView.decorations.from(f),
})

// ---------- page gutter ----------

class PageMarker extends GutterMarker {
  constructor(page) { super(); this.page = page }
  eq(other) { return other.page === this.page }
  toDOM() {
    const el = document.createElement('span')
    el.textContent = `tr. ${this.page}`
    el.title = `Bắt đầu trang ${this.page} của bản gốc`
    return el
  }
}

function pageMarkers(doc, pages) {
  const ranges = []
  let previous = null
  for (let i = 0; i < Math.min(pages.length, doc.lines); i++) {
    const page = pages[i]
    if (page != null && page !== previous) ranges.push(new PageMarker(page).range(doc.line(i + 1).from))
    previous = page
  }
  return RangeSet.of(ranges)
}

function pageGutter(pages) {
  const field = StateField.define({
    create: (state) => pageMarkers(state.doc, pages),
    update: (set, tr) => set.map(tr.changes),
  })
  return [field, gutter({ class: 'cm-page-gutter', markers: (v) => v.state.field(field) })]
}

// ---------- lint diagnostics from claims ----------

const SEVERITY_WORD = { error: 'Nghiêm trọng', warning: 'Cần xem', info: 'Thông tin' }

function el(tag, cls, text) {
  const node = document.createElement(tag)
  if (cls) node.className = cls
  if (text != null) node.textContent = text
  return node
}

/** The hover card: verdict, the strongest evidence, legal basis with its verification label. */
function card(c) {
  const root = el('div', 'gs-card')
  const head = el('div', 'gs-card-head')
  head.append(el('span', `gs-sev gs-sev-${c.severity}`, SEVERITY_WORD[c.severity]), el('b', null, c.status_label))
  if (c.in_queue) head.append(el('span', 'gs-pill', `Hàng đợi #${c.priority_rank}`))
  root.append(head, el('div', 'gs-card-msg', c.message))
  const ev = c.evidence?.[0]
  if (ev) {
    const box = el('div', 'gs-card-ev')
    box.append(el('div', 'gs-card-label', `Bằng chứng · ${ev.source_name}, tr. ${ev.page ?? '—'}${ev.independent ? ' · độc lập' : ' · cùng doanh nghiệp'}`))
    box.append(el('div', 'gs-card-quote', `“${ev.text.slice(0, 220)}${ev.text.length > 220 ? '…' : ''}”`))
    root.append(box)
  }
  const src = c.legal?.sources?.[0]
  if (src) {
    const box = el('div', 'gs-card-ev')
    box.append(el('div', 'gs-card-label', `Căn cứ · ${src.document}`))
    box.append(el('div', src.verified ? 'gs-ok' : 'gs-unverified', src.verification_label))
    root.append(box)
  }
  const n = c.suggestions?.length || 0
  root.append(el('div', 'gs-card-foot', n ? `${n} đề xuất sửa · Ctrl+. để mở` : 'Không còn đề xuất tự động'))
  return root
}

export function lintFromClaims(state, handlers) {
  const open = state.field(claimsField).filter((c) => !c.resolved && c.to > c.from)
  return setDiagnostics(state, open.map((c) => ({
    from: c.from,
    to: c.to,
    severity: c.severity,
    message: c.message,
    source: c.status_label,
    renderMessage: () => card(c),
    actions: [
      ...(c.suggestions?.length ? [{ name: 'Đề xuất sửa', apply: () => handlers.quickFix(c.id) }] : []),
      { name: 'Xem bằng chứng', apply: () => handlers.showEvidence(c.id) },
      { name: 'Bỏ qua…', apply: () => handlers.ignore(c.id) },
    ],
  })))
}

// ---------- theme ----------

const FONT = '"Inter Variable", ui-sans-serif, system-ui, "Segoe UI", Arial, sans-serif'
const theme = EditorView.theme({
  '&': { height: '100%', backgroundColor: '#fff', color: '#1e293b' },
  '&.cm-focused': { outline: 'none' },
  '.cm-scroller': { fontFamily: FONT, lineHeight: '1.75' },
  '.cm-content': { padding: '20px 0 48px', maxWidth: '900px' },
  '.cm-line': { padding: '0 40px 10px 14px' },
  '.cm-gutters': { backgroundColor: '#fff', border: 'none', color: '#a3afbf' },
  '.cm-lineNumbers .cm-gutterElement': { padding: '0 6px 0 18px', fontSize: '0.8em', fontVariantNumeric: 'tabular-nums' },
  '.cm-page-gutter': { minWidth: '52px', paddingLeft: '4px' },
  '.cm-page-gutter .cm-gutterElement span': {
    display: 'inline-block', marginTop: '3px', padding: '0 6px', borderRadius: '999px', fontSize: '10.5px', fontWeight: '600',
    lineHeight: '18px', color: '#15603f', backgroundColor: '#e7f5ee',
  },
  '.cm-gutter-lint': { width: '22px' },
  '.cm-gutter-lint .cm-gutterElement': { padding: '2px 0 0' },
  '.cm-activeLine': { backgroundColor: 'transparent' },
  '.cm-activeLineGutter': { backgroundColor: 'transparent', color: '#0f3d2e', fontWeight: '600' },
  '.cm-selectionBackground': { backgroundColor: '#d1fae5 !important' },
  '&.cm-focused .cm-selectionBackground': { backgroundColor: '#bbf7d0 !important' },
  '.cm-cursor': { borderLeftColor: '#0f3d2e', borderLeftWidth: '2px' },
  // Claims read as highlighted passages, tinted by severity, rather than wavy underlines.
  '.cm-lintRange': { backgroundImage: 'none !important', borderRadius: '3px', paddingBottom: '1px', transition: 'background-color .15s' },
  '.cm-lintRange-error': { backgroundColor: 'rgba(254, 205, 202, .55)', boxShadow: 'inset 0 -2px 0 rgba(220, 38, 38, .55)' },
  '.cm-lintRange-warning': { backgroundColor: 'rgba(254, 240, 199, .85)', boxShadow: 'inset 0 -2px 0 rgba(245, 158, 11, .5)' },
  '.cm-lintRange-info': { backgroundColor: 'rgba(224, 242, 254, .9)', boxShadow: 'inset 0 -2px 0 rgba(14, 165, 233, .45)' },
  '.cm-claim-active, .cm-claim-active .cm-lintRange': { backgroundColor: '#fde68a !important', boxShadow: 'inset 0 -2px 0 #d97706 !important' },
  '.cm-flash': { backgroundColor: '#fcd34d', borderRadius: '3px' },
  '.cm-searchMatch': { backgroundColor: 'rgba(52, 211, 153, .3)', outline: '1px solid rgba(16, 185, 129, .5)', borderRadius: '2px' },
  '.cm-searchMatch-selected': { backgroundColor: 'rgba(16, 185, 129, .55)' },
  '.cm-selectionMatch': { backgroundColor: 'rgba(16, 185, 129, .12)' },
  '.cm-panels': { backgroundColor: '#f8fafc', color: '#334155', borderColor: '#e2e8f0' },
  '.cm-panels.cm-panels-top': { borderBottom: '1px solid #e2e8f0' },
  '.cm-search': { fontFamily: FONT, fontSize: '12px', padding: '6px 10px' },
  '.cm-search input, .cm-search button': { borderRadius: '6px' },
  '.cm-textfield': { border: '1px solid #cbd5e1', padding: '3px 8px', backgroundColor: '#fff' },
  '.cm-button': { backgroundImage: 'none', backgroundColor: '#fff', border: '1px solid #cbd5e1', padding: '3px 10px' },
  '.cm-tooltip': { border: '1px solid #e2e8f0', borderRadius: '12px', boxShadow: '0 16px 40px -8px rgba(15,23,42,.22)', overflow: 'hidden', backgroundColor: '#fff' },
  '.cm-tooltip-lint': { maxWidth: '460px' },
  '.cm-diagnostic': { padding: '12px 14px', borderLeftWidth: '0' },
  '.cm-diagnostic-error, .cm-diagnostic-warning, .cm-diagnostic-info': { borderLeft: 'none' },
  '.cm-diagnosticAction': { backgroundColor: '#0f3d2e', borderRadius: '7px', padding: '4px 10px', marginTop: '10px', marginRight: '6px', fontSize: '12px', fontWeight: '600' },
  '.cm-diagnosticAction:hover': { backgroundColor: '#14533e' },
  '.cm-diagnosticSource': { display: 'none' },
})

const zoomSlot = new Compartment()
const zoomTheme = (px) => EditorView.theme({ '&': { fontSize: `${px}px` } })

/** Move to the next/previous claim, leaving the cursor at its start: the claim highlight marks it, not a selection. */
function toDiagnostic(view, move) {
  if (!move(view)) return false
  view.dispatch({ selection: { anchor: view.state.selection.main.from } })
  return true
}

/**
 * Build the editor. `opts`: doc, pages, readOnly, handlers {quickFix, showEvidence, ignore,
 * accept, reject, save, select, change}.
 */
export function createEditor(parent, opts) {
  const h = opts.handlers
  const keys = [
    { key: 'F8', run: (v) => toDiagnostic(v, nextDiagnostic), preventDefault: true },
    { key: 'Shift-F8', run: (v) => toDiagnostic(v, previousDiagnostic), preventDefault: true },
    { key: 'Mod-.', run: (v) => { const c = claimAt(v.state, v.state.selection.main.head); if (c) h.quickFix(c.id); return true }, preventDefault: true },
    { key: 'Mod-Enter', run: () => h.accept(), preventDefault: true },
    { key: 'Escape', run: () => h.reject() },
    { key: 'Mod-s', run: () => { h.save(); return true }, preventDefault: true },
  ]
  const state = EditorState.create({
    doc: opts.doc,
    extensions: [
      lineNumbers({ formatNumber: (n) => String(n) }),
      ...pageGutter(opts.pages || []),
      lintGutter(),
      history(),
      drawSelection(),
      highlightActiveLine(),
      highlightSelectionMatches(),
      search({ top: true }),
      EditorView.lineWrapping,
      claimsField,
      flashField,
      activeField,
      zoomSlot.of(zoomTheme(opts.fontSize || 15)),
      keymap.of([...keys, ...searchKeymap, ...historyKeymap, ...defaultKeymap]),
      EditorState.readOnly.of(!!opts.readOnly),
      EditorView.editable.of(!opts.readOnly),
      theme,
      EditorView.updateListener.of((u) => {
        if (u.selectionSet || u.docChanged) {
          const c = claimAt(u.state, u.state.selection.main.head)
          h.select(c ? c.id : null)
        }
        if (u.docChanged) {
          const user = u.transactions.some((tr) => tr.isUserEvent('input') || tr.isUserEvent('delete') || tr.isUserEvent('undo') || tr.isUserEvent('redo'))
          const touched = new Set()
          if (user) {
            for (const tr of u.transactions) {
              tr.changes.iterChangedRanges((fromA, toA) => {
                for (const c of u.startState.field(claimsField)) if (fromA <= c.to && toA >= c.from) touched.add(c.id)
              })
            }
          }
          h.change({ user, touched: [...touched] })
        }
      }),
    ],
  })
  return new EditorView({ state, parent })
}

export function loadClaims(view, claims, handlers) {
  view.dispatch({ effects: setClaims.of(claims) })
  view.dispatch(lintFromClaims(view.state, handlers))
}

export function flash(view, claim) {
  view.dispatch({ effects: flashRange.of(claim ? { from: claim.from, to: claim.to } : null) })
}

export function reveal(view, claim) {
  view.dispatch({
    selection: { anchor: claim.from },
    effects: EditorView.scrollIntoView(claim.from, { y: 'center' }),
  })
  view.focus()
}

/** Where a suggestion lands in the claim as it reads now; null when its target is gone. */
export function suggestionChange(state, claim, s) {
  const text = state.doc.sliceString(claim.from, claim.to)
  if (s.position === 'append') {
    const trimmed = text.replace(/\s+$/, '')
    const cut = /[.;!?]$/.test(trimmed) ? trimmed.length - 1 : trimmed.length
    return { from: claim.from + cut, to: claim.from + cut, insert: s.replacement }
  }
  const at = text.indexOf(s.target)
  if (at < 0) return null
  return { from: claim.from + at, to: claim.from + at + s.target.length, insert: s.replacement }
}

/** Font size of the report, in px (the toolbar's zoom). */
export function setZoom(view, px) {
  view.dispatch({ effects: zoomSlot.reconfigure(zoomTheme(px)) })
}

/** Scroll to the first paragraph of page `page` of the original (or the nearest later one). */
export function gotoPage(view, pages, page) {
  let index = pages.findIndex((p) => p != null && p >= page)
  if (index < 0) index = pages.length - 1
  if (index < 0) return
  const line = view.state.doc.line(Math.min(index + 1, view.state.doc.lines))
  view.dispatch({ selection: { anchor: line.from }, effects: EditorView.scrollIntoView(line.from, { y: 'start', yMargin: 12 }) })
}

/** Page of the original shown at the top of the viewport. */
export function pageAtTop(view, pages) {
  const block = view.lineBlockAtHeight(view.scrollDOM.scrollTop + 8)
  const n = view.state.doc.lineAt(block.from).number
  for (let i = n - 1; i >= 0; i--) if (pages[i] != null) return pages[i]
  return pages.find((p) => p != null) ?? null
}

/** Find `text` (case-insensitive) and select the next / previous match. Returns false when nothing matches. */
export function searchText(view, text, backwards = false) {
  view.dispatch({ effects: setSearchQuery.of(new SearchQuery({ search: text, caseSensitive: false })) })
  if (!text) return true
  return backwards ? findPrevious(view) : findNext(view)
}
