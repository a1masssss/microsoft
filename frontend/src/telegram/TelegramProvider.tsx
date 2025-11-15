/**
 * Telegram context provider
 */
import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { createContext, useContext, type ReactNode } from 'react';
import { useTelegram } from './useTelegram';
import type { WebApp, TelegramUser } from './types';

interface TelegramContextType {
  webApp: WebApp | null;
  user: TelegramUser | null;
  initData: string;
  colorScheme: 'light' | 'dark';
  themeParams: Record<string, string | undefined>;
}

const TelegramContext = createContext<TelegramContextType | undefined>(undefined);

export const TelegramProvider = ({ children }: { children: ReactNode }) => {
  const telegram = useTelegram();

  return (
    <TelegramContext.Provider value={telegram}>
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegramContext = () => {
  const context = useContext(TelegramContext);
  if (!context) {
    throw new Error('useTelegramContext must be used within TelegramProvider');
  }
  return context;
};
