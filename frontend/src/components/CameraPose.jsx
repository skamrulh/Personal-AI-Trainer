import React, { useRef, useEffect } from 'react'
import * as posedetection from '@tensorflow-models/pose-detection'
import '@tensorflow/tfjs-backend-webgl'
import { drawKeypoints, drawSkeleton } from '../utils/draw'

export default function CameraPose({ onFrame }){
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const detectorRef = useRef(null)
  const throttleRef = useRef(0)

  useEffect(()=> {
    let mounted = true
    async function init(){
      await import('@tensorflow/tfjs-backend-webgl')
      await tf.setBackend('webgl')
      await tf.ready()
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width:640, height:480 } })
      videoRef.current.srcObject = stream
      await videoRef.current.play()
      detectorRef.current = await posedetection.createDetector(posedetection.SupportedModels.MoveNet, { modelType: 'SinglePose.Lightning' })
      requestAnimationFrame(loop)
    }
    init()
    return ()=> { mounted = false }
  },[])

  async function loop(){
    const video = videoRef.current
    const canvas = canvasRef.current
    if(video && detectorRef.current){
      const poses = await detectorRef.current.estimatePoses(video)
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      if(poses && poses.length){
        drawKeypoints(poses[0].keypoints, ctx)
        drawSkeleton(poses[0].keypoints, ctx)
        const now = Date.now()
        if(now - throttleRef.current > 250){ // send ~4x/sec
          const kp = poses[0].keypoints.map(k=>({ name:k.name, x:k.x, y:k.y, score:k.score }))
          onFrame(kp)
          throttleRef.current = now
        }
      }
    }
    requestAnimationFrame(loop)
  }

  return (
    <div>
      <video ref={videoRef} width={640} height={480} style={{display:'none'}} />
      <canvas ref={canvasRef} width={640} height={480} style={{border:'1px solid #ddd'}} />
    </div>
  )
}
