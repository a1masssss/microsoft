'use client'

import { SplineScene } from "@/components/ui/spline";
import { Card } from "@/components/ui/card"
import { SpotlightAceternity } from "@/components/ui/spotlight-aceternity"
import { NavBarDemo } from "@/components/NavBarDemo"

export function Voice() {
  return (
    <div className="min-h-screen bg-black">
      <NavBarDemo />
      
      <div className="pt-32 px-4 pb-20">
        <Card className="w-full h-[600px] bg-black/[0.96] relative overflow-hidden border-zinc-800">
          <SpotlightAceternity
            className="-top-40 left-0 md:left-60 md:-top-20"
            fill="white"
          />
          
          <div className="flex flex-col md:flex-row h-full">
            {/* Left content */}
            <div className="flex-1 p-8 relative z-10 flex flex-col justify-center">
              <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400">
                Interactive 3D
              </h1>
              <p className="mt-4 text-neutral-300 max-w-lg text-lg">
                Bring your UI to life with beautiful 3D scenes. Create immersive experiences 
                that capture attention and enhance your design.
              </p>
              <div className="mt-8 flex gap-4">
                <button className="px-6 py-3 bg-white text-black rounded-lg font-semibold hover:bg-neutral-200 transition-colors">
                  Get Started
                </button>
                <button className="px-6 py-3 bg-transparent border border-neutral-700 text-white rounded-lg font-semibold hover:bg-neutral-900 transition-colors">
                  Learn More
                </button>
              </div>
            </div>

            {/* Right content - 3D Scene */}
            <div className="flex-1 relative">
              <SplineScene 
                scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                className="w-full h-full"
              />
            </div>
          </div>
        </Card>

        {/* Additional content section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-6 bg-zinc-900/50 border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-2">Real-time 3D</h3>
            <p className="text-neutral-400">
              Interactive 3D models that respond to user interaction in real-time.
            </p>
          </Card>
          
          <Card className="p-6 bg-zinc-900/50 border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-2">Easy Integration</h3>
            <p className="text-neutral-400">
              Simple to implement with just a few lines of code.
            </p>
          </Card>
          
          <Card className="p-6 bg-zinc-900/50 border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-2">Performance</h3>
            <p className="text-neutral-400">
              Optimized for web with lazy loading and efficient rendering.
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}

