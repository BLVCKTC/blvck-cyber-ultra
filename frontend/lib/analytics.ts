// Lightweight client-side analytics tracker.
// Events are persisted to localStorage and mirrored to window.dataLayer
// so any downstream tag manager (GTM, Segment, PostHog) can consume them.

export type AnalyticsEvent = {
  name: string
  props?: Record<string, string | number | boolean | undefined>
  ts: number
  path: string
}

const STORAGE_KEY = "blvck.analytics.events"
const MAX_EVENTS = 500

export function track(name: string, props?: AnalyticsEvent["props"]) {
  if (typeof window === "undefined") return
  const event: AnalyticsEvent = {
    name,
    props,
    ts: Date.now(),
    path: window.location.pathname + window.location.search,
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    const list: AnalyticsEvent[] = raw ? JSON.parse(raw) : []
    list.push(event)
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(-MAX_EVENTS)))
  } catch {
    // ignore quota / privacy-mode errors
  }
  // Mirror to dataLayer for GTM / downstream analytics
  const w = window as unknown as { dataLayer?: unknown[] }
  w.dataLayer = w.dataLayer || []
  w.dataLayer.push({ event: name, ...props })
  if (process.env.NODE_ENV === "development") {
    // eslint-disable-next-line no-console
    console.debug("[analytics]", name, props)
  }
}

export function getEvents(): AnalyticsEvent[] {
  if (typeof window === "undefined") return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function clearEvents() {
  if (typeof window === "undefined") return
  window.localStorage.removeItem(STORAGE_KEY)
}