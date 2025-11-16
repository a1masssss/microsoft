import { useState } from 'react';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { ChatPage } from './pages/ChatPage';
import { HistoryPage } from './pages/HistoryPage';
import { DeepQueryPage } from './pages/DeepQueryPage';
import { useTelegram } from './hooks/useTelegram';

type Page = 'home' | 'chat' | 'history' | 'deep' | 'contacts';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const { isReady } = useTelegram();

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 rounded-full bg-gray-900 animate-pulse" />
            <div className="w-12 h-12 rounded-full bg-gray-600 -ml-6 animate-pulse" />
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
      case 'deep':
        return <DeepQueryPage />;
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
