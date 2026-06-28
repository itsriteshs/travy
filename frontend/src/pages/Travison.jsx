import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera, ImagePlus, Sparkles } from 'lucide-react'
import { Button } from '../components/ui/button'
import { computeStructuredResult, submitTravisonImage } from '../lib/travy'

const MAX_IMAGE_DIMENSION = 1280
const MAX_IMAGE_BYTES = 2_600_000

function canvasToJpegBlob(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('Failed to encode image'))
          return
        }
        resolve(blob)
      },
      'image/jpeg',
      quality,
    )
  })
}

async function compressImageForVision(file) {
  if (file.size <= MAX_IMAGE_BYTES) return file

  const objectUrl = URL.createObjectURL(file)
  try {
    const image = await new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('Could not read uploaded image'))
      img.src = objectUrl
    })

    const scale = Math.min(1, MAX_IMAGE_DIMENSION / Math.max(image.width, image.height))
    const targetWidth = Math.max(1, Math.round(image.width * scale))
    const targetHeight = Math.max(1, Math.round(image.height * scale))

    const canvas = document.createElement('canvas')
    canvas.width = targetWidth
    canvas.height = targetHeight

    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('Canvas is not available in this browser')

    ctx.drawImage(image, 0, 0, targetWidth, targetHeight)

    let quality = 0.82
    let blob = await canvasToJpegBlob(canvas, quality)
    while (blob.size > MAX_IMAGE_BYTES && quality > 0.45) {
      quality -= 0.08
      blob = await canvasToJpegBlob(canvas, quality)
    }

    const safeName = (file.name || 'travison-image').replace(/\.[^/.]+$/, '')
    return new File([blob], `${safeName}-optimized.jpg`, { type: 'image/jpeg' })
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}

export function Travison() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [additionalContext, setAdditionalContext] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [visionSummary, setVisionSummary] = useState(null)

  const previewUrl = useMemo(() => {
    if (!selectedFile) return ''
    return URL.createObjectURL(selectedFile)
  }, [selectedFile])

  async function onSubmit(e) {
    e.preventDefault()
    if (!selectedFile) {
      setError('Please upload or capture an image first.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const optimizedFile = await compressImageForVision(selectedFile)
      const response = await submitTravisonImage(optimizedFile, additionalContext)
      setVisionSummary(response.vision)

      const structured = computeStructuredResult(response.result, response.prompt_used)
      sessionStorage.setItem(
        'travy_result',
        JSON.stringify({ result: response.result, prompt: response.prompt_used, structured }),
      )
      navigate('/results')
    } catch (err) {
      setError(err.message || 'Failed to process image for Travison.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-4 inline-flex items-center gap-2 border-[2px] border-black bg-[var(--yellow)] px-3 py-1 text-[11px] font-black uppercase tracking-[0.18em]">
        <Sparkles size={14} />
        Travison
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr] lg:items-start">
        <section className="border-[3px] border-black bg-white p-5 shadow-[6px_6px_0_#000]">
          <h1 className="text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">
            Upload surroundings,
            <br />
            get similar trips.
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--muted-foreground)]">
            Travison detects landmarks and scene clues from your photo, then asks the AI planner to
            build a similar-style itinerary.
          </p>
          <p className="mt-1 max-w-2xl text-[11px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]">
            Large photos are auto-compressed before upload.
          </p>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <label className="block border-[2px] border-dashed border-black bg-[var(--muted)] p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-black uppercase tracking-widest">
                <ImagePlus size={16} />
                Upload or capture image
              </div>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={(e) => {
                  const file = e.target.files?.[0] || null
                  setSelectedFile(file)
                  setVisionSummary(null)
                }}
                className="block w-full text-sm"
              />
            </label>

            {previewUrl && (
              <div className="overflow-hidden border-[3px] border-black">
                <img
                  src={previewUrl}
                  alt="Travison upload preview"
                  className="h-72 w-full object-cover"
                />
              </div>
            )}

            <div>
              <label className="mb-1 block text-[11px] font-black uppercase tracking-widest">
                Optional context
              </label>
              <textarea
                value={additionalContext}
                onChange={(e) => setAdditionalContext(e.target.value)}
                rows={3}
                placeholder="Budget, preferred city, number of people, time window..."
                className="w-full border-[2px] border-black bg-[var(--muted)] px-3 py-2 text-sm"
              />
            </div>

            <Button type="submit" disabled={loading} className="brutal-press gap-2">
              <Camera size={15} />
              {loading ? 'Analyzing image...' : 'Generate similar trip'}
            </Button>

            {error && (
              <div className="border-[2px] border-red-600 bg-red-50 px-3 py-2 text-sm font-bold text-red-800">
                {error}
              </div>
            )}
          </form>
        </section>

        <aside className="space-y-4">
          <div className="border-[3px] border-black bg-[var(--primary)] p-5 shadow-[5px_5px_0_#000]">
            <div className="text-[10px] font-black uppercase tracking-widest text-black/60">
              Travison flow
            </div>
            <ol className="mt-2 space-y-2 text-sm font-semibold text-black/90">
              <li>1. User uploads or captures a photo.</li>
              <li>2. Vision API detects landmark and visual context.</li>
              <li>3. Otari planner suggests similar-style places.</li>
            </ol>
          </div>

          {visionSummary && (
            <div className="border-[3px] border-black bg-white p-4 shadow-[5px_5px_0_#000]">
              <div className="text-[10px] font-black uppercase tracking-widest text-[var(--muted-foreground)]">
                Vision summary
              </div>
              <div className="mt-2 text-lg font-black">{visionSummary.primary_subject}</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {(visionSummary.landmarks || []).slice(0, 5).map((landmark) => (
                  <span
                    key={landmark}
                    className="border-[2px] border-black bg-[var(--yellow)] px-2 py-1 text-[10px] font-black uppercase tracking-widest"
                  >
                    {landmark}
                  </span>
                ))}
                {(visionSummary.labels || []).slice(0, 5).map((label) => (
                  <span
                    key={label}
                    className="border-[2px] border-black bg-[var(--muted)] px-2 py-1 text-[10px] font-black uppercase tracking-widest"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </main>
  )
}
