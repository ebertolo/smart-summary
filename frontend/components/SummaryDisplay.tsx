'use client'

import { useState, useEffect } from 'react'

interface SummaryDisplayProps {
  summary: string
  isStreaming: boolean
  onClear?: () => void
  onEdit?: (newSummary: string) => void
}

export default function SummaryDisplay({ summary, isStreaming, onClear, onEdit }: SummaryDisplayProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedSummary, setEditedSummary] = useState(summary)

  // Update editedSummary when summary changes
  useEffect(() => {
    setEditedSummary(summary)
  }, [summary])

  const wordCount = summary.trim().split(/\s+/).filter(Boolean).length
  const charCount = summary.length

  const handleEdit = () => {
    setEditedSummary(summary) // Ensure we start with current summary
    setIsEditing(true)
  }

  const handleSave = () => {
    if (onEdit) {
      onEdit(editedSummary)
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedSummary(summary)
    setIsEditing(false)
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(summary)
    // Could add a toast notification here
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-gray-700">Summary</h2>
        {isStreaming && (
          <div className="flex items-center gap-2 text-blue-600">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Generating...</span>
          </div>
        )}
      </div>

      <div className="min-h-[16rem] max-h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg border border-gray-200">
        {summary ? (
          isEditing ? (
            <textarea
              value={editedSummary}
              onChange={(e) => setEditedSummary(e.target.value)}
              className="w-full h-full min-h-[14rem] p-2 text-gray-800 bg-white border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              autoFocus
            />
          ) : (
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {summary}
              </p>
              {isStreaming && (
                <span className="inline-block w-2 h-5 bg-blue-600 animate-pulse ml-1"></span>
              )}
            </div>
          )
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg
              className="w-16 h-16 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-center">
              Your summary will appear here
              <br />
              <span className="text-sm">Enter text and click Summarize to get started</span>
            </p>
          </div>
        )}
      </div>

      {summary && (
        <div className="flex justify-between items-center gap-2">
          <div className="flex gap-4 text-sm text-gray-600">
            <span>{wordCount} words</span>
            <span>{charCount} characters</span>
          </div>
          
          {isEditing ? (
            <div className="flex gap-2">
              <button
                onClick={handleCancel}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors font-medium"
              >
                Save
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleEdit}
                disabled={isStreaming}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                title={isStreaming ? "Cannot edit while generating" : "Edit summary"}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                onClick={onClear}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1"
                title="Clear summary"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear
              </button>
              <button
                onClick={handleCopy}
                className="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-1"
                title="Copy to clipboard"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
