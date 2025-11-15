import { VercelV0Chat } from "@/components/ui/v0-ai-chat"
import { NavBarDemo } from "@/components/NavBarDemo"

export function Dashboard() {
    return (
        <div className="h-screen flex flex-col bg-black">
            <NavBarDemo />
            <div className="flex-1 overflow-hidden">
                <VercelV0Chat />
            </div>
        </div>
    )
}

