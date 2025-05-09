import { useState, useRef, useEffect, createContext, useContext } from 'react';
import { PaperAirplaneIcon, BoltIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import ChatMessage from './ChatMessage';
import ChatHistory from './ChatHistory';
import { ViewMode } from '../App';
import { queryLLM } from '../services/api';

type PendingAction =
  | {
      type: "confirm";
      prompt: string;
      query: any;
    }
  | {
      type: "collect";
      prompt: string;
      fields: string[];
      operation: string;
      collection: string;
    }
  | null;


interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  sqlCode?: string;  // Will store MongoDB code despite the name
  rawLlmResponse?: string;  // Raw response from LLM
}

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messages: Message[];
  starred?: boolean;
}

interface SuggestedPrompt {
  title: string;
  prompt: string;
  description?: string;
}

interface ChatProps {
  viewMode: ViewMode;
  showSidebar?: boolean;
  disableInput?: boolean;
}

// Create a shared context for chat state
interface ChatContextType {
  conversations: Conversation[];
  setConversations: React.Dispatch<React.SetStateAction<Conversation[]>>;
  activeConversationId: string | null;
  setActiveConversationId: React.Dispatch<React.SetStateAction<string | null>>;
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  initialized: boolean;
  setInitialized: React.Dispatch<React.SetStateAction<boolean>>;
}

const ChatContext = createContext<ChatContextType | null>(null);

// Provider component to wrap around both Chat components
export function ChatProvider({ 
  children, 
  shouldAutoInitialize = true 
}: { 
  children: React.ReactNode;
  shouldAutoInitialize?: boolean;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  // Automatically initialize with a new chat if configured to do so
  useEffect(() => {
    if (shouldAutoInitialize && !initialized && conversations.length === 0) {
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title: `New Chat 1`,
        lastMessage: '',
        timestamp: new Date().toLocaleString(),
        messages: [],
      };
      setConversations([newConversation]);
      setActiveConversationId(newConversation.id);
      setInitialized(true);
    }
  }, [shouldAutoInitialize, initialized, conversations.length]);

  return (
    <ChatContext.Provider value={{
      conversations,
      setConversations,
      activeConversationId,
      setActiveConversationId,
      input,
      setInput,
      isLoading,
      setIsLoading,
      initialized,
      setInitialized
    }}>
      {children}
    </ChatContext.Provider>
  );
}

// Hook to access the chat context
function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}

