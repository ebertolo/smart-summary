'use client'

import { useState, useEffect, useCallback } from 'react'

interface SummaryItem {
  id: string
  text: string
  summary: string
  strategy: string
  detailLevel: string
  timestamp: number
  wordCount: number
}

interface SummaryHistoryProps {
  onSelectSummary: (summaryData: { id: string; summary: string }) => void
}

export default function SummaryHistory({ onSelectSummary }: SummaryHistoryProps) {
  const [history, setHistory] = useState<SummaryItem[]>([])
  const [isExpanded, setIsExpanded] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
    // Load history from localStorage
    const saved = localStorage.getItem('summaryHistory')
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load history:', e)
      }
    }
  }, [])

  const addToHistory = useCallback((item: Omit<SummaryItem, 'id' | 'timestamp'>) => {
    const newItem: SummaryItem = {
      ...item,
      id: Date.now().toString(),
      timestamp: Date.now(),
    }
    
    setHistory(prevHistory => {
      // Check if this item already exists (by comparing summary content and timestamp proximity)
      const isDuplicate = prevHistory.some(existing => 
        existing.summary === newItem.summary && 
        Math.abs(existing.timestamp - newItem.timestamp) < 2000 // Within 2 seconds
      )
      
      if (isDuplicate) {
        console.log('Duplicate detected, skipping...')
        return prevHistory
      }
      
      const updatedHistory = [newItem, ...prevHistory].slice(0, 20) // Keep last 20
      localStorage.setItem('summaryHistory', JSON.stringify(updatedHistory))
      return updatedHistory
    })
  }, [])

  const updateItem = useCallback((id: string, newSummary: string) => {
    setHistory(prevHistory => {
      const updatedHistory = prevHistory.map(item =>
        item.id === id
          ? { ...item, summary: newSummary, wordCount: newSummary.trim().split(/\s+/).filter(Boolean).length }
          : item
      )
      localStorage.setItem('summaryHistory', JSON.stringify(updatedHistory))
      return updatedHistory
    })
  }, [])

  const deleteItem = (id: string) => {
    setHistory(prevHistory => {
      const updatedHistory = prevHistory.filter(item => item.id !== id)
      localStorage.setItem('summaryHistory', JSON.stringify(updatedHistory))
      return updatedHistory
    })
  }

  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem('summaryHistory')
  }

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  // Expose addToHistory method globally for use by parent component
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return
    
    (window as any).addToSummaryHistory = addToHistory;
    (window as any).updateSummaryHistory = updateItem
    
    // Cleanup on unmount
    return () => {
      if (typeof window !== 'undefined') {
        delete (window as any).addToSummaryHistory
        delete (window as any).updateSummaryHistory
      }
    }
  }, [addToHistory, updateItem])

  if (history.length === 0) {
    return null
  }

  // Prevent SSR hydration mismatch
  if (!isMounted) {
    return null
  }

  return (
    <div className="mt-8 bg-white rounded-2xl shadow-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-bold text-gray-800">Summary History</h3>
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
            {history.length}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
          <button
            onClick={clearHistory}
            className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      <div className={`space-y-3 ${isExpanded ? '' : 'max-h-96 overflow-y-auto'}`}>
        {history.map((item) => (
          <div
            key={item.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50/30 transition-colors cursor-pointer group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1" onClick={() => onSelectSummary({ id: item.id, summary: item.summary })}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-gray-500">
                    {formatDate(item.timestamp)}
                  </span>
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                    {item.strategy}
                  </span>
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                    {item.detailLevel}
                  </span>
                  <span className="text-xs text-gray-500">
                    {item.wordCount} words
                  </span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">
                  {item.summary}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  deleteItem(item.id)
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 text-red-500 hover:bg-red-50 rounded transition-all"
                title="Delete"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
