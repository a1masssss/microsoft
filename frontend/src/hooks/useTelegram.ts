import { useEffect, useState } from 'react';
import WebApp from '@twa-dev/sdk';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
}

export const useTelegram = () => {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize Telegram Web App
    WebApp.ready();
    WebApp.expand();

    // Get user data
    if (WebApp.initDataUnsafe?.user) {
      setUser(WebApp.initDataUnsafe.user as TelegramUser);
    }

    setIsReady(true);

    // Apply Telegram theme
    document.documentElement.style.setProperty(
      '--tg-theme-bg-color',
      WebApp.themeParams.bg_color || '#ffffff'
    );
    document.documentElement.style.setProperty(
      '--tg-theme-text-color',
      WebApp.themeParams.text_color || '#000000'
    );
    document.documentElement.style.setProperty(
      '--tg-theme-hint-color',
      WebApp.themeParams.hint_color || '#999999'
    );
    document.documentElement.style.setProperty(
      '--tg-theme-button-color',
      WebApp.themeParams.button_color || '#3390ec'
    );
    document.documentElement.style.setProperty(
      '--tg-theme-button-text-color',
      WebApp.themeParams.button_text_color || '#ffffff'
    );
  }, []);

  const showAlert = (message: string) => {
    WebApp.showAlert(message);
  };

  const showConfirm = (message: string) => {
    return new Promise<boolean>((resolve) => {
      WebApp.showConfirm(message, resolve);
    });
  };

  const hapticFeedback = (type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
    switch (type) {
      case 'light':
      case 'medium':
      case 'heavy':
      case 'rigid':
      case 'soft':
        WebApp.HapticFeedback.impactOccurred(type);
        break;
    }
  };

  return {
    user,
    isReady,
    initData: WebApp.initData,
    colorScheme: WebApp.colorScheme,
    themeParams: WebApp.themeParams,
    showAlert,
    showConfirm,
    hapticFeedback,
    WebApp,
  };
};
