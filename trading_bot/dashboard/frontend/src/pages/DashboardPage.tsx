import React, { useState } from 'react';
import { Sidebar } from '../components/Layout/Sidebar';
import { Navbar } from '../components/Layout/Navbar';
import { StatsCard } from '../components/Dashboard/StatsCard';
import { TradingTerminal } from '../components/Dashboard/TradingTerminal';
import { PriceChart } from '../components/Dashboard/PriceChart';
import { Wallet, TrendingUp, Activity, BarChart3 } from 'lucide-react';

import { motion } from 'framer-motion';

const DashboardPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState('dashboard');

    return (
        <div className="min-h-screen bg-background">
            <Sidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                onLogout={() => console.log('Logout')}
            />
            <div className="flex flex-col">
                <Navbar />
                <main className="ml-64 p-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex flex-col gap-8"
                    >
                        {/* Page Header */}
                        <div>
                            <h1 className="text-3xl font-bold text-white">Trading Overview</h1>
                            <p className="text-gray-500 mt-1">Monitor your performance and manage assets in real-time.</p>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <StatsCard
                                label="Wallet Balance"
                                value="$42,500.00"
                                change={12.5}
                                icon={Wallet}
                                iconColor="text-primary"
                            />
                            <StatsCard
                                label="Total Profit"
                                value="+$3,240.15"
                                change={5.2}
                                icon={TrendingUp}
                                iconColor="text-success"
                            />
                            <StatsCard
                                label="Active Margin"
                                value="$12,000.00"
                                icon={Activity}
                                iconColor="text-blue-400"
                            />
                            <StatsCard
                                label="Win Rate"
                                value="68%"
                                change={-1.2}
                                icon={BarChart3}
                                iconColor="text-purple-400"
                            />
                        </div>

                        {/* Main Dashboard Layout */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            <div className="lg:col-span-2 flex flex-col gap-8">
                                <div className="glass rounded-xl overflow-hidden border border-white/5 bg-black/20">
                                    <PriceChart />
                                </div>

                                {/* Open Positions Placeholder */}
                                <div className="glass rounded-xl p-6 border border-white/5 min-h-[300px]">
                                    <h3 className="text-lg font-bold text-white mb-6">Active Positions</h3>
                                    <div className="flex items-center justify-center h-48 text-gray-600 italic">
                                        No active positions found
                                    </div>
                                </div>
                            </div>

                            <div className="lg:col-span-1">
                                <TradingTerminal />
                            </div>
                        </div>
                    </motion.div>
                </main>
            </div>
        </div>
    );
};

export default DashboardPage;
