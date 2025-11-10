'use client'

import { useState } from 'react'
import { summarizeText } from '@/lib/api'

interface SummaryFormProps {
  onSummaryStart: () => void
  onSummaryChunk: (chunk: string) => void
  onSummaryComplete: () => void
  onAuthRequired: () => void
  onSummaryRequest?: (text: string, strategy: string, detailLevel: string) => void
  isAuthenticated: boolean
}

export default function SummaryForm({
  onSummaryStart,
  onSummaryChunk,
  onSummaryComplete,
  onAuthRequired,
  onSummaryRequest,
  isAuthenticated,
}: SummaryFormProps) {
  const [text, setText] = useState('')
  const [strategy, setStrategy] = useState('hierarchical')
  const [compressionRatio, setCompressionRatio] = useState(20) // Percentage (5-50%)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isAuthenticated) {
      onAuthRequired()
      return
    }

    if (text.trim().length < 100) {
      setError('Text must be at least 100 characters long')
      return
    }

    if (text.length > 300000) {
      setError('Text exceeds maximum limit of 300,000 characters')
      return
    }

    setError('')
    setIsLoading(true)
    onSummaryStart()

    // Notify parent about the request
    if (onSummaryRequest) {
      onSummaryRequest(text, strategy, `${compressionRatio}%`)
    }

    try {
      await summarizeText(
        { text, strategy, compression_ratio: compressionRatio / 100 }, // Convert % to decimal
        onSummaryChunk
      )
      onSummaryComplete()
    } catch (err: any) {
      setError(err.message || 'Failed to summarize text')
      onSummaryComplete()
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setText('')
    setError('')
  }

  const charCount = text.length
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="text" className="block text-sm font-bold text-gray-700 mb-2">
          Enter Text to Summarize
        </label>
        <textarea
          id="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full h-64 px-4 py-3 text-gray-800 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder:text-gray-400"
          placeholder="Paste your text here... (minimum 100 characters, maximum 300,000)"
          disabled={isLoading}
        />
        <div className="mt-2 flex justify-between text-sm text-gray-500">
          <span>{wordCount.toLocaleString()} words</span>
          <span className={charCount < 100 ? 'text-red-500' : charCount > 300000 ? 'text-orange-500' : ''}>
            {charCount.toLocaleString()} / 300,000 characters
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="strategy" className="block text-sm font-medium text-gray-700 mb-2">
            Strategy
          </label>
          <select
            id="strategy"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            className="w-full px-4 py-2 text-gray-800 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          >
            <option value="simple">Simple - Quick summary</option>
            <option value="hierarchical">Hierarchical - Structured</option>
            <option value="detailed">Detailed - Comprehensive</option>
          </select>
        </div>

        <div>
          <label htmlFor="compression" className="block text-sm font-medium text-gray-700 mb-2">
            Summary Size: {compressionRatio}% of original
          </label>
          <input
            id="compression"
            type="range"
            min="5"
            max="50"
            step="5"
            value={compressionRatio}
            onChange={(e) => setCompressionRatio(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            disabled={isLoading}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <div className="text-left w-1/3">
              <div>5%</div>
              <div>(Brief)</div>
            </div>
            <div className="text-center w-1/3">
              <div>25%</div>
              <div>(Balanced)</div>
            </div>
            <div className="text-right w-1/3">
              <div>50%</div>
              <div>(Detailed)</div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isLoading || !text.trim() || charCount < 100 || charCount > 300000}
          className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Summarizing...
            </span>
          ) : (
            '✨ Summarize'
          )}
        </button>

        <button
          type="button"
          onClick={handleClear}
          disabled={isLoading}
          className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Clear
        </button>
      </div>
    </form>
  )
}
