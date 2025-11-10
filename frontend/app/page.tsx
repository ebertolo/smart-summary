'use client'

import { useState, useEffect, useRef } from 'react'
import SummaryForm from '@/components/SummaryForm'
import SummaryDisplay from '@/components/SummaryDisplay'
import AuthModal from '@/components/AuthModal'
import SummaryHistory from '@/components/SummaryHistory'
import { logout } from '@/lib/api'

export default function Home() {
  const [summary, setSummary] = useState('')
  const [currentText, setCurrentText] = useState('')
  const [currentStrategy, setCurrentStrategy] = useState('')
  const [currentDetailLevel, setCurrentDetailLevel] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [username, setUsername] = useState('')

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    setIsAuthenticated(!!token)
    if (storedUsername) {
      setUsername(storedUsername)
    }
  }, [])

  const handleSummaryStart = () => {
    setSummary('')
    setIsStreaming(true)
  }

  const handleSummaryChunk = (chunk: string) => {
    setSummary(prev => prev + chunk)
  }

  const handleSummaryComplete = () => {
    setIsStreaming(false)
    // Mark that we should save this summary to history
    shouldSaveToHistory.current = true
  }

  // Track if we should save to history (only for NEW summaries, not selected ones)
  const shouldSaveToHistory = useRef(false)
  const selectedHistoryId = useRef<string | null>(null)

  // Save to history ONLY when summary is complete and it's a NEW summary (not selected from history)
  useEffect(() => {
    if (!isStreaming && summary && currentText && shouldSaveToHistory.current) {
      const wordCount = summary.trim().split(/\s+/).filter(Boolean).length
      if (typeof window !== 'undefined' && (window as any).addToSummaryHistory) {
        (window as any).addToSummaryHistory({
          text: currentText,
          summary: summary,
          strategy: currentStrategy,
          detailLevel: currentDetailLevel,
          wordCount: wordCount,
        })
        shouldSaveToHistory.current = false // Reset flag after saving
      }
    }
  }, [isStreaming, summary, currentText, currentStrategy, currentDetailLevel])

  const handleSelectFromHistory = (summaryData: { id: string; summary: string }) => {
    setSummary(summaryData.summary)
    selectedHistoryId.current = summaryData.id
    shouldSaveToHistory.current = false // Don't save when selecting from history
  }

  const handleEditSummary = (newSummary: string) => {
    setSummary(newSummary)
    
    // If this was selected from history, update the history item
    if (selectedHistoryId.current && typeof window !== 'undefined' && (window as any).updateSummaryHistory) {
      (window as any).updateSummaryHistory(selectedHistoryId.current, newSummary)
    }
  }

  const handleSummaryRequest = (text: string, strategy: string, detailLevel: string) => {
    setCurrentText(text)
    setCurrentStrategy(strategy)
    setCurrentDetailLevel(detailLevel)
  }

  const handleAuthRequired = () => {
    setShowAuthModal(true)
  }

  const handleAuthSuccess = () => {
    setIsAuthenticated(true)
    setShowAuthModal(false)
    // Get username from localStorage (set by AuthModal)
    const storedUsername = localStorage.getItem('username')
    if (storedUsername) {
      setUsername(storedUsername)
    }
  }

  const handleLogout = async () => {
    // Call backend logout endpoint for logging
    await logout()
    
    // Clear local state
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setIsAuthenticated(false)
    setUsername('')
    setSummary('')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Smart Summary
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            AI-Powered Text Summarization with Real-time Streaming
          </p>
          
          {/* Auth Status */}
          {isAuthenticated && (
            <div className="flex justify-end items-center gap-4">
              <div className="flex items-center gap-3">
                <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  ✓ User logged: {username}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors font-medium"
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </header>

        {/* Main Content - Only show if authenticated */}
        {isAuthenticated ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Section */}
              <div className="bg-white rounded-2xl shadow-xl p-6 lg:p-8">
                <SummaryForm
                  onSummaryStart={handleSummaryStart}
                  onSummaryChunk={handleSummaryChunk}
                  onSummaryComplete={handleSummaryComplete}
                  onAuthRequired={handleAuthRequired}
                  onSummaryRequest={handleSummaryRequest}
                  isAuthenticated={isAuthenticated}
                />
              </div>

              {/* Output Section */}
              <div className="bg-white rounded-2xl shadow-xl p-6 lg:p-8">
                <SummaryDisplay
                  summary={summary}
                  isStreaming={isStreaming}
                  onClear={() => setSummary('')}
                  onEdit={handleEditSummary}
                />
              </div>
            </div>

            {/* History Section */}
            <SummaryHistory onSelectSummary={handleSelectFromHistory} />
          </>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="text-6xl mb-4">🔒</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Authentication Required
            </h2>
            <p className="text-gray-600 mb-6">
              Please login to start summarizing your texts
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Login Now
            </button>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">🎯</div>
              <h3 className="text-lg font-bold text-gray-800">Summarization Strategies</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                <h4 className="font-semibold text-blue-900 mb-2">⚡ Simple</h4>
                <p className="text-sm text-gray-600">
                  Fast single-pass summary. Best for short texts (&lt;50K chars). Direct AI summarization without chunking.
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                <h4 className="font-semibold text-purple-900 mb-2">🔄 Hierarchical</h4>
                <p className="text-sm text-gray-600">
                  Multi-level processing for medium/long texts. Chunks → Summaries → Combined. Balances speed and quality.
                </p>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                <h4 className="font-semibold text-green-900 mb-2">📊 Detailed</h4>
                <p className="text-sm text-gray-600">
                  Map-Reduce with extractive analysis. Extracts key sentences first, then AI refines. Most comprehensive.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 text-sm">
          <p>Powered by FastAPI, Next.js, and Claude AI</p>
        </footer>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onSuccess={handleAuthSuccess}
        />
      )}
    </main>
  )
}
