const API_BASE = '/api'

export function formatCurrency(value) {
  const numericValue = Number.isFinite(value) ? value : 0
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 3,
  }).format(numericValue)
}

export function formatRatio(value) {
  return `${Math.max(0, Math.min(100, Math.round(Number(value) || 0)))}%`
}

async function readJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : null

  if (!response.ok) {
    const message = data?.detail || data?.message || `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return data
}

export async function fetchBudgetSnapshot() {
  const data = await readJson('/budget')
  return {
    totalBudget: Number(data.total_budget ?? 2),
    currentSpend: Number(data.current_spend ?? data.total_spend ?? 0),
    remainingBudget: Number(data.remaining_budget ?? 0),
  }
}

export async function submitTravelPrompt(prompt) {
  return readJson('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  })
}

function isSectionHeading(line) {
  return /^(#{1,3}\s*)?(timeline|travel order|route|spend(?:ing)?|estimated spending|summary|places)\b/i.test(line)
}

function sectionKey(line) {
  const normalized = line.replace(/^#{1,3}\s*/, '').toLowerCase()
  if (normalized.startsWith('timeline')) return 'timeline'
  if (normalized.startsWith('travel order') || normalized.startsWith('route')) return 'travelOrder'
  if (normalized.startsWith('spend') || normalized.startsWith('estimated spending')) return 'spending'
  if (normalized.startsWith('places')) return 'places'
  if (normalized.startsWith('summary')) return 'summary'
  return null
}

function cleanBullet(line) {
  return line.replace(/^[-*•\d.)\s]+/, '').trim()
}

function extractTime(line) {
  const timeMatch = line.match(/\b(?:\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm))\b/i)
  if (timeMatch) return timeMatch[0].toUpperCase().replace(/\s+/g, ' ')
  const rangeMatch = line.match(/\b(?:\d{1,2}\s*(?:am|pm))\s*[-–—]\s*(?:\d{1,2}\s*(?:am|pm))\b/i)
  if (rangeMatch) return rangeMatch[0].toUpperCase().replace(/\s+/g, ' ')
  return ''
}

function parseTimelineLine(line) {
  const time = extractTime(line)
  const text = cleanBullet(line)
  if (!time && !text) return null

  const remainder = time ? text.replace(time, '').replace(/^[-:–—\s]+/, '').trim() : text
  const title = remainder.split(' - ')[0].split(':')[0].trim() || remainder || time || 'Stop'

  return {
    time: time || 'Anytime',
    title,
    detail: remainder || text,
  }
}

export function parseItineraryResponse(responseText) {
  const lines = String(responseText || '')
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line.trim())

  const buckets = {
    timeline: [],
    travelOrder: [],
    places: [],
    spending: [],
    summary: [],
  }

  let current = 'summary'

  for (const line of lines) {
    if (!line) continue

    if (isSectionHeading(line)) {
      const key = sectionKey(line)
      if (key) {
        current = key
      }
      continue
    }

    const cleaned = cleanBullet(line)
    if (!cleaned) continue

    if (current === 'timeline') {
      const parsed = parseTimelineLine(cleaned)
      if (parsed) {
        buckets.timeline.push(parsed)
      }
      continue
    }

    if (current === 'travelOrder') {
      buckets.travelOrder.push(cleaned)
      continue
    }

    if (current === 'places') {
      buckets.places.push(cleaned)
      continue
    }

    if (current === 'spending') {
      buckets.spending.push(cleaned)
      continue
    }

    buckets.summary.push(cleaned)
  }

  const responseSummary = buckets.summary.join(' ')
  const title = responseSummary.split('.').find(Boolean)?.trim() || 'Travel plan'

  return {
    title,
    summary: responseSummary || String(responseText || '').trim(),
    timeline: buckets.timeline,
    travelOrder: buckets.travelOrder,
    places: buckets.places,
    spending: buckets.spending,
    rawText: String(responseText || '').trim(),
  }
}