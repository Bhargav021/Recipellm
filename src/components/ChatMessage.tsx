import { PaperAirplaneIcon, UserIcon } from '@heroicons/react/24/solid';
import { ViewMode } from '../App';

interface ChatMessageProps {
  content: string;
  isUser: boolean;
  timestamp: string;
  sqlCode?: string; // Keeping this prop name for compatibility, but it will store MongoDB queries
  rawLlmResponse?: string;
  viewMode: ViewMode;
}

export default function ChatMessage({ content, isUser, timestamp, sqlCode, rawLlmResponse, viewMode }: ChatMessageProps) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`flex items-start max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div>
          <div className={`rounded-lg px-3 py-2 ${
            isUser ? 'user-message' : 'ai-message'
          }`}>
            <div className="text-sm whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: content }} />

            
            {/* In dev mode, also show MongoDB queries and raw LLM response */}
            {viewMode === 'dev' && !isUser && (
              <div className="mt-3 border-t border-greenTheme-softGreen pt-2">
                {sqlCode && (
                  <div className="mb-2">
                    <p className="text-xs font-semibold text-greenTheme-deepGreen mb-1">MongoDB Query:</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">{sqlCode}</pre>
                  </div>
                )}
                
                {rawLlmResponse && (
                  <div>
                    <p className="text-xs font-semibold text-greenTheme-deepGreen mb-1">Raw LLM Response:</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">{rawLlmResponse}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}