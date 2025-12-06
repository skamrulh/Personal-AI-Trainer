import React from 'react'

export default function FeedbackPanel({ feedback }) {
  return (
    <div>
      <div style={{padding:10,border:'1px solid #eee',minHeight:60}}>
        <strong>Short:</strong>
        <div>{feedback.short || '—'}</div>
      </div>
      <div style={{marginTop:10,padding:10,border:'1px solid #eee',minHeight:120}}>
        <strong>Explanation:</strong>
        <div>{feedback.long || '—'}</div>
      </div>
      <div style={{marginTop:10}}>
        <strong>Metrics:</strong>
        <pre style={{background:'#f7f7f7',padding:10}}>{JSON.stringify(feedback.metrics || {}, null, 2)}</pre>
      </div>
    </div>
  )
}
