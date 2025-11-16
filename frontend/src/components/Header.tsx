import { Home, MessageSquare, History, Layers } from 'lucide-react';

type Page = 'home' | 'chat' | 'history' | 'deep' | 'contacts';

interface HeaderProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

export const Header = ({ currentPage, onNavigate }: HeaderProps) => {
  const navItems = [
    { id: 'home' as Page, label: 'Главная', icon: Home },
    { id: 'chat' as Page, label: 'Чат', icon: MessageSquare },
    { id: 'history' as Page, label: 'История', icon: History },
    { id: 'deep' as Page, label: 'Deep Query', icon: Layers },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        {/* Logo */}
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-full bg-mastercard-red" />
              <div className="w-8 h-8 rounded-full -ml-4 border border-white bg-mastercard-orange" />
            </div>
            <span className="ml-2 text-xl font-semibold text-gray-900">Mastercard</span>
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
                className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-sm transition-colors ${
                  isActive
                    ? 'border-gray-900 text-gray-900 font-medium'
                    : 'border-transparent text-gray-500 hover:border-gray-200 hover:text-gray-900'
                }`}
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
