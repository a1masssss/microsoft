import { useState, useEffect } from "react"
import { VercelV0Chat } from "@/components/ui/v0-ai-chat"
import { NavBarDemo } from "@/components/NavBarDemo"
import DatabaseMindMap from "@/components/mindmap/DatabaseMindMap"
import { DeepQuery } from "@/components/DeepQuery"
import { useNavigation } from "@/contexts/NavigationContext"

type DashboardTab = 'chat' | 'mindmap' | 'deepquery';

export function Dashboard() {
    const { currentPage } = useNavigation();
    const [activeTab, setActiveTab] = useState<DashboardTab>('chat');
    const [databaseId, setDatabaseId] = useState(1);

    // Switch to mindmap tab when navigated from Mind Map navbar item
    useEffect(() => {
        if (currentPage === 'mindmap') {
            setActiveTab('mindmap');
        } else if (currentPage === 'dashboard') {
            setActiveTab('chat');
        }
    }, [currentPage]);

    return (
        <div className="h-screen flex flex-col bg-black">
            <NavBarDemo />

            {/* Tab Navigation */}
            <div className="bg-black border-b border-gray-800">
                <div className="flex gap-1 px-4">
                    <button
                        onClick={() => setActiveTab('chat')}
                        className={`px-6 py-3 text-sm font-medium transition-colors relative ${
                            activeTab === 'chat'
                                ? 'text-white'
                                : 'text-gray-400 hover:text-gray-300'
                        }`}
                    >
                        AI SQL Assistant
                        {activeTab === 'chat' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('deepquery')}
                        className={`px-6 py-3 text-sm font-medium transition-colors relative ${
                            activeTab === 'deepquery'
                                ? 'text-white'
                                : 'text-gray-400 hover:text-gray-300'
                        }`}
                    >
                        Deep Query
                        {activeTab === 'deepquery' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('mindmap')}
                        className={`px-6 py-3 text-sm font-medium transition-colors relative ${
                            activeTab === 'mindmap'
                                ? 'text-white'
                                : 'text-gray-400 hover:text-gray-300'
                        }`}
                    >
                        Database Mind Map
                        {activeTab === 'mindmap' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500" />
                        )}
                    </button>
                </div>
            </div>

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

