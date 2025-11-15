import { VercelV0Chat } from "@/components/ui/v0-ai-chat"
import { NavBarDemo } from "@/components/NavBarDemo"

export function Dashboard() {
    return (
        <div className="min-h-screen bg-white dark:bg-black">
            <NavBarDemo />
            <div className="pt-32">
                <VercelV0Chat />
            </div>
        </div>
    )
}

