import React from 'react';
import { LayoutDashboard, Wallet, History, LineChart, LogOut, Settings } from 'lucide-react';
import { cn } from '../../components/Shared/GlassCard';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
    onLogout: () => void;
}

const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
    { id: 'journal', label: 'Trade Journal', icon: History },
    { id: 'analysis', label: 'Analysis', icon: LineChart },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, onLogout }) => {
    return (
        <div className="w-64 h-screen glass border-r border-white/5 flex flex-col p-4 fixed left-0 top-0">
            <div className="flex items-center gap-3 px-2 mb-10">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                    <span className="text-background font-bold text-lg">G</span>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-orange-400 bg-clip-text text-transparent">
                    AntiGravity
                </h1>
            </div>

            <nav className="flex-1 space-y-2">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={cn(
                            "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group",
                            activeTab === item.id
                                ? "bg-primary text-background font-medium"
                                : "text-gray-400 hover:bg-white/5 hover:text-white"
                        )}
                    >
                        <item.icon size={20} className={cn(
                            "transition-colors",
                            activeTab === item.id ? "text-background" : "text-gray-500 group-hover:text-primary"
                        )} />
                        {item.label}
                    </button>
                ))}
            </nav>

            <div className="space-y-2 pt-4 border-t border-white/5">
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 hover:bg-white/5 hover:text-white transition-all">
                    <Settings size={20} />
                    Settings
                </button>
                <button
                    onClick={onLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-danger hover:bg-danger/10 transition-all"
                >
                    <LogOut size={20} />
                    Logout
                </button>
            </div>
        </div>
    );
};
