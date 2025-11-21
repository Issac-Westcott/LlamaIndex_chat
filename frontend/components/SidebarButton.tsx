'use client';

import { Menu } from 'lucide-react';

interface SidebarButtonProps {
  onClick: () => void;
}

export default function SidebarButton({ onClick }: SidebarButtonProps) {
  return (
    <button
      onClick={onClick}
      className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
    >
      <Menu className="w-5 h-5" />
    </button>
  );
}
