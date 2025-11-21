'use client';

import { AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';
import { Message } from '@/app/page';

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-6">
      <AnimatePresence>
        {messages.map((message, index) => (
          <MessageBubble key={message.id} message={message} index={index} />
        ))}
      </AnimatePresence>
    </div>
  );
}
