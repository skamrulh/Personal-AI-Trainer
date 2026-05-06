import React, { useRef, useEffect } from 'react'
import * as tf from '@tensorflow/tfjs'                    // FIX 2: tf was never imported
import * as posedetection from '@tensorflow-models/pose-detection'
import '@tensorflow/tfjs-backend-webgl'
import { drawKeypoints, drawSkeleton } from '../utils/draw'

export default function CameraPose({ onFrame }) {
  const videoRef    = useRef(null)
  const canvasRef   = useRef(null)
  const detectorRef = useRef(null)
  const throttleRef = useRef(0)
  const rafRef      = useRef(null)   // FIX 7: track RAF handle for cancellation

  useEffect(() => {
    let mounted = true

    async function init() {
      try {
        await tf.setBackend('webgl')
        await tf.ready()

        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 },
        })
        if (!mounted) { stream.getTracks().forEach(t => t.stop()); return }

        videoRef.current.srcObject = stream
        await videoRef.current.play()

        detectorRef.current = await posedetection.createDetector(
          posedetection.SupportedModels.MoveNet,
          { modelType: 'SinglePose.Lightning' },
        )
        if (mounted) rafRef.current = requestAnimationFrame(loop)
      } catch (err) {
        console.error('PT Coach init error:', err)
      }
    }

    init()

    // FIX 7: cleanup cancels the animation loop and stops the camera stream
    return () => {
      mounted = false
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop())
      }
    }
  }, [])

  async function loop() {
    const video  = videoRef.current
    const canvas = canvasRef.current

    if (video && canvas && detectorRef.current) {
      try {
        const poses = await detectorRef.current.estimatePoses(video)
        const ctx   = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        if (poses?.length) {
          drawKeypoints(poses[0].keypoints, ctx)
          drawSkeleton(poses[0].keypoints, ctx)

          const now = Date.now()
          if (now - throttleRef.current > 250) {          // ~4 fps to backend
            const kp = poses[0].keypoints.map(k => ({
              name: k.name, x: k.x, y: k.y, score: k.score,
            }))
            onFrame(kp)
            throttleRef.current = now
          }
        }
      } catch (err) {
        // Estimation errors are non-fatal; keep looping
        console.warn('Pose estimation error:', err)
      }
    }

    rafRef.current = requestAnimationFrame(loop)   // FIX 7: store handle every frame
  }

  return (
    <div>
      <video ref={videoRef} width={640} height={480} style={{ display: 'none' }} />
      <canvas ref={canvasRef} width={640} height={480} style={{ border: '1px solid #ddd' }} />
    </div>
  )
}
