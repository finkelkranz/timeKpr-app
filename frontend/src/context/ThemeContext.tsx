import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark' | 'system';
  isDarkMode: boolean;
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [storedTheme, setStoredTheme] = useState<'light' | 'dark' | 'system'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
      return saved || 'system';
    }
    return 'system';
  });

  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
      if (saved === 'light') return false;
      if (saved === 'dark') return true;
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDarkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemChange = (e: MediaQueryListEvent) => {
      if (storedTheme === 'system') {
        setIsDarkMode(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleSystemChange);
    return () => mediaQuery.removeEventListener('change', handleSystemChange);
  }, [storedTheme]);

  const computeIsDark = useCallback((theme: 'light' | 'dark' | 'system'): boolean => {
    if (theme === 'light') return false;
    if (theme === 'dark') return true;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }, []);

  const toggleTheme = useCallback(() => {
    const newTheme = isDarkMode ? 'light' : 'dark';
    localStorage.setItem('theme', newTheme);
    setStoredTheme(newTheme);
    setIsDarkMode(!isDarkMode);
  }, [isDarkMode]);

  const setTheme = useCallback((theme: 'light' | 'dark' | 'system') => {
    localStorage.setItem('theme', theme);
    setStoredTheme(theme);
    setIsDarkMode(computeIsDark(theme));
  }, [computeIsDark]);

  return (
    <ThemeContext.Provider value={{ theme: storedTheme, isDarkMode, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
