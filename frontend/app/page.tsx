'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageList from '@/components/MessageList';
import InputArea from '@/components/InputArea';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import SidebarButton from '@/components/SidebarButton';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thinking?: string;
  timestamp: Date;
}

export interface Conversation {
  session_id: string;
  title: string;
  message_count: number;
  last_updated: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/conversations');
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error('加载会话列表失败:', error);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setSessionId(null);
    setSidebarOpen(false);
    loadConversations();
  };

  const handleSelectConversation = async (selectedSessionId: string) => {
    try {
      setSessionId(selectedSessionId);
      setSidebarOpen(false);
      setIsLoading(true);

      // 加载该会话的历史消息
      const response = await fetch(`/api/conversation/${selectedSessionId}`);
      if (!response.ok) {
        throw new Error('加载历史消息失败');
      }

      const data = await response.json();

      // 将历史消息转换为前端格式
      const historyMessages: Message[] = data.messages.map(
        (msg: any, index: number) => ({
          id: `${selectedSessionId}-${index}-${Date.now()}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content || '',
          thinking: msg.thinking || '',
          timestamp: new Date(), // 可以后续从后端返回时间戳
        })
      );

      setMessages(historyMessages);

      // 滚动到底部
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    } catch (error) {
      console.error('加载历史消息失败:', error);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (sessionIdToDelete: string) => {
    try {
      await fetch('/api/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionIdToDelete,
        }),
      });
      if (sessionIdToDelete === sessionId) {
        handleNewConversation();
      } else {
        loadConversations();
      }
    } catch (error) {
      console.error('删除会话失败:', error);
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
      console.log('用户停止了响应');
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // 如果已有正在进行的请求，先停止
    if (abortControllerRef.current) {
      handleStop();
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageInput = input.trim();
    setInput('');
    setIsLoading(true);

    // 创建助手消息占位符
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      thinking: '',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    // 创建 AbortController 用于取消请求
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageInput,
          session_id: sessionId,
          stream: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentSessionId = sessionId;

      if (!reader) {
        throw new Error('无法读取响应流');
      }

      let receivedDone = false;
      let timeoutId: NodeJS.Timeout | null = null;

      // 设置超时（5分钟）
      timeoutId = setTimeout(
        () => {
          console.warn('请求超时，自动停止');
          handleStop();
        },
        5 * 60 * 1000
      );

      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            // 流结束
            if (timeoutId) {
              clearTimeout(timeoutId);
              timeoutId = null;
            }
            if (!receivedDone) {
              // 如果没有收到 done 信号，手动结束
              console.log('流结束，但没有收到 done 信号');
              setIsLoading(false);
              loadConversations();
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim() === '') continue; // 跳过空行

            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue; // 跳过空数据

                const data = JSON.parse(jsonStr);

                if (data.session_id && !currentSessionId) {
                  currentSessionId = data.session_id;
                  setSessionId(data.session_id);
                  loadConversations();
                }

                if (data.type === 'thinking' && data.content) {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? {
                            ...msg,
                            thinking: (msg.thinking || '') + data.content,
                          }
                        : msg
                    )
                  );
                }

                if (data.type === 'content' && data.content) {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: msg.content + data.content }
                        : msg
                    )
                  );
                }

                if (data.type === 'done') {
                  receivedDone = true;
                  if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                  }
                  setIsLoading(false);
                  abortControllerRef.current = null;
                  loadConversations();
                  return;
                }

                if (data.type === 'error' || data.error) {
                  const errorMsg = data.error || data.message || '发生错误';
                  console.error('API 错误:', errorMsg);
                  if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                  }
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? {
                            ...msg,
                            content:
                              msg.content || `抱歉，发生了错误：${errorMsg}`,
                          }
                        : msg
                    )
                  );
                  setIsLoading(false);
                  abortControllerRef.current = null;
                  return;
                }
              } catch (e) {
                console.error('解析 SSE 数据错误:', e, '原始数据:', line);
              }
            }
          }
        }
      } catch (abortError: any) {
        // 请求被取消
        if (abortError.name === 'AbortError') {
          console.log('请求已被用户取消');
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }
          setIsLoading(false);
          abortControllerRef.current = null;
          return;
        }
        throw abortError;
      } finally {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      }
    } catch (error: any) {
      console.error('Error:', error);
      // 如果是取消错误，不显示错误消息
      if (error.name === 'AbortError') {
        setIsLoading(false);
        abortControllerRef.current = null;
        return;
      }
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content:
                  msg.content ||
                  `抱歉，发生了错误：${error instanceof Error ? error.message : '未知错误'}`,
              }
            : msg
        )
      );
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleClear = async () => {
    if (!sessionId) return;

    try {
      await fetch('/api/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
        }),
      });

      setMessages([]);
      setSessionId(null);
      loadConversations();
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900">
      {/* 侧边栏 */}
      <div className="hidden lg:block w-64 flex-shrink-0 border-r border-gray-200 dark:border-gray-800">
        <Sidebar
          isOpen={true}
          onClose={() => {}}
          conversations={conversations}
          currentSessionId={sessionId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      {/* 移动端侧边栏 */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        currentSessionId={sessionId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onClear={handleClear}
          hasMessages={messages.length > 0}
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        />

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-8">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                    LlamaIndex Chat
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 text-lg">
                    开始与 AI 助手对话
                  </p>
                </motion.div>
              </div>
            ) : (
              <MessageList messages={messages} />
            )}
            {isLoading && (
              <div className="flex items-center justify-between gap-4 text-gray-500 dark:text-gray-400 mt-4 px-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>AI 正在思考...</span>
                </div>
                <button
                  onClick={handleStop}
                  className="px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                  停止生成
                </button>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <InputArea
          input={input}
          setInput={setInput}
          onSend={handleSend}
          onStop={handleStop}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
