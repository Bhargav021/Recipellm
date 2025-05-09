import { 
  PencilIcon, 
  MagnifyingGlassIcon,
  CheckIcon,
  XMarkIcon,
  PlusCircleIcon,
  ChatBubbleOvalLeftIcon,
  PlusIcon,
  StarIcon as StarIconOutline
} from '@heroicons/react/24/outline';
import {
  StarIcon,
  TrashIcon
} from '@heroicons/react/24/solid';
import { useState, useEffect } from 'react';

interface ChatHistoryProps {
  conversations: Array<{
    id: string;
    title: string;
    lastMessage: string;
    timestamp: string;
    starred?: boolean;
  }>;
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onRenameChat?: (id: string, newTitle: string) => void;
  onDeleteChat?: (id: string) => void;
  onStarChat?: (id: string, starred: boolean) => void;
}

export default function ChatHistory({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onStarChat
}: ChatHistoryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  
  // Filter and sort conversations - starred at top, then the rest
  const filteredConversations = conversations
    .filter(conv => 
      !searchQuery || 
      conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.lastMessage.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      // First sort by starred status (starred first)
      if (a.starred && !b.starred) return -1;
      if (!a.starred && b.starred) return 1;
      // Then sort by timestamp (newest first) within each group
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
  
  const handleStartRename = (id: string, currentTitle: string) => {
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  // Handle double-click to edit chat name
  const handleDoubleClick = (id: string, currentTitle: string) => {
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const handleSaveRename = (id: string) => {
    if (onRenameChat && editTitle.trim()) {
      onRenameChat(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = () => {
    setEditingId(null);
  };

  const handleDeleteChat = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (onDeleteChat) {
      onDeleteChat(id);
    }
  };

  const handleStarChat = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (onStarChat) {
      const conversation = conversations.find(conv => conv.id === id);
      if (conversation) {
        onStarChat(id, !conversation.starred);
      }
    }
  };

  // Helper function to highlight matching text
  const highlightText = (text: string, query: string): React.ReactNode => {
    if (!query.trim()) {
      return text;
    }
    
    const regex = new RegExp(`(${query.trim()})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, i) => 
      regex.test(part) ? (
        <span key={i} className="bg-yellow-200 text-black">
          {part}
        </span>
      ) : (
        part
      )
    );
  };

  return (
    <div className="w-64 flex flex-col h-full border-r border-slate-200 theme-green:border-greenTheme-softGreen theme-green:bg-greenTheme-cream">
      {/* Search */}
      <div className="p-2 border-b border-slate-200 theme-green:border-greenTheme-softGreen">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border border-slate-200 rounded-full pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-slate-400 placeholder-slate-500 theme-green:bg-greenTheme-lightCream theme-green:text-greenTheme-deepGreen theme-green:border-greenTheme-softGreen theme-green:placeholder-greenTheme-mutedOlive"
            />
            <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-2.5 text-slate-500 theme-green:text-greenTheme-deepGreen" />
          </div>
          <button 
            onClick={onNewChat}
            className="theme-exempt flex items-center justify-center p-1.5 rounded-full bg-gradient-to-r from-slate-600 to-slate-700 text-white hover:opacity-90 border-none flex-shrink-0 transition-all shadow-sm theme-green:from-greenTheme-deepGreen theme-green:to-greenTheme-darkForest"
          >
            <div className="relative">
              <ChatBubbleOvalLeftIcon className="w-5 h-5" />
              <PlusIcon className="w-2.5 h-2.5 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
            </div>
          </button>
        </div>
      </div>
      
      {/* Chat List */}
      <div className="flex-1 overflow-y-auto theme-green:bg-greenTheme-cream">
        {filteredConversations.map((conversation) => {          
          return (
            <div key={conversation.id} className="relative">
              <div
                onClick={() => editingId !== conversation.id && onSelectConversation(conversation.id)}
                onDoubleClick={() => handleDoubleClick(conversation.id, conversation.title)}
                className={`w-full py-2 px-4 text-left transition-colors flex items-center justify-between ${
                  activeConversationId === conversation.id 
                    ? 'bg-gray-200 theme-green:bg-greenTheme-softGreen border-l-4 theme-green:border-l-greenTheme-deepGreen' 
                    : 'hover:bg-gray-100 theme-green:hover:bg-greenTheme-lightCream border-l-4 border-transparent'
                } cursor-pointer text-slate-900 theme-green:text-greenTheme-deepGreen`}
              >
                {editingId === conversation.id ? (
                  <div className="flex items-center w-full pr-2">
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full text-sm bg-white text-slate-900 border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-slate-500 theme-green:bg-greenTheme-lightCream theme-green:text-greenTheme-deepGreen theme-green:border-greenTheme-softGreen"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveRename(conversation.id);
                        } else if (e.key === 'Escape') {
                          handleCancelRename();
                        }
                      }}
                    />
                    <div className="flex ml-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSaveRename(conversation.id);
                        }}
                        className="theme-exempt p-1 text-green-600 hover:text-green-700 theme-green:text-greenTheme-deepGreen theme-green:hover:text-greenTheme-darkForest"
                      >
                        <CheckIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCancelRename();
                        }}
                        className="theme-exempt p-1 text-red-600 hover:text-red-700"
                      >
                        <XMarkIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <h3 className="text-sm font-medium truncate flex-1">
                      {searchQuery ? highlightText(conversation.title, searchQuery) : conversation.title}
                    </h3>
                    <div className="flex items-center ml-2">
                      <button 
                        onClick={(e) => handleStarChat(conversation.id, e)}
                        className={`theme-exempt p-1 rounded ${conversation.starred ? 'text-yellow-400' : 'text-gray-400'} hover:text-yellow-500 transition-colors mr-1`}
                      >
                        {conversation.starred ? (
                          <StarIcon className="w-4 h-4" />
                        ) : (
                          <StarIconOutline className="w-4 h-4" />
                        )}
                      </button>
                      <button 
                        onClick={(e) => handleDeleteChat(conversation.id, e)}
                        className="theme-exempt p-1 rounded text-red-500 hover:text-red-600 transition-colors mr-1"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
} 