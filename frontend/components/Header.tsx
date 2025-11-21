'use client';

import { Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';
import SidebarButton from './SidebarButton';

interface HeaderProps {
  onClear: () => void;
  hasMessages: boolean;
  onMenuClick?: () => void;
}

export default function Header({
  onClear,
  hasMessages,
  onMenuClick,
}: HeaderProps) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900"
    >
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onMenuClick && <SidebarButton onClick={onMenuClick} />}
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            LlamaIndex Chat
          </h1>
        </div>
        {hasMessages && (
          <button
            onClick={onClear}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Trash2 className="w-4 h-4" />
            <span>清除对话</span>
          </button>
        )}
      </div>
    </motion.header>
  );
}
