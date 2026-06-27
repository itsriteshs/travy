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

// ─── Structured result computation for Results page ─────────────────────────

function parseCostNumber(costStr) {
  if (!costStr) return 0
  const m = String(costStr).match(/[\d,]+/)
  if (!m) return 0
  return Number(m[0].replace(/,/g, '')) || 0
}

function parsePromptContext(prompt) {
  const text = String(prompt || '')

  // Group size
  const groupM = text.match(/(\d+)\s*(?:friends?|people|persons?|travelers?|pax)/i)
  const groupSize = groupM ? Math.max(1, Math.min(20, parseInt(groupM[1]))) : 1

  // Budget per person
  const budgetM = text.match(/([₹$€£])(\d[\d,]*)(?:\s*each|\s*\/person|\s*per\s*person)?/i)
  const budgetPerPerson = budgetM ? Number(budgetM[2].replace(/,/g, '')) : 0
  const currencySymbol = budgetM ? budgetM[1] : '₹'

  // Time range
  const timeM = text.match(/(\d{1,2}\s*(?:AM|PM))\s*(?:to|-)\s*(\d{1,2}\s*(?:AM|PM))/i)
  const timeRange = timeM ? `${timeM[1].toUpperCase()} - ${timeM[2].toUpperCase()}` : ''

  // Activities
  const activityWords = ['shopping', 'food', 'photos', 'sightseeing', 'museums', 'hiking', 'beach', 'nightlife', 'cafe', 'history', 'nature', 'market']
  const activities = activityWords.filter((w) => text.toLowerCase().includes(w))

  // Energy
  const isLowEnergy = /not too tiring|relaxed|easy|slow|low energy/i.test(text)
  const isHighEnergy = /packed|energetic|active|intense/i.test(text)
  const energyLabel = isLowEnergy ? 'MEDIUM-LOW ENERGY' : isHighEnergy ? 'HIGH ENERGY' : 'MEDIUM ENERGY'

  return { groupSize, budgetPerPerson, currencySymbol, timeRange, activities, energyLabel }
}

