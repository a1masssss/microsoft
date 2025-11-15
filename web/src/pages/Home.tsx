import { HeroScrollDemo } from '@/components/HeroScrollDemo'
import { NavBarDemo } from '@/components/NavBarDemo'

export function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-black">
      <NavBarDemo />
      <HeroScrollDemo />
    </div>
  )
}

