import React from 'react'

export default function PlatformBadge({ platform }) {
  const normalized = (platform || 'unknown').toLowerCase()
  
  let color = '#6f6d62'
  let letter = 'U'
  if (normalized.includes('meta') || normalized.includes('facebook')) {
    color = '#1877F2'
    letter = 'M'
  } else if (normalized.includes('google')) {
    color = '#3d6bdb'
    letter = 'G'
  } else if (normalized.includes('tiktok')) {
    color = '#111319'
    letter = 'T'
  } else if (normalized.includes('taboola')) {
    color = '#0aa0dd'
    letter = 'T'
  } else {
    letter = normalized.charAt(0).toUpperCase() || 'U'
  }

  return (
    <div className="platform-badge">
      <div className="platform-icon" style={{ backgroundColor: color }}>
        {letter}
      </div>
      <span className="platform-name">{normalized}</span>
    </div>
  )
}
