import { useEffect, useRef, useState } from 'react'
import { FilesetResolver, HandLandmarker } from '@mediapipe/tasks-vision'
import type { NormalizedLandmark } from '@mediapipe/tasks-vision'
import { predictFrame } from '../../services/inferenceApi'
import type { Prediction } from '../../services/inferenceApi'
import { GeneratedOutput } from '../GeneratedOutput/GeneratedOutput'
import { RecognitionPanel } from '../RecognitionPanel/RecognitionPanel'
import '../shared/PanelStyles.css'
import './CameraRecognition.css'

const SAMPLE_INTERVAL_MS = 900
const CONFIRMATION_WINDOW = 3
const REQUIRED_AGREEMENT = 2
const HAND_DETECTION_INTERVAL_MS = 50

type NormalizedBounds = { left: number; top: number; right: number; bottom: number }

function boundsForHands(hands: NormalizedLandmark[][]): NormalizedBounds | null {
  const points = hands.flat()
  if (!points.length) return null
  return {
    left: Math.max(0, Math.min(...points.map((point) => point.x))),
    top: Math.max(0, Math.min(...points.map((point) => point.y))),
    right: Math.min(1, Math.max(...points.map((point) => point.x))),
    bottom: Math.min(1, Math.max(...points.map((point) => point.y))),
  }
}

function frameFromVideo(video: HTMLVideoElement): Promise<Blob> {
  const canvas = document.createElement('canvas')
  const cropSide = Math.min(video.videoWidth, video.videoHeight)
  canvas.width = cropSide
  canvas.height = cropSide
  const context = canvas.getContext('2d')
  if (!canvas.width || !canvas.height || !context) return Promise.reject(new Error('The camera is still starting.'))
  // The classifier was trained on square upper-body images. Use the same
  // centered square view rather than moving/zooming the signer into a
  // hand-only crop the model has never seen during training.
  const cropX = (video.videoWidth - cropSide) / 2
  const cropY = (video.videoHeight - cropSide) / 2
  context.drawImage(video, cropX, cropY, cropSide, cropSide, 0, 0, cropSide, cropSide)
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('Unable to prepare this camera frame.'))
    }, 'image/jpeg', 0.85)
  })
}

