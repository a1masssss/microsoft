import { useState, useEffect } from "react"
import { VercelV0Chat } from "@/components/ui/v0-ai-chat"
import { NavBarDemo } from "@/components/NavBarDemo"
import DatabaseMindMap from "@/components/mindmap/DatabaseMindMap"
import { DeepQuery } from "@/components/DeepQuery"
import { useNavigation } from "@/contexts/NavigationContext"

type DashboardTab = 'chat' | 'mindmap' | 'deepquery';

interface DashboardProps {
    activeTab?: DashboardTab;
}

export function Dashboard({ activeTab: initialTab }: DashboardProps) {
    const { currentPage } = useNavigation();
    const [activeTab, setActiveTab] = useState<DashboardTab>(initialTab || 'chat');
    const [databaseId, setDatabaseId] = useState(1);

    // Update tab based on navigation
    useEffect(() => {
        if (currentPage === 'ai-sql-assistant') {
            setActiveTab('chat');
        } else if (currentPage === 'deep-query') {
            setActiveTab('deepquery');
        } else if (currentPage === 'database-mind-map') {
            setActiveTab('mindmap');
        }
    }, [currentPage]);

    // Also update if prop changes
    useEffect(() => {
        if (initialTab) {
            setActiveTab(initialTab);
        }
    }, [initialTab]);

    return (
        <div className="h-screen flex flex-col bg-black">
            <NavBarDemo />

            {/* Tab Content */}
            <div className="flex-1 overflow-hidden">
                {activeTab === 'chat' && <VercelV0Chat />}
                {activeTab === 'deepquery' && <DeepQuery databaseId={databaseId} />}
                {activeTab === 'mindmap' && (
                    <div className="h-full flex flex-col bg-gray-50">
                        {/* Mind Map Header */}
                        <div className="bg-white border-b border-gray-200 px-6 py-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-xl font-bold text-gray-900">Database Mind Map</h2>
                                    <p className="text-sm text-gray-600 mt-1">
                                        Visualize your database schema as an interactive mind map
                                    </p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <label className="text-sm font-medium text-gray-700">
                                        Database ID:
                                    </label>
                                    <input
                                        type="number"
                                        value={databaseId}
                                        onChange={(e) => setDatabaseId(parseInt(e.target.value) || 1)}
                                        className="w-20 px-3 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                                        min="1"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Mind Map Component */}
                        <div className="flex-1 overflow-hidden">
                            <DatabaseMindMap databaseId={databaseId} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

