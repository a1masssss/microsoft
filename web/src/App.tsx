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
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'voice' && <Voice />}
      {currentPage === 'about' && <Dashboard />}
      {currentPage === 'projects' && <Dashboard />}
      {currentPage === 'resume' && <Dashboard />}
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
