import { useState } from 'react'
import Chat, { ChatProvider } from './components/Chat'
import { Cog6ToothIcon, CommandLineIcon } from '@heroicons/react/24/outline'

export type ViewMode = 'user' | 'dev';

function App() {
  const [theme, setTheme] = useState<'default' | 'green'>('green')
  const [showDevMode, setShowDevMode] = useState(false)

  const toggleTheme = () => {
    setTheme(prev => prev === 'default' ? 'green' : 'default')
  }

  const toggleDevMode = () => {
    setShowDevMode(prev => !prev)
  }

  return (
    <div className={`flex flex-col h-screen ${theme === 'green' ? 'theme-green bg-greenTheme-cream' : 'bg-white'}`}>
      <div className="absolute top-4 right-4 z-10 flex space-x-2">
        <button 
          onClick={toggleDevMode}
          className={`p-2 rounded-full transition-colors shadow-sm ${
            theme === 'green' 
              ? 'bg-greenTheme-softGreen hover:bg-greenTheme-hoverGreen text-greenTheme-deepGreen border border-greenTheme-deepGreen border-opacity-20' 
              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
          }`}
          title={`${showDevMode ? 'Hide' : 'Show'} developer mode`}
        >
          <CommandLineIcon className="w-5 h-5" />
        </button>
        <button 
          onClick={toggleTheme}
          className={`p-2 rounded-full transition-colors shadow-sm ${
            theme === 'green' 
              ? 'bg-greenTheme-softGreen hover:bg-greenTheme-hoverGreen text-greenTheme-deepGreen border border-greenTheme-deepGreen border-opacity-20' 
              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
          }`}
          title={`Switch to ${theme === 'default' ? 'green' : 'default'} theme`}
        >
          <Cog6ToothIcon className="w-5 h-5" />
        </button>
      </div>
      <main className="flex-1 overflow-hidden">
        {showDevMode ? (
          <div className="flex h-full">
            <ChatProvider shouldAutoInitialize={true}>
              <div className="flex h-full">
                {/* This is the user view with sidebar */}
                <Chat viewMode="user" showSidebar={true} disableInput={false} />
              </div>
            </ChatProvider>
            <div className="border-l border-greenTheme-softGreen h-full w-1/2">
              <div className="h-10 bg-greenTheme-deepGreen flex items-center justify-center font-medium text-white">
                Developer View
              </div>
              <div className="h-[calc(100%-2.5rem)] overflow-hidden">
                <ChatProvider shouldAutoInitialize={false}>
                  <Chat viewMode="dev" showSidebar={false} disableInput={true} />
                </ChatProvider>
              </div>
            </div>
          </div>
        ) : (
          <ChatProvider shouldAutoInitialize={true}>
            <Chat viewMode="user" showSidebar={true} disableInput={false} />
          </ChatProvider>
        )}
      </main>
    </div>
  )
}

export default App
