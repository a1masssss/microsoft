import './App.css'
import { NavigationProvider, useNavigation } from './contexts/NavigationContext'
import { Home } from './pages/Home'
import { Dashboard } from './pages/Dashboard'
import { Voice } from './pages/Voice'

function AppContent() {
  const { currentPage } = useNavigation()

  return (
    <>
      {currentPage === 'home' && <Home />}
      {currentPage === 'ai-sql-assistant' && <Dashboard activeTab="chat" />}
      {currentPage === 'deep-query' && <Dashboard activeTab="deepquery" />}
      {currentPage === 'database-mind-map' && <Dashboard activeTab="mindmap" />}
      {currentPage === 'voice' && <Voice />}
    </>
  )
}

function App() {
  return (
    <NavigationProvider>
      <AppContent />
    </NavigationProvider>
  )
}

export default App
