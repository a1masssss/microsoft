import { Home, MessageSquare, History, Mail } from 'lucide-react';

type Page = 'home' | 'chat' | 'history' | 'contacts';

interface HeaderProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

export const Header = ({ currentPage, onNavigate }: HeaderProps) => {
  const navItems = [
    { id: 'home' as Page, label: 'Главная', icon: Home },
    { id: 'chat' as Page, label: 'Chat', icon: MessageSquare },
    { id: 'history' as Page, label: 'История', icon: History },
    { id: 'contacts' as Page, label: 'Контакты', icon: Mail },
  ];

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        {/* Logo */}
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-full bg-mastercard-red" />
              <div className="w-8 h-8 rounded-full bg-mastercard-orange -ml-4" />
            </div>
            <span className="text-xl font-bold text-gray-900 ml-2">Mastercard</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex gap-1 -mb-px overflow-x-auto scrollbar-hide">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap
                  ${isActive
                    ? 'border-mastercard-orange text-mastercard-orange font-medium'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
