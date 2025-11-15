import { Home, Briefcase, FileText, LayoutDashboard, Mic } from 'lucide-react'
import { NavBar } from "@/components/ui/tubelight-navbar"

export function NavBarDemo() {
  const navItems = [
    { name: 'Hero', url: 'home', icon: Home },
    { name: 'Dashboard', url: 'dashboard', icon: LayoutDashboard },
    { name: 'Voice', url: 'voice', icon: Mic },
    { name: 'Projects', url: 'projects', icon: Briefcase },
    { name: 'Resume', url: 'resume', icon: FileText }
  ]

  return <NavBar items={navItems} />
}

