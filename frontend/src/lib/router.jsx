import { useEffect, useState } from 'react'

/**
 * Hash routing, deliberately tiny.
 *
 * The app is a single page served next to the API; a hash keeps deep links to
 * a claim working without server-side routing, and a saved run reopens from
 * `#/runs/<id>/claims/<claim>` after a reload because the id is in the URL.
 */

function parse() {
  const raw = window.location.hash.replace(/^#\/?/, '')
  const [pathPart, query = ''] = raw.split('?')
  const segments = pathPart.split('/').filter(Boolean).map(decodeURIComponent)
  return { segments, query: new URLSearchParams(query), path: `/${segments.join('/')}` }
}

export function navigate(path, { replace = false } = {}) {
  const next = `#${path.startsWith('/') ? path : `/${path}`}`
  if (replace) window.location.replace(next)
  else window.location.hash = next
}

export function useHashRoute() {
  const [route, setRoute] = useState(parse)
  useEffect(() => {
    const onChange = () => setRoute(parse())
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return route
}

export function Link({ to, className = '', children, ...rest }) {
  return (
    <a href={`#${to.startsWith('/') ? to : `/${to}`}`} className={className} {...rest}>
      {children}
    </a>
  )
}