function extractStopsFromResponse(responseText) {
  const text = String(responseText || '')
  const stops = []

  // Try structured STOP blocks (from updated Otari prompt)
  const structuredRe = /STOP\s+(\d+)\s*\nNAME:\s*([^\n]+)\nTIME:\s*([^\n]+)\nCOST:\s*([^\n]+)\nINFO:\s*([^\n]+)/gm
  let m
  while ((m = structuredRe.exec(text)) !== null) {
    stops.push({
      index: parseInt(m[1]),
      name: m[2].trim(),
      time_range: m[3].trim(),
      cost_per_person: m[4].trim(),
      description: m[5].trim(),
    })
  }
  if (stops.length > 0) return stops

  // Fallback: numbered list parsing  "1. Place Name" patterns
  const lines = text.split('\n')
  let currentStop = null
  let idx = 0

  for (const raw of lines) {
    const line = raw.trim()
    if (!line) continue

    // Numbered heading: "1. Place", "## 2. Place", "**3. Place**"
    const numM = line.match(/^(?:#{1,3}\s*)?(\d{1,2})[.)]\s+([^*#\n]+)/)
    if (numM && parseInt(numM[1]) <= 15) {
      if (currentStop) stops.push(currentStop)
      idx++
      currentStop = {
        index: idx,
        name: numM[2].replace(/\*+/g, '').trim(),
        time_range: '',
        cost_per_person: '',
        description: '',
      }
      continue
    }

    if (currentStop) {
      // Time
      if (!currentStop.time_range) {
        const tM = line.match(/\d{1,2}:\d{2}\s*(?:AM|PM)?\s*[-–]\s*\d{1,2}:\d{2}\s*(?:AM|PM)?/i)
          || line.match(/\d{1,2}\s*(?:AM|PM)\s*[-–]\s*\d{1,2}\s*(?:AM|PM)/i)
        if (tM) { currentStop.time_range = tM[0].toUpperCase(); continue }
      }
      // Cost
      if (!currentStop.cost_per_person) {
        const cM = line.match(/[₹$€£]\d[\d,]*(?:\s*\/\s*person)?/i)
        if (cM) { currentStop.cost_per_person = cM[0]; continue }
      }
      // Description (first bullet or sentence)
      if (!currentStop.description) {
        const desc = line.replace(/^[-*•]\s*/, '').trim()
        if (desc && !desc.match(/^#+/)) currentStop.description = desc
      }
    }
  }
  if (currentStop) stops.push(currentStop)

  // Last resort: extract from timeline buckets
  if (stops.length === 0) {
    const parsed = parseItineraryResponse(responseText)
    for (const [i, t] of parsed.timeline.entries()) {
      stops.push({
        index: i + 1,
        name: t.title || `Stop ${i + 1}`,
        time_range: t.time || '',
        cost_per_person: '',
        description: t.detail || '',
      })
    }
  }

  return stops
}

function extractPlanTitle(responseText, prompt) {
  const text = String(responseText || '')

  // Structured format
  const titleM = text.match(/^TITLE:\s*(.+)$/m)
  if (titleM) return titleM[1].trim()

  // First H1/H2 heading
  const headingM = text.match(/^#{1,2}\s+(.+)$/m)
  if (headingM) return headingM[1].replace(/[*#]/g, '').trim()

  // Derive from prompt city
  const cityM = String(prompt || '').match(/\bin\s+([A-Za-z\s]+?)(?:\s+for|\s+from|\s*$)/i)
  const city = cityM ? cityM[1].trim() : 'Your City'
  return `${city} Plan`
}

function extractPlanDescription(responseText) {
  const text = String(responseText || '')
  const descM = text.match(/^DESC:\s*(.+)$/m)
  if (descM) return descM[1].trim()
  // First non-heading sentence
  const sentences = text.replace(/^#{1,3}[^\n]*/gm, '').split(/\n/).map(l => l.trim()).filter(Boolean)
  const first = sentences.find(s => s.length > 20 && !s.startsWith('STOP') && !s.startsWith('TITLE'))
  return first ? first.replace(/^[-*•]\s*/, '') : ''
}

function computeStopFits(stop, index, totalStops, budgetPerPerson, complexity, groupSize) {
  const cost = parseCostNumber(stop.cost_per_person)

  // Budget fit: how affordable this stop is relative to per-stop budget
  const perStopBudget = budgetPerPerson > 0 ? budgetPerPerson / Math.max(totalStops, 1) : 200
  const budgetFit = perStopBudget > 0
    ? Math.max(10, Math.min(100, Math.round(100 - (cost / perStopBudget) * 25)))
    : complexity

  // Mood fit: derived from complexity score (how well model understood the request)
  const moodFit = Math.max(20, Math.min(100, complexity))

  // Group fit: inverse of group size (larger groups harder to accommodate)
  const groupFit = Math.max(5, Math.min(100, Math.round(100 / (groupSize * 2)) + 1))

  // Distance fit: sinusoidal based on position (peaks in middle of route)
  const progress = totalStops > 1 ? index / (totalStops - 1) : 0.5
  const distanceFit = Math.round(30 + 30 * Math.sin(progress * Math.PI))

  // Fatigue increases across the day
  const fatigue = index < totalStops / 2 ? 'LOW' : index < totalStops * 0.8 ? 'MEDIUM' : 'HIGH'

  const fitScore = Math.round((budgetFit * 0.35 + moodFit * 0.3 + distanceFit * 0.2 + groupFit * 0.15))

  return { ...stop, budget_fit: budgetFit, mood_fit: moodFit, group_fit: groupFit, distance_fit: distanceFit, fatigue, fit_score: fitScore }
}

function computePlanFit(stops) {
  if (!stops.length) return { score: 50 }
  const avg = (arr) => Math.round(arr.reduce((a, b) => a + b, 0) / arr.length)
  const budgetFit = avg(stops.map(s => s.budget_fit))
  const moodFit = avg(stops.map(s => s.mood_fit))
  const distanceFit = avg(stops.map(s => s.distance_fit))
  const groupFit = avg(stops.map(s => s.group_fit))
  const timeFit = Math.min(100, stops.length * 18)
  const fatiguePenalty = Math.max(0, (stops.length - 3) * 4)
  const score = Math.min(100, Math.max(10, Math.round(
    budgetFit * 0.3 + moodFit * 0.25 + distanceFit * 0.2 + groupFit * 0.1 + timeFit * 0.15 - fatiguePenalty
  )))
  return { score, budget_fit: budgetFit, mood_fit: moodFit, distance_fit: distanceFit, group_fit: groupFit, time_fit: timeFit, fatigue_penalty: fatiguePenalty }
}

function buildTripTags(prompt, groupSize, budgetPerPerson, currencySymbol, timeRange, activities, energyLabel) {
  const tags = []
  if (groupSize > 1) tags.push(`${groupSize} TRAVELER(S)`)
  if (budgetPerPerson > 0) tags.push(`${currencySymbol}${budgetPerPerson}/PERSON`)
  if (timeRange) tags.push(timeRange)
  if (activities.length > 0) tags.push(activities.slice(0, 3).map(a => a.toUpperCase()).join(' + '))
  tags.push(energyLabel)
  return tags
}

function buildStatusBadges(apiResult) {
  const badges = []
  const sec = apiResult?.transparency?.security_status || ''
  if (sec.toLowerCase().includes('safe') || sec.toLowerCase().includes('clean')) {
    badges.push('VALIDATION PASSED')
  }
  if (apiResult?.transparency?.intent?.toLowerCase().includes('group') || (apiResult._groupSize > 1)) {
    badges.push('GROUP-AWARE UI')
  }
  if (apiResult?.transparency?.selected_model) {
    badges.push('GUARDIAN ROUTE AVAILABLE')
  }
  return badges
}

export function computeStructuredResult(apiResult, originalPrompt) {
  const { groupSize, budgetPerPerson, currencySymbol, timeRange, activities, energyLabel } =
    parsePromptContext(originalPrompt)

  const rawResponse = apiResult?.response || ''
  const complexity = apiResult?.transparency?.complexity_score ?? 50

  // Extract stops from Otari response
  const rawStops = extractStopsFromResponse(rawResponse)

  // Compute fit scores for each stop
  const stops = rawStops.map((stop, i) =>
    computeStopFits(stop, i, rawStops.length, budgetPerPerson, complexity, groupSize),
  )

  // Plan-level fit
  const planFit = computePlanFit(stops)

  // Budget breakdown
  const totalCost = stops.reduce((sum, s) => sum + parseCostNumber(s.cost_per_person), 0)
  const estimatedTotal = totalCost > 0 ? totalCost : budgetPerPerson > 0 ? budgetPerPerson * 0.88 : 0
  const budgetBreakdown = {
    budgetPerPerson,
    estimatedTotal,
    currencySymbol,
    status: estimatedTotal <= budgetPerPerson || budgetPerPerson === 0 ? 'within_budget' : 'over_budget',
  }

  // Plan title/description
  const plan = {
    title: extractPlanTitle(rawResponse, originalPrompt),
    description: extractPlanDescription(rawResponse),
  }

  // Trip tags
  const tripTags = buildTripTags(originalPrompt, groupSize, budgetPerPerson, currencySymbol, timeRange, activities, energyLabel)

  // Status badges from transparency
  const statusBadges = buildStatusBadges({ ...apiResult, _groupSize: groupSize })

  return {
    plan,
    stops,
    planFit,
    budgetBreakdown,
    transparency: apiResult?.transparency ?? {},
    budget: apiResult?.budget ?? {},
    tripTags,
    statusBadges,
    rawResponse,
  }
}