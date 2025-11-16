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
