import { useState, useEffect } from 'react';
import { useTelegramContext } from './telegram/TelegramProvider';
import { telegramApi } from './api/telegram';
import type { QueryResponse, HistoryItem } from './api/telegram';
import './App.css';

function App() {
  const { user, initData, colorScheme, themeParams } = useTelegramContext();
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load history on mount
  useEffect(() => {
    if (initData) {
      loadHistory();
    }
  }, [initData]);

  const loadHistory = async () => {
    try {
      const data = await telegramApi.getHistory(initData, 5);
      setHistory(data);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !initData) return;

    setLoading(true);
    setError(null);

    try {
      const result = await telegramApi.sendQuery(initData, query);
      setResponse(result);
      setQuery('');
      loadHistory();
    } catch (err) {
      setError('Ошибка при отправке запроса');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Apply Telegram theme
  const appStyle = {
    backgroundColor: themeParams.bg_color || (colorScheme === 'dark' ? '#1a1a1a' : '#ffffff'),
    color: themeParams.text_color || (colorScheme === 'dark' ? '#ffffff' : '#000000'),
    minHeight: '100vh',
    padding: '20px',
  };

  const buttonStyle = {
    backgroundColor: themeParams.button_color || '#0088cc',
    color: themeParams.button_text_color || '#ffffff',
  };

  return (
    <div style={appStyle}>
      <div className="container">
        <h1>Telegram Mini App</h1>

        {user && (
          <div className="user-info">
            <p>Привет, {user.first_name || user.username}!</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="query-form">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Введите ваш запрос..."
            rows={3}
            disabled={loading}
          />
          <button
            type="submit"
            style={buttonStyle}
            disabled={loading || !query.trim()}
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {response && (
          <div className="response">
            <h3>Ответ:</h3>
            <p>{response.response}</p>
          </div>
        )}

        {history.length > 0 && (
          <div className="history">
            <h3>История запросов:</h3>
            {history.map((item) => (
              <div key={item.id} className="history-item">
                <strong>Q:</strong> {item.query}
                <br />
                <strong>A:</strong> {item.response}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