export function CameraRecognition() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const timerRef = useRef<number | null>(null)
  const requestRef = useRef<AbortController | null>(null)
  const requestInFlight = useRef(false)
  const predictionWindow = useRef<Prediction[]>([])
  const lastRecordedLabel = useRef<string | null>(null)
  const overlayRef = useRef<HTMLCanvasElement>(null)
  const handLandmarker = useRef<HandLandmarker | null>(null)
  const handBounds = useRef<NormalizedBounds | null>(null)
  const handDetectionFrame = useRef<number | null>(null)
  const startRecognitionLoopRef = useRef<() => void>(() => undefined)
  const lastDetectionTime = useRef(0)
  const lastVideoTime = useRef(-1)
  const [handModelReady, setHandModelReady] = useState(false)
  const [handDetectionError, setHandDetectionError] = useState('')
  const [handsVisible, setHandsVisible] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [cameraError, setCameraError] = useState('')
  const [apiError, setApiError] = useState('')
  const [isRecognizing, setIsRecognizing] = useState(false)
  const [isConfirming, setIsConfirming] = useState(false)
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [signHistory, setSignHistory] = useState<string[]>([])

  useEffect(() => {
    if (stream && videoRef.current) videoRef.current.srcObject = stream
  }, [stream])

  useEffect(() => {
    let cancelled = false
    let landmarker: HandLandmarker | null = null
    async function initializeHandDetection() {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.3/wasm',
        )
        const options = {
          baseOptions: { modelAssetPath: '/hand_landmarker.task', delegate: 'GPU' as const },
          runningMode: 'VIDEO' as const,
          numHands: 2,
          minHandDetectionConfidence: 0.55,
          minHandPresenceConfidence: 0.55,
          minTrackingConfidence: 0.55,
        }
        // Keep hand landmark inference on the GPU; do not silently move this
        // workload to the CPU when browser GPU support is unavailable.
        landmarker = await HandLandmarker.createFromOptions(vision, options)
        if (cancelled) landmarker.close()
        else {
          handLandmarker.current = landmarker
          setHandModelReady(true)
          setHandDetectionError('')
        }
      } catch {
        if (!cancelled) setHandDetectionError('GPU hand detection could not start. Check that browser hardware acceleration is enabled, then reload the page.')
      }
    }
    void initializeHandDetection()
    return () => {
      cancelled = true
      const currentLandmarker = handLandmarker.current
      handLandmarker.current = null
      currentLandmarker?.close()
      if (landmarker && landmarker !== currentLandmarker) landmarker.close()
    }
  }, [])

  function drawHandOverlay(hands: NormalizedLandmark[][], width: number, height: number) {
    const canvas = overlayRef.current
    if (!canvas) return
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }
    const context = canvas.getContext('2d')
    if (!context) return
    context.clearRect(0, 0, width, height)
    context.lineWidth = Math.max(2, width / 480)
    context.strokeStyle = '#6ee7ff'
    context.fillStyle = '#17b7db'
    context.shadowColor = '#062b38'
    context.shadowBlur = 3
    for (const hand of hands) {
      for (const connection of HandLandmarker.HAND_CONNECTIONS) {
        const first = hand[connection.start]
        const second = hand[connection.end]
        if (!first || !second) continue
        context.beginPath()
        context.moveTo(first.x * width, first.y * height)
        context.lineTo(second.x * width, second.y * height)
        context.stroke()
      }
      for (const point of hand) {
        context.beginPath()
        context.arc(point.x * width, point.y * height, Math.max(2.5, width / 180), 0, Math.PI * 2)
        context.fill()
      }
      const minX = Math.min(...hand.map((point) => point.x)) * width
      const minY = Math.min(...hand.map((point) => point.y)) * height
      const maxX = Math.max(...hand.map((point) => point.x)) * width
      const maxY = Math.max(...hand.map((point) => point.y)) * height
      context.strokeStyle = '#28d6ff'
      context.lineWidth = Math.max(3, width / 360)
      context.strokeRect(minX, minY, maxX - minX, maxY - minY)
      context.strokeStyle = '#6ee7ff'
      context.lineWidth = Math.max(2, width / 480)
    }
    context.shadowBlur = 0
    if (hands.length) {
      context.font = `600 ${Math.max(14, width / 45)}px Arial`
      const label = 'HAND FOCUSED'
      const labelWidth = context.measureText(label).width + 18
      const labelHeight = Math.max(25, width / 28)
      context.fillStyle = '#13add0'
      context.fillRect(12, 12, labelWidth, labelHeight)
      context.fillStyle = '#ffffff'
      context.fillText(label, 21, 12 + labelHeight * 0.7)
    }
  }

  function startHandDetectionLoop() {
    if (handDetectionFrame.current !== null) return
    const detect = (now: number) => {
      const video = videoRef.current
      const detector = handLandmarker.current
      if (video && detector && video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA
        && video.currentTime !== lastVideoTime.current
        && now - lastDetectionTime.current >= HAND_DETECTION_INTERVAL_MS) {
        lastVideoTime.current = video.currentTime
        lastDetectionTime.current = now
        try {
          const result = detector.detectForVideo(video, now)
          handBounds.current = boundsForHands(result.landmarks)
          const visible = result.landmarks.length > 0
          setHandsVisible((previous) => previous === visible ? previous : visible)
          drawHandOverlay(result.landmarks, video.videoWidth, video.videoHeight)
        } catch {
          handBounds.current = null
          setHandsVisible(false)
          drawHandOverlay([], video.videoWidth, video.videoHeight)
        }
      }
      handDetectionFrame.current = window.requestAnimationFrame(detect)
    }
    handDetectionFrame.current = window.requestAnimationFrame(detect)
  }

  function stopRecognitionLoop() {
    if (timerRef.current !== null) window.clearInterval(timerRef.current)
    timerRef.current = null
    requestRef.current?.abort()
    requestRef.current = null
    requestInFlight.current = false
    setIsRecognizing(false)
  }

  function stopCamera() {
    stopRecognitionLoop()
    stream?.getTracks().forEach((track) => track.stop())
    setStream(null)
    setPrediction(null)
    predictionWindow.current = []
    lastRecordedLabel.current = null
    setSignHistory([])
    setIsConfirming(false)
    setApiError('')
  }

  async function recognizeFrame() {
    const video = videoRef.current
    if (!video || requestInFlight.current || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return
    requestInFlight.current = true
    const controller = new AbortController()
    requestRef.current = controller
    setIsRecognizing(true)
    try {
      const bounds = handBounds.current
      if (!bounds) {
        predictionWindow.current = []
        setPrediction(null)
        setIsConfirming(false)
        return
      }
      const frame = await frameFromVideo(video)
      const nextPrediction = await predictFrame(frame, controller.signal)
      if (!controller.signal.aborted) {
        if (nextPrediction.low_confidence) {
          predictionWindow.current = []
          setIsConfirming(true)
          setPrediction(null)
          setApiError('')
          return
        }

        predictionWindow.current = [
          ...predictionWindow.current,
          nextPrediction,
        ].slice(-CONFIRMATION_WINDOW)
        const votes = new Map<string, number>()
        for (const item of predictionWindow.current) {
          votes.set(item.label, (votes.get(item.label) ?? 0) + 1)
        }
        const confirmedLabel = [...votes.entries()].find(
          ([, count]) => count >= REQUIRED_AGREEMENT,
        )?.[0]
        if (confirmedLabel) {
          const matchingPredictions = predictionWindow.current.filter(
            (item) => item.label === confirmedLabel,
          )
          setPrediction(matchingPredictions[matchingPredictions.length - 1])
          if (lastRecordedLabel.current !== confirmedLabel) {
            lastRecordedLabel.current = confirmedLabel
            setSignHistory((labels) => [...labels.slice(-7), confirmedLabel])
          }
          setIsConfirming(false)
        } else {
          setPrediction(null)
          setIsConfirming(true)
        }
        setApiError('')
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        predictionWindow.current = []
        setPrediction(null)
        setIsConfirming(false)
        setApiError(error instanceof Error ? error.message : 'Recognition is unavailable.')
      }
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null
        requestInFlight.current = false
        setIsRecognizing(false)
      }
    }
  }

  function startRecognitionLoop() {
    if (timerRef.current !== null) return
    if (!handModelReady) return
    startHandDetectionLoop()
    stopRecognitionLoop()
    void recognizeFrame()
    timerRef.current = window.setInterval(() => void recognizeFrame(), SAMPLE_INTERVAL_MS)
  }
  function clearSignHistory() {
    setSignHistory([])
  }

  useEffect(() => () => {
    stopRecognitionLoop()
    if (handDetectionFrame.current !== null) window.cancelAnimationFrame(handDetectionFrame.current)
    handDetectionFrame.current = null
    stream?.getTracks().forEach((track) => track.stop())
  }, [stream])

  useEffect(() => {
    startRecognitionLoopRef.current = startRecognitionLoop
    if (!stream || !handModelReady) return
    const timer = window.setTimeout(() => startRecognitionLoopRef.current(), 0)
    return () => window.clearTimeout(timer)
    // The loop callback reads current refs and is refreshed when readiness or
    // the stream changes; including it would restart the deferred startup on each render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stream, handModelReady])

  async function startCamera() {
    setCameraError('')
    setApiError('')
    setPrediction(null)
    predictionWindow.current = []
    lastRecordedLabel.current = null
    setSignHistory([])
    setIsConfirming(false)
    try {
      const cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      })
      setStream(cameraStream)
    } catch {
      setCameraError('Camera access is unavailable. Allow camera permission in your browser, then try again.')
    }
  }

  return (
    <section className="camera-workspace" aria-label="Camera recognition workspace">
      <div className="camera-panel">
        <div className="panel-heading">
          <div className="panel-title"><span className="step-badge">01</span><h3>Camera</h3></div>
          <span className="panel-hint">HAND LANDMARK FOCUS</span>
        </div>
        <div className="camera-stage">
          {stream ? (
            <>
              <video ref={videoRef} autoPlay playsInline muted onCanPlay={() => startRecognitionLoopRef.current()} />
              <canvas ref={overlayRef} className="hand-overlay" aria-hidden="true" />
              <span className="camera-live">{handsVisible ? 'HANDS TRACKED' : 'SHOW YOUR HANDS'}</span>
              <button className="stop-camera" onClick={stopCamera}>Stop camera</button>
            </>
          ) : (
            <div className="camera-empty">
              <span className="camera-glyph" aria-hidden="true">◉</span>
              <p>Open your camera to begin</p>
              <span>{handModelReady ? 'Hand tracking is ready. Keep your signing hands visible and well lit.' : 'Loading on-device hand tracking…'}</span>
              <button className="start-camera" onClick={startCamera} disabled={!handModelReady}>◎ &nbsp;Open camera</button>
            </div>
          )}
        </div>
        {cameraError && <p className="inline-error" role="alert">ⓘ &nbsp;{cameraError}</p>}
        {handDetectionError && <p className="inline-error" role="alert">ⓘ &nbsp;{handDetectionError}</p>}
        {apiError && <p className="inline-error" role="alert">ⓘ &nbsp;{apiError}</p>}
        <p className="privacy-footnote">◈ &nbsp;Hand tracking runs on this device. Centered square frames are sent for sign classification only while a hand is tracked; frames are not saved.</p>
      </div>
      <RecognitionPanel cameraReady={Boolean(stream)} isRecognizing={isRecognizing} isConfirming={isConfirming} prediction={prediction} />
      <GeneratedOutput signHistory={signHistory} onClear={clearSignHistory} />
    </section>
  )
}
