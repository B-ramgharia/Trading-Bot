import type React from 'react';
import { Bell, Search, User } from 'lucide-react';



export const Navbar: React.FC = () => {
    return (
        <nav className="h-16 flex items-center justify-between px-8 bg-background/50 backdrop-blur-md border-b border-white/5 sticky top-0 z-10 ml-64">
            <div className="flex items-center gap-4 w-96">
                <div className="relative w-full group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-primary transition-colors" size={18} />
                    <input
                        type="text"
                        placeholder="Search symbols..."
                        className="w-full bg-white/5 border border-white/5 rounded-lg py-2 pl-10 pr-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-sm"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative text-gray-400 hover:text-white transition-colors">
                    <Bell size={20} />
                    <span className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full border-2 border-background"></span>
                </button>

                <div className="h-8 w-[1px] bg-white/10"></div>

                <div className="flex items-center gap-3 cursor-pointer group">
                    <div className="text-right">
                        <p className="text-sm font-medium text-white group-hover:text-primary transition-colors">Trader One</p>
                        <p className="text-xs text-gray-500">Verified Account</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-secondary border border-white/10 flex items-center justify-center overflow-hidden group-hover:border-primary/50 transition-all">
                        <User size={20} className="text-gray-400 group-hover:text-primary transition-colors" />
                    </div>
                </div>
            </div>
        </nav>
    );
};
