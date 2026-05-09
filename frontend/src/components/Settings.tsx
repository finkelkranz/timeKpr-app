import { useEffect, useState } from 'react';
import { useTheme } from '../context/ThemeContext';

interface SettingsProps {
  onClose: () => void;
}

function Settings({ onClose }: SettingsProps) {
  const { theme, setTheme } = useTheme();
  const [activeTheme, setActiveTheme] = useState<'light' | 'dark' | 'system'>(theme);

  // Sync activeTheme with context theme
  useEffect(() => {
    setActiveTheme(theme);
  }, [theme]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape as any);
    return () => window.removeEventListener('keydown', handleEscape as any);
  }, [onClose]);

  // Close on backdrop click
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
  };

  const themeOptions = [
    { id: 'light' as const, label: 'Light', icon: '☀️' },
    { id: 'dark' as const, label: 'Dark', icon: '🌙' },
    { id: 'system' as const, label: 'System', icon: '💻' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={handleBackdropClick}>
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800 z-10">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-2 rounded-full transition-colors"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Theme Section */}
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Appearance
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Choose how timekpr Admin looks
            </p>

            <div className="grid grid-cols-3 gap-2">
              {themeOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => handleThemeChange(option.id)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-all duration-200
                    ${activeTheme === option.id 
                      ? 'bg-blue-600 text-white shadow-lg' 
                      : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                >
                  <span className="text-2xl">{option.icon}</span>
                  <span className="text-sm font-medium">{option.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Info Section */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4">
            <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-200 mb-2">
              About
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              timekpr Admin v1.0.0
            </p>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              Manage screen time for your family
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
