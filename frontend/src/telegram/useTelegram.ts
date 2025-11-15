/**
 * Hook for accessing Telegram WebApp API
 */
import { useEffect, useState } from 'react';
import type { WebApp, TelegramUser } from './types';

export const useTelegram = () => {
  const [webApp, setWebApp] = useState<WebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);

  useEffect(() => {
    const app = window.Telegram?.WebApp;

    if (app) {
      app.ready();
      app.expand();
      setWebApp(app);
      setUser(app.initDataUnsafe.user || null);
    }
  }, []);

  return {
    webApp,
    user,
    initData: webApp?.initData || '',
    colorScheme: webApp?.colorScheme || 'light',
    themeParams: webApp?.themeParams || {},
  };
};
