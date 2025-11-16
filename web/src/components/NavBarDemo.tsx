import { Home, MessageSquare, GitBranch, Network, Mic } from 'lucide-react'
import { NavBar } from "@/components/ui/tubelight-navbar"

export function NavBarDemo() {
  const navItems = [
    { name: 'Hero', url: 'home', icon: Home },
    { name: 'AI SQL Assistant', url: 'ai-sql-assistant', icon: MessageSquare },
    { name: 'Deep Query', url: 'deep-query', icon: GitBranch },
    { name: 'Database Mind Map', url: 'database-mind-map', icon: Network },
    { name: 'Voice', url: 'voice', icon: Mic }
  ]

  return <NavBar items={navItems} />
}

