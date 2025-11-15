"use client"

import React, { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { type LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { useNavigation } from "@/contexts/NavigationContext"

interface NavItem {
  name: string
  url: string
  icon: LucideIcon
}

interface NavBarProps {
  items: NavItem[]
  className?: string
}

export function NavBar({ items, className }: NavBarProps) {
  const { navigateTo, currentPage } = useNavigation()
  const [activeTab, setActiveTab] = useState(items[0].name)
  const [isMobile, setIsMobile] = useState(false)

  // Update active tab when page changes
  useEffect(() => {
    const activeItem = items.find(item => item.url === currentPage)
    if (activeItem) {
      setActiveTab(activeItem.name)
    }
  }, [currentPage, items])

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  return (
    <div
      className={cn(
        "fixed top-6 left-1/2 -translate-x-1/2 z-50",
        className,
      )}
    >
      <div className="flex items-center gap-2 bg-white/80 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-800 backdrop-blur-xl py-2 px-2 rounded-full shadow-xl">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.name

          return (
            <a
              key={item.name}
              href={`#${item.url}`}
              onClick={(e) => {
                e.preventDefault()
                setActiveTab(item.name)
                navigateTo(item.url as any)
              }}
              className={cn(
                "relative cursor-pointer text-sm font-semibold px-5 py-2.5 rounded-full transition-colors",
                "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100",
                isActive && "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
              )}
            >
              <span className="hidden md:inline">{item.name}</span>
              <span className="md:hidden">
                <Icon size={18} strokeWidth={2.5} />
              </span>
              {isActive && (
                <motion.div
                  layoutId="lamp"
                  className="absolute inset-0 w-full rounded-full -z-10"
                  initial={false}
                  transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30,
                  }}
                >
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-10 h-1.5 bg-blue-500 dark:bg-blue-400 rounded-t-full">
                    <div className="absolute w-16 h-8 bg-blue-500/30 dark:bg-blue-400/30 rounded-full blur-lg -top-3 -left-3" />
                    <div className="absolute w-12 h-6 bg-blue-500/40 dark:bg-blue-400/40 rounded-full blur-md -top-2" />
                    <div className="absolute w-6 h-4 bg-blue-500/50 dark:bg-blue-400/50 rounded-full blur-sm top-0 left-2" />
                  </div>
                </motion.div>
              )}
            </a>
          )
        })}
      </div>
    </div>
  )
}

