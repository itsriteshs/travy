import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Upload } from 'lucide-react'

export function AudioRecorder({ onTranscribed, recordLabel = 'Record', showUpload = true }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [frequencies, setFrequencies] = useState([])
  const [error, setError] = useState('')
  
  const mediaRecorderRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)
  const fileInputRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationRef = useRef(null)

  // Visualize frequency data
  useEffect(() => {
    if (!isRecording) return

    const updateFrequencies = () => {
      if (analyserRef.current) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
        analyserRef.current.getByteFrequencyData(dataArray)
        
        // Sample every 4th bar for smoother visualization (reduce from ~1024 to ~256 bars)
        const sampled = Array.from(dataArray).filter((_, i) => i % 4 === 0)
        setFrequencies(sampled)
      }
      animationRef.current = requestAnimationFrame(updateFrequencies)
    }

    animationRef.current = requestAnimationFrame(updateFrequencies)
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [isRecording])

  function startRecording() {
    setError('')
    chunksRef.current = []
    setRecordingTime(0)
    setFrequencies([])

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        streamRef.current = stream
        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunksRef.current.push(e.data)
        }

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
      console.log('Recording stopped. Blob size:', blob.size)
      await transcribeAudio(blob)
      stream.getTracks().forEach((track) => track.stop())
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
    }

        // Set up Web Audio API for visualization
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        audioContextRef.current = audioContext
        const analyser = audioContext.createAnalyser()
        analyserRef.current = analyser
        analyser.fftSize = 1024
        const source = audioContext.createMediaStreamSource(stream)
        source.connect(analyser)

        mediaRecorder.start()
        setIsRecording(true)

        timerRef.current = setInterval(() => {
          setRecordingTime((t) => t + 1)
        }, 1000)
      })
      .catch((err) => {
        const msg = err.name === 'NotAllowedError' 
          ? 'Microphone access denied' 
          : `Microphone error: ${err.message}`
        setError(msg)
        console.error(msg, err)
      })
  }

  function stopRecording() {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      clearInterval(timerRef.current)
      setFrequencies([])
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }

  async function transcribeAudio(audioBlob) {
    setIsTranscribing(true)
    setError('')
    try {
      // First, convert blob to audio data and resample to 16000 Hz
      const arrayBuffer = await audioBlob.arrayBuffer()
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      
      console.log('Original audio sample rate from context:', audioContext.sampleRate)
      
      // Decode the WAV file
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      console.log('Decoded audio buffer - channels:', audioBuffer.numberOfChannels, 'duration:', audioBuffer.duration, 'sample rate:', audioBuffer.sampleRate)
      
      // Resample to 16000 Hz if needed
      const targetSampleRate = 16000
      let resampledBuffer = audioBuffer
      
      if (audioBuffer.sampleRate !== targetSampleRate) {
        console.log(`Resampling from ${audioBuffer.sampleRate} Hz to ${targetSampleRate} Hz`)
        
        // Create offline context for resampling
        const offlineContext = new OfflineAudioContext(
          audioBuffer.numberOfChannels,
          Math.ceil(audioBuffer.duration * targetSampleRate),
          targetSampleRate
        )
        
        const source = offlineContext.createBufferSource()
        source.buffer = audioBuffer
        source.connect(offlineContext.destination)
        source.start()
        
        resampledBuffer = await offlineContext.startRendering()
        console.log('Resampled buffer created - sample rate:', resampledBuffer.sampleRate)
      }
      
      // Convert to PCM16 (linear16)
      const pcmData = new Int16Array(resampledBuffer.length)
      const channelData = resampledBuffer.getChannelData(0)
      for (let i = 0; i < channelData.length; i++) {
        const value = Math.max(-1, Math.min(1, channelData[i]))
        pcmData[i] = value < 0 ? value * 0x8000 : value * 0x7FFF
      }
      
      console.log('PCM data created - length:', pcmData.length, 'bytes:', pcmData.buffer.byteLength)
      
      // Convert to base64 in chunks to avoid stack overflow
      const uint8Array = new Uint8Array(pcmData.buffer)
      let binary = ''
      const chunkSize = 8192
      for (let i = 0; i < uint8Array.length; i += chunkSize) {
        const chunk = uint8Array.slice(i, i + chunkSize)
        binary += String.fromCharCode.apply(null, chunk)
      }
      const base64 = btoa(binary)
      
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_base64: base64 }),
      })

      const result = await response.json()
      console.log('Transcription result:', result)
      console.log('Result status:', result.status, 'Text:', result.text, 'Length:', result.text?.length)
      if (result.status === 'success' && result.text && result.text.trim()) {
        console.log('Calling onTranscribed with:', result.text)
        onTranscribed(result.text)
        setError('')
      } else if (result.status === 'success' && !result.text) {
        setError('Transcription returned empty text. Try speaking more clearly.')
        console.warn('Empty transcription received')
      } else if (result.error) {
        setError(`Transcription error: ${result.error}`)
        console.error('Transcription error:', result.error)
      } else {
        setError('Unexpected transcription response')
        console.error('Unexpected response:', result)
      }
      setIsTranscribing(false)
      audioContext.close()
    } catch (err) {
      setError(`Failed to transcribe: ${err.message}`)
      console.error('Failed to transcribe:', err)
      setIsTranscribing(false)
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return

    setIsTranscribing(true)
    setError('')
    try {
      // Convert file to audio data and resample to 16000 Hz
      const arrayBuffer = await file.arrayBuffer()
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      
      console.log('File upload - audio context sample rate:', audioContext.sampleRate)
      
      // Decode the audio file
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      console.log('Decoded file - channels:', audioBuffer.numberOfChannels, 'duration:', audioBuffer.duration, 'sample rate:', audioBuffer.sampleRate)
      
      // Resample to 16000 Hz if needed
      const targetSampleRate = 16000
      let resampledBuffer = audioBuffer
      
      if (audioBuffer.sampleRate !== targetSampleRate) {
        console.log(`File resampling from ${audioBuffer.sampleRate} Hz to ${targetSampleRate} Hz`)
        
        const offlineContext = new OfflineAudioContext(
          audioBuffer.numberOfChannels,
          Math.ceil(audioBuffer.duration * targetSampleRate),
          targetSampleRate
        )
        
        const source = offlineContext.createBufferSource()
        source.buffer = audioBuffer
        source.connect(offlineContext.destination)
        source.start()
        
        resampledBuffer = await offlineContext.startRendering()
        console.log('File resampled - sample rate:', resampledBuffer.sampleRate)
      }
      
      // Convert to PCM16
      const pcmData = new Int16Array(resampledBuffer.length)
      const channelData = resampledBuffer.getChannelData(0)
      for (let i = 0; i < channelData.length; i++) {
        const value = Math.max(-1, Math.min(1, channelData[i]))
        pcmData[i] = value < 0 ? value * 0x8000 : value * 0x7FFF
      }
      
      console.log('File PCM data created - length:', pcmData.length, 'bytes:', pcmData.buffer.byteLength)
      
      // Convert to base64 in chunks to avoid stack overflow
      const uint8Array = new Uint8Array(pcmData.buffer)
      let binary = ''
      const chunkSize = 8192
      for (let i = 0; i < uint8Array.length; i += chunkSize) {
        const chunk = uint8Array.slice(i, i + chunkSize)
        binary += String.fromCharCode.apply(null, chunk)
      }
      const base64 = btoa(binary)
      
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_base64: base64 }),
      })

      const result = await response.json()
      console.log('File transcription result:', result)
      if (result.status === 'success' && result.text && result.text.trim()) {
        console.log('Calling onTranscribed with:', result.text)
        onTranscribed(result.text)
        setError('')
      } else if (result.status === 'success' && !result.text) {
        setError('Transcription returned empty text. Try a different audio file.')
        console.warn('Empty transcription received')
      } else if (result.error) {
        setError(`Transcription error: ${result.error}`)
        console.error('Transcription error:', result.error)
      } else {
        setError('Unexpected transcription response')
        console.error('Unexpected response:', result)
      }
      setIsTranscribing(false)
      audioContext.close()
    } catch (err) {
      setError(`Failed to transcribe: ${err.message}`)
      console.error('Failed to transcribe:', err)
      setIsTranscribing(false)
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-end gap-2">
        {isRecording ? (
          <>
            <div className="flex items-center gap-2 border-[2px] border-red-600 bg-red-50 px-3 py-1.5">
              <div className="h-2 w-2 bg-red-600 rounded-full animate-pulse" />
              <span className="text-sm font-bold text-red-700">{recordingTime}s</span>
            </div>

            {/* Frequency visualization */}
            <div className="flex items-end gap-1 h-12">
              {frequencies.slice(0, 16).map((freq, i) => (
                <div
                  key={i}
                  className="w-1 bg-gradient-to-t from-red-600 to-red-400 transition-all duration-75"
                  style={{
                    height: `${Math.max(4, (freq / 255) * 48)}px`,
                  }}
                />
              ))}
            </div>

            <button
              type="button"
              onClick={stopRecording}
              className="brutal-press border-[3px] border-red-700 bg-red-600 px-3 py-1.5 text-[11px] font-bold text-white hover:bg-red-700 shadow-[3px_3px_0_rgba(0,0,0,0.1)]"
            >
              <Square size={14} className="mr-1 inline-block" />
              Stop
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={startRecording}
              disabled={isTranscribing}
              className="brutal-press border-[3px] border-black bg-[var(--primary)] px-3 py-1.5 text-[11px] font-bold text-black hover:bg-blue-400 disabled:opacity-50 shadow-[3px_3px_0_rgba(0,0,0,0.1)]"
            >
              <Mic size={14} className="mr-1 inline-block" />
              {recordLabel}
            </button>
            {showUpload && (
              <>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isTranscribing}
                  className="brutal-press border-[3px] border-black bg-[var(--yellow)] px-3 py-1.5 text-[11px] font-bold text-black hover:bg-yellow-200 disabled:opacity-50 shadow-[3px_3px_0_rgba(0,0,0,0.1)]"
                >
                  <Upload size={14} className="mr-1 inline-block" />
                  Upload
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </>
            )}
          </>
        )}
        {isTranscribing && (
          <span className="text-xs font-bold text-[var(--muted-foreground)]">
            Transcribing…
          </span>
        )}
      </div>
      {error && (
        <div className="border-[2px] border-red-500 bg-red-50 px-3 py-2 text-xs font-bold text-red-700">
          {error}
        </div>
      )}
    </div>
  )
}
