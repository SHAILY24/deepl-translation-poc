import { useState, useEffect } from 'react'

// API base URL - update for production
const API_URL = import.meta.env.PROD 
  ? 'http://localhost:13601' 
  : 'http://localhost:13601'

function App() {
  const [text, setText] = useState('')
  const [sourceLang, setSourceLang] = useState('AUTO')
  const [targetLang, setTargetLang] = useState('ES')
  const [translation, setTranslation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [languages, setLanguages] = useState([])

  // Fetch supported languages on mount
  useEffect(() => {
    fetch(`${API_URL}/api/languages`)
      .then(res => res.json())
      .then(data => setLanguages(data.languages))
      .catch(err => console.error('Failed to load languages:', err))
  }, [])

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError('Please enter some text to translate')
      return
    }

    setLoading(true)
    setError('')
    setTranslation('')

    try {
      const requestBody = {
        text: text.trim(),
        target_lang: targetLang
      }

      // Only include source_lang if not auto-detect
      if (sourceLang !== 'AUTO') {
        requestBody.source_lang = sourceLang
      }

      const response = await fetch(`${API_URL}/api/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Translation failed')
      }

      setTranslation(data.translated_text)
    } catch (err) {
      setError(err.message || 'An error occurred during translation')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleTranslate()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            DeepL Translation Tool
          </h1>
          <p className="text-gray-600">
            Powered by DeepL API - Professional translation at your fingertips
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-lg shadow-xl p-6 md:p-8">
          {/* Language Selectors */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Language
              </label>
              <select
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="AUTO">Auto-detect</option>
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Language
              </label>
              <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Text Input and Output */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            {/* Input */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Text to Translate
                </label>
                <span className="text-xs text-gray-500">
                  {text.length} / 50,000 characters
                </span>
              </div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Enter text to translate... (Ctrl+Enter to translate)"
                className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                maxLength={50000}
              />
            </div>

            {/* Output */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Translation
              </label>
              <div className="w-full h-64 px-4 py-3 border border-gray-200 rounded-lg bg-gray-50 overflow-y-auto">
                {loading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  </div>
                ) : translation ? (
                  <p className="text-gray-800 whitespace-pre-wrap">{translation}</p>
                ) : (
                  <p className="text-gray-400 italic">Translation will appear here...</p>
                )}
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Translate Button */}
          <div className="flex justify-center">
            <button
              onClick={handleTranslate}
              disabled={loading || !text.trim()}
              className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Translating...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M7 2a1 1 0 011 1v1h3a1 1 0 110 2H9.578a18.87 18.87 0 01-1.724 4.78c.29.354.596.696.914 1.026a1 1 0 11-1.44 1.389c-.188-.196-.373-.396-.554-.6a19.098 19.098 0 01-3.107 3.567 1 1 0 01-1.334-1.49 17.087 17.087 0 003.13-3.733 18.992 18.992 0 01-1.487-2.494 1 1 0 111.79-.89c.234.47.489.928.764 1.372.417-.934.752-1.913.997-2.927H3a1 1 0 110-2h3V3a1 1 0 011-1zm6 6a1 1 0 01.894.553l2.991 5.982a.869.869 0 01.02.037l.99 1.98a1 1 0 11-1.79.895L15.383 16h-4.764l-.724 1.447a1 1 0 11-1.788-.894l.99-1.98.019-.038 2.99-5.982A1 1 0 0113 8zm-1.382 6h2.764L13 11.236 11.618 14z" clipRule="evenodd" />
                  </svg>
                  Translate
                </>
              )}
            </button>
          </div>

          {/* Footer Info */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
            <p>Press <kbd className="px-2 py-1 bg-gray-100 rounded">Ctrl</kbd> + <kbd className="px-2 py-1 bg-gray-100 rounded">Enter</kbd> to translate quickly</p>
          </div>
        </div>

        {/* Tech Stack Footer */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>Built with FastAPI, React 18, Tailwind CSS, and Docker</p>
          <p className="mt-1">Created by Shaily Sharma</p>
        </div>
      </div>
    </div>
  )
}

export default App
