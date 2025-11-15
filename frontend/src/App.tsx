import { useState } from 'react';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { ChatPage } from './pages/ChatPage';
import { HistoryPage } from './pages/HistoryPage';
import { ContactsPage } from './pages/ContactsPage';
import { useTelegram } from './hooks/useTelegram';

type Page = 'home' | 'chat' | 'history' | 'contacts';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const { isReady } = useTelegram();

  // Wait for Telegram to be ready
  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 rounded-full bg-mastercard-red animate-pulse" />
            <div className="w-12 h-12 rounded-full bg-mastercard-orange -ml-6 animate-pulse" />
          </div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'chat':
        return <ChatPage />;
      case 'history':
        return <HistoryPage />;
      case 'contacts':
        return <ContactsPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentPage={currentPage} onNavigate={setCurrentPage} />
      {renderPage()}
    </div>
  );
}

export default App;
