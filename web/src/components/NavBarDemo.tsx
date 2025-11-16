import { Home, Briefcase, FileText, LayoutDashboard, Mic, Network } from 'lucide-react'
import { NavBar } from "@/components/ui/tubelight-navbar"

export function NavBarDemo() {
  const navItems = [
    { name: 'Hero', url: 'home', icon: Home },
    { name: 'Dashboard', url: 'dashboard', icon: LayoutDashboard },
    { name: 'Voice', url: 'voice', icon: Mic },
    { name: 'Mind Map', url: 'mindmap', icon: Network },
    { name: 'Projects', url: 'projects', icon: Briefcase },
    { name: 'Resume', url: 'resume', icon: FileText }
  ]

  return <NavBar items={navItems} />
}

