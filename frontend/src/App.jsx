import React, { useEffect, useState } from 'react'
import CameraPose from './components/CameraPose'
import FeedbackPanel from './components/FeedbackPanel'
import { startSession, sendFrame, getMetrics, sessionChat } from './services/api'

export default function App(){
  const [sessionId, setSessionId] = useState(null)
  const [feedback, setFeedback] = useState({short:null,long:null,metrics:null})

  useEffect(()=> {
    (async ()=>{
      const sid = await startSession('squat')
      setSessionId(sid)
    })()
  },[])

  async function handleFrame(keypoints){
    if(!sessionId) return
    const res = await sendFrame(sessionId, keypoints)
    if(res){
      setFeedback({ short: res.short, long: res.long, metrics: res.metrics })
    }
  }

  return (
    <div style={{display:'flex',gap:20,padding:20}}>
      <div>
        <CameraPose onFrame={handleFrame} />
      </div>
      <div style={{width:400}}>
        <h2>Coach Feedback</h2>
        <FeedbackPanel feedback={feedback} sessionId={sessionId} />
      </div>
    </div>
  )
}