// Only expose ChatProvider and Chat at export
export default function Chat({ viewMode, showSidebar = true, disableInput = false }: ChatProps) {
  const context = useChatContext();
  const { 
    conversations, 
    setConversations, 
    activeConversationId, 
    setActiveConversationId, 
    input, 
    setInput, 
    isLoading, 
    setIsLoading
  } = context;
  
  
  const [isPromptDropdownOpen, setIsPromptDropdownOpen] = useState(false);
  const [hoveredPrompt, setHoveredPrompt] = useState<string | null>(null);
  const [mode, setMode] = useState<"mongo" | "sql">("mongo");
  const [pendingAction, setPendingAction] = useState<PendingAction | null >(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});


  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Define suggested prompts related to recipes and nutrition
  const suggestedPrompts: SuggestedPrompt[] = [
    {
      title: "Find a Recipe by Ingredients",
      prompt: "What can I make with chicken, spinach, and feta cheese?",
      description: "List ingredients you have on hand"
    },
    {
      title: "Get Nutritional Information",
      prompt: "What's the nutritional value of a slice of avocado toast?",
      description: "Ask about calories, protein, etc."
    },
    {
      title: "Meal Planning Help",
      prompt: "Create a 5-day meal plan for a family of four with a focus on Mediterranean cuisine.",
      description: "Specify dietary preferences"
    },
    {
      title: "Find Similar Recipes",
      prompt: "I love chicken parmesan. What are some similar dishes I could try?",
      description: "Discover related recipes"
    },
    {
      title: "Dietary Restrictions",
      prompt: "What are some gluten-free dessert options that are also low in sugar?",
      description: "Find recipes for specific diets"
    },
    {
      title: "Cooking Tips",
      prompt: "What's the best way to perfectly sear a steak?",
      description: "Get advice on cooking techniques"
    }
  ];

  const handlePromptClick = (prompt: string) => {
    setInput(prompt);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversationId, conversations]);

  const handleNewChat = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: `New Chat ${conversations.length + 1}`,
      lastMessage: '',
      timestamp: new Date().toLocaleString(),
      messages: [],
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setInput('');
  };

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
    setInput('');
  };

  const handleRenameChat = (id: string, newTitle: string) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === id) {
        return {
          ...conv,
          title: newTitle
        };
      }
      return conv;
    }));
  };

  const handleDeleteChat = (id: string) => {
    // Create a copy of the conversations to avoid potential state conflicts
    const remainingConversations = conversations.filter(conv => conv.id !== id);
    setConversations(remainingConversations);
    
    // If the active chat is deleted, select another one or show the empty state
    if (activeConversationId === id) {
      if (remainingConversations.length > 0) {
        setActiveConversationId(remainingConversations[0].id);
      } else {
        setActiveConversationId(null);
      }
    }
  };

  const handleStarChat = (id: string, starred: boolean) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === id) {
        return {
          ...conv,
          starred
        };
      }
      return conv;
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !activeConversationId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      isUser: true,
      timestamp: new Date().toLocaleTimeString(),
    };

    setConversations(prev => prev.map(conv => {
      if (conv.id === activeConversationId) {
        return {
          ...conv,
          messages: [...conv.messages, userMessage],
          lastMessage: input.trim(),
          timestamp: new Date().toLocaleString(),
        };
      }
      return conv;
    }));

    setInput('');
    setIsLoading(true);

    try {
      // Call our Flask backend API
      const response = await queryLLM(userMessage.content, mode);
      // Handle special response types like collect_input or confirm_query
      if (response.action === "collect_input") {
        setPendingAction({
          type: "collect",
          prompt: response.prompt || "📝 Please enter the required fields.",
          operation: response.operation,
          collection: response.collection || response.table,
          fields: response.fields,
        });
        setFormValues({});
        return;
      }

      if (response.action === "confirm_query") {
        setPendingAction({
          type: "confirm",
          query: response.query,
          prompt: response.prompt
        });
        return;
      }


      
      let messageContent = '';
      let mongoQueryCode = '';
      let rawResponse = '';
      
      if (response.success || response.result || response.data) {
        const results = response.data || response.result || response;
        
        // Extract the message content
        if (typeof results === 'string') {
          messageContent = results;
        } else {
          messageContent = response.message || 'Query processed successfully';
          
          // If results is an array, format it
          if (results && Array.isArray(results)) {
            const formattedResults = results.map(item => {
              if (item.name) {
                const ingredients = item.recipeingredientparts || item.ingredients || [];
                return `\n• ${item.name} (ingredients: ${Array.isArray(ingredients) ? ingredients.join(', ') : ingredients})`;
              } else if (item.ingredient_name) {
                return `\n• ${item.ingredient_name} - ${item.energy_kcal || 0} kcal`;
              } else {
                return `\n• ${JSON.stringify(item)}`;
              }
            }).join('');
            
            messageContent += formattedResults;
          }
        }
        
        // Extract MongoDB query from response data if present
        // Check if the response contains a MongoDB query pattern
        const mongoQueryMatch = typeof results === 'string' && 
          results.match(/MongoDB query:\s*(.*?\s+find\s+.*?)(?:\n|$)/i);
        
        if (mongoQueryMatch && mongoQueryMatch[1]) {
          mongoQueryCode = mongoQueryMatch[1].trim();
        } else {
          // Fallback to a basic query based on user input
          mongoQueryCode = `db.recipes.find({ $text: { $search: "${userMessage.content}" } })`;
        }
        
        rawResponse = `Query processed: "${userMessage.content}"\n` +
          `Database operation: ${JSON.stringify(response)}\n` +
          `Found ${Array.isArray(results) ? results.length : 'N/A'} results matching criteria.`;
      } else {
        messageContent = response.message || "Sorry, I couldn't process your request.";
        rawResponse = "Error processing query";
      }
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: messageContent,
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
        sqlCode: mongoQueryCode,
        rawLlmResponse: rawResponse
      };
      
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          return {
            ...conv,
            messages: [...conv.messages, aiMessage],
          };
        }
        return conv;
      }));
    } catch (error) {
      // Handle error
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, there was an error connecting to the backend service. Please try again later.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
      };
      
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          return {
            ...conv,
            messages: [...conv.messages, errorMessage],
          };
        }
        return conv;
      }));
      
      console.error("API Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const activeConversation = conversations.find(conv => conv.id === activeConversationId);

  // Show empty state with suggestions or the active chat
  const renderContent = () => {
    if (!activeConversation) {
      return (
        <div className="flex-1 flex items-center justify-center bg-white">
          <div className="text-center">
            <h3 className="text-lg font-medium text-slate-800 mb-2">Select a conversation</h3>
            <p className="text-slate-500">Choose from existing chats or start a new one</p>
          </div>
        </div>
      );
    }

    if (activeConversation.messages.length === 0) {
      return (
        <>
          {/* Chat Header */}
          <div className="py-2 px-4 border-b border-slate-200 theme-green:border-greenTheme-softGreen">
            <h2 className="font-medium text-[#2E5339]">{activeConversation.title}</h2>
          </div>
    
          {/* Empty Chat with Suggested Prompts */}
          <div className="flex-1 overflow-y-auto p-4 bg-white theme-green:bg-greenTheme-cream">
            <div className="max-w-3xl mx-auto">
              {/* Structured Form from Backend */}
              {pendingAction?.type === "collect" && (
                      <div className="bg-yellow-50 border border-yellow-300 p-4 rounded mt-4 max-w-3xl mx-auto shadow-sm">
                        <h4 className="text-yellow-800 font-semibold mb-2">
                          📝 Provide Details for {pendingAction.operation} into <code>{pendingAction.collection}</code>
                        </h4>
                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            const inputString = pendingAction.fields.map(field => `${field}=${formValues[field] || ""}`).join(", ");
                            handleSubmit({ preventDefault: () => {} } as React.FormEvent);
                            setInput(inputString);
                            setPendingAction(null);
                          }}
                          className="space-y-3"
                        >
                          {pendingAction.fields.map((field) => (
                            <div key={field}>
                              <label className="block text-sm font-medium text-slate-700 mb-1">
                                {field.replace(/_/g, ' ').replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase()}:
                              </label>

                              <input
                                type="text"
                                className="w-full p-2 border border-slate-300 rounded focus:outline-none focus:ring"
                                value={formValues[field] || ""}
                                onChange={(e) =>
                                  setFormValues((prev) => ({
                                    ...prev,
                                    [field]: e.target.value,
                                  }))
                                }
                              />
                            </div>
                          ))}
                          <button
                            type="submit"
                            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                          >
                            Submit
                          </button>
                        </form>
                      </div>
                    )}
    
                    {/* Confirmation Prompt */}
                    {pendingAction?.type === "confirm" && (
                      <div className="bg-blue-50 border border-blue-300 p-4 rounded mt-4 max-w-3xl mx-auto shadow-sm">
                        <h4 className="text-blue-800 font-semibold mb-2">⚠️ Confirmation Required</h4>
                        <p className="text-sm text-blue-700 mb-3">{pendingAction.prompt}</p>
                        <div className="space-x-2">
                          {["yes", "no", "rewrite"].map((opt) => (
                            <button
                              key={opt}
                              onClick={() => {
                                setInput(opt);
                                handleSubmit({ preventDefault: () => {} } as React.FormEvent);
                                setPendingAction(null);
                              }}
                              className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                            >
                              {opt}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
              <div className="flex items-center justify-center mb-8 mt-12">
                <div className="mr-4">
                  <img 
                    src="/images/Logo.jpeg" 
                    alt="PlatePal Logo" 
                    className="h-36 bg-greenTheme-cream rounded-full shadow-sm p-1"
                  />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-1 text-[#2E5339]">PlatePal</h2>
                  <p className="text-lg text-[#556B5D]">Your AI Recipe & Nutrition Assistant</p>
                </div>
              </div>
    
              {!disableInput && (
                <div className="mb-6">
                  <div className="relative">
                    <button
                      onClick={() => setIsPromptDropdownOpen(!isPromptDropdownOpen)}
                      className="w-full flex items-center justify-between p-4 rounded-lg bg-greenTheme-softGreen border border-greenTheme-mutedOlive text-greenTheme-darkForest font-medium hover:shadow-md hover:bg-opacity-95 transition-all duration-200"
                    >
                      <div className="flex items-center">
                        <BoltIcon className="w-5 h-5 text-[#2E5339] mr-2" />
                        <span className="text-lg">Suggested Prompts</span>
                      </div>
                      <div className="bg-white bg-opacity-50 rounded-full p-1 transition-transform duration-200">
                        {isPromptDropdownOpen ? (
                          <ChevronUpIcon className="w-5 h-5 text-greenTheme-deepGreen" />
                        ) : (
                          <ChevronDownIcon className="w-5 h-5 text-greenTheme-deepGreen" />
                        )}
                      </div>
                    </button>
    
                    
    
                    <div className={`mt-3 pt-4 pb-3 px-3 bg-greenTheme-cream border border-greenTheme-softGreen rounded-lg shadow-lg overflow-hidden transition-all duration-300 ${isPromptDropdownOpen ? 'opacity-100 max-h-[500px]' : 'opacity-0 max-h-0 pointer-events-none'}`}>
                      <div className="flex flex-wrap gap-4 p-2">
                        {suggestedPrompts.map((item, index) => (
                          <button
                            key={index}
                            onClick={() => {
                              handlePromptClick(item.prompt);
                              setIsPromptDropdownOpen(false);
                            }}
                            onMouseEnter={() => setHoveredPrompt(item.prompt)}
                            onMouseLeave={() => setHoveredPrompt(null)}
                            className="flex-grow md:flex-grow-0 text-left px-4 py-3 m-1 rounded-full bg-greenTheme-softGreen hover:bg-greenTheme-deepGreen hover:text-white border border-greenTheme-mutedOlive transition-all duration-200 group shadow-sm hover:shadow-md hover:scale-110 transform origin-center hover:-translate-y-1 relative"
                          >
                            <h4 className="font-medium text-base text-greenTheme-darkForest group-hover:text-white transition-colors truncate">
                              {item.title}
                            </h4>
                          </button>
                        ))}
                      </div>
    
                      {/* Preview Area */}
                      <div className={`mt-4 px-4 py-3 bg-white border border-greenTheme-softGreen rounded-lg transition-all duration-200 ${hoveredPrompt ? 'opacity-100 max-h-[100px]' : 'opacity-0 max-h-0 overflow-hidden'}`}>
                        <p className="text-greenTheme-deepGreen">
                          {hoveredPrompt || ""}
                        </p>
                      </div>
    
                      <div className="px-2 pt-3">
                        <p className="text-xs text-greenTheme-mutedOlive">Click on a prompt to start a conversation</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
    
          {/* Mode Toggle */}
          <div className="flex justify-center mb-3 space-x-4">
            <button
              onClick={() => setMode("mongo")}
              className={`px-4 py-1 rounded-full border ${mode === "mongo" ? "bg-green-200 text-green-800 font-bold" : "bg-white border-gray-300"}`}
            >
              Mongo
            </button>
            <button
              onClick={() => setMode("sql")}
              className={`px-4 py-1 rounded-full border ${mode === "sql" ? "bg-blue-200 text-blue-800 font-bold" : "bg-white border-gray-300"}`}
            >
              SQL
            </button>
          </div>
    
          {/* Message Input */}
          {!disableInput && (
            <div className="border-t border-slate-200 theme-green:border-greenTheme-softGreen py-3 px-4 bg-white theme-green:bg-greenTheme-cream">
              <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                <div className="flex items-center">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask about recipes, nutrition, meal plans..."
                      className="w-full p-2 pl-3 pr-10 border border-slate-300 rounded-full focus:outline-none focus:ring-1 focus:ring-slate-400 resize-none bg-white text-slate-900 placeholder-slate-500 theme-green:bg-greenTheme-lightCream theme-green:text-greenTheme-deepGreen theme-green:border-greenTheme-softGreen theme-green:placeholder-greenTheme-mutedOlive theme-green:focus:ring-greenTheme-deepGreen theme-green:shadow-sm"
                      disabled={isLoading || !activeConversationId}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSubmit(e);
                        }
                      }}
                    />
                    <button
                      type="submit"
                      disabled={isLoading || !input.trim() || !activeConversationId}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-slate-500 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed theme-green:text-greenTheme-deepGreen theme-green:hover:text-greenTheme-darkForest theme-green:bg-greenTheme-softGreen theme-green:hover:bg-greenTheme-hoverGreen rounded-full transition-colors"
                    >
                      <PaperAirplaneIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}
        </>
      );
    }
    

    return (
      <>
        {/* Chat Header */}
        <div className="bg-white py-2 px-4 border-b border-slate-200 theme-green:bg-greenTheme-cream theme-green:border-greenTheme-softGreen">
          <h2 className="font-medium text-[#2E5339]">{activeConversation.title}</h2>
        </div>
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 bg-white theme-green:bg-greenTheme-cream">
          <div className="max-w-3xl mx-auto">
            {activeConversation.messages.map((message) => (
              <ChatMessage
                key={message.id}
                content={message.content}
                isUser={message.isUser}
                timestamp={message.timestamp}
                sqlCode={message.sqlCode}
                rawLlmResponse={message.rawLlmResponse}
                viewMode={viewMode}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 rounded-lg px-4 py-2 theme-green:bg-greenTheme-softGreen shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce theme-green:bg-greenTheme-deepGreen"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100 theme-green:bg-greenTheme-deepGreen"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200 theme-green:bg-greenTheme-deepGreen"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        {/* Mode Toggle */}
        <div className="flex justify-center mb-3 space-x-4">
          <button
            onClick={() => setMode("mongo")}
            className={`px-4 py-1 rounded-full border ${
              mode === "mongo" ? "bg-green-200 text-green-800 font-bold" : "bg-white border-gray-300"
            }`}
          >
            Mongo
          </button>
          <button
            onClick={() => setMode("sql")}
            className={`px-4 py-1 rounded-full border ${
              mode === "sql" ? "bg-blue-200 text-blue-800 font-bold" : "bg-white border-gray-300"
            }`}
          >
            SQL
          </button>
        </div>
        {/* Message Input */}
        {!disableInput && (
          <div className="border-t border-slate-200 theme-green:border-greenTheme-softGreen py-3 px-4 bg-white theme-green:bg-greenTheme-cream">
            <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
              <div className="flex items-center">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about recipes, nutrition, meal plans..."
                    className="w-full p-2 pl-3 pr-10 border border-slate-300 rounded-full focus:outline-none focus:ring-1 focus:ring-slate-400 resize-none bg-white text-slate-900 placeholder-slate-500 theme-green:bg-greenTheme-lightCream theme-green:text-greenTheme-deepGreen theme-green:border-greenTheme-softGreen theme-green:placeholder-greenTheme-mutedOlive theme-green:focus:ring-greenTheme-deepGreen theme-green:shadow-sm"
                    disabled={isLoading || !activeConversationId}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !input.trim() || !activeConversationId}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-slate-500 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed theme-green:text-greenTheme-deepGreen theme-green:hover:text-greenTheme-darkForest theme-green:bg-greenTheme-softGreen theme-green:hover:bg-greenTheme-hoverGreen rounded-full transition-colors"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}
      </>
    );
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* Chat History Sidebar - Only show if showSidebar is true */}
      {showSidebar && (
        <ChatHistory
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onNewChat={handleNewChat}
          onRenameChat={handleRenameChat}
          onDeleteChat={handleDeleteChat}
          onStarChat={handleStarChat}
        />
      )}
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderContent()}
      </div>
      {/* Global Structured Form */}
      {pendingAction?.type === "collect" && (
        <div className="bg-yellow-50 border border-yellow-300 p-4 rounded mt-4 max-w-3xl mx-auto shadow-sm">
          <h4 className="text-yellow-800 font-semibold mb-2">📝 Provide Details for {pendingAction.operation} into <code>{pendingAction.collection}</code></h4>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              console.log("🔍 Submitting structured DELETE request:", {
                operation: pendingAction.operation,
                table: pendingAction.collection,
                fields: formValues
              });
              fetch("http://localhost:5001/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  operation: pendingAction.operation,
                  table: pendingAction.collection,
                  fields: formValues,
                  mode: mode,
                  original_query: `delete ${pendingAction.collection}`  // optional trace
                })
              })
              .then(res => res.json())
              .then(response => {
                const messageContent = response.result || response.error || "Unknown result";
                const aiMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: messageContent,
                  isUser: false,
                  timestamp: new Date().toLocaleTimeString(),
                };
                setConversations(prev => prev.map(conv => {
                  if (conv.id === activeConversationId) {
                    return { ...conv, messages: [...conv.messages, aiMessage] };
                  }
                  return conv;
                }));
              })
              .catch(err => {
                console.error("Submit error:", err);
              })
              .finally(() => {
                setPendingAction(null);
                setIsLoading(false);
              });
              
            }}
            className="space-y-3"
          >
            {"fields" in pendingAction && pendingAction.fields.map((field) => (
              <div key={field}>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  {field}:
                </label>
                <input
                  type="text"
                  className="w-full p-2 border border-slate-300 rounded focus:outline-none focus:ring"
                  value={formValues[field] || ""}
                  onChange={(e) =>
                    setFormValues((prev) => ({
                      ...prev,
                      [field]: e.target.value,
                    }))
                  }
                />
              </div>
            ))}
            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Submit
            </button>
          </form>
        </div>
      )}

      {/* Confirmation Prompt */}
      {pendingAction?.type === "confirm" && (
        <div className="bg-blue-50 border border-blue-300 p-4 rounded mt-4 max-w-3xl mx-auto shadow-sm">
          <h4 className="text-blue-800 font-semibold mb-2">⚠️ Confirmation Required</h4>
          <p className="text-sm text-blue-700 mb-3">{pendingAction.prompt}</p>
          <div className="space-x-2">
            {["yes", "no", "rewrite"].map((opt) => (
              <button
                key={opt}
                onClick={() => {
                  setInput(opt);
                  handleSubmit({
                    preventDefault: () => {},
                  } as React.FormEvent);
                  setPendingAction(null);
                }}
                className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 