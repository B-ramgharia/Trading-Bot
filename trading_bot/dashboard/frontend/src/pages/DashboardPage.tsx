import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from '../components/Layout/Sidebar';
import { Navbar } from '../components/Layout/Navbar';
import { StatsCard } from '../components/Dashboard/StatsCard';
import { TradingTerminal } from '../components/Dashboard/TradingTerminal';
import { PriceChart } from '../components/Dashboard/PriceChart';
import { PositionsTable } from '../components/Dashboard/PositionsTable';
import type { Position } from '../components/Dashboard/PositionsTable';
import { Wallet, TrendingUp, Activity, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const INITIAL_POSITIONS: Position[] = [
    {
        id: '1',
        symbol: 'BTCUSDT',
        side: 'BUY',
        size: 0.25,
        entryPrice: 64200.50,
        markPrice: 66134.90,
        pnl: 483.60,
        pnlPercent: 12.55,
    },
    {
        id: '2',
        symbol: 'ETHUSDT',
        side: 'SELL',
        size: 2.5,
        entryPrice: 3500.20,
        markPrice: 3420.15,
        pnl: 200.12,
        pnlPercent: 5.72,
    }
];

const DashboardPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [positions, setPositions] = useState<Position[]>(INITIAL_POSITIONS);
    const [balance, setBalance] = useState(42500.00);
    const [totalProfit, setTotalProfit] = useState(3240.15);

    // Simulated Price Ticking
    useEffect(() => {
        const interval = setInterval(() => {
            setPositions(prev => prev.map(pos => {
                const jitter = (Math.random() - 0.5) * 10;
                const newMarkPrice = pos.markPrice + jitter;
                const pnlDiff = pos.side === 'BUY'
                    ? (newMarkPrice - pos.markPrice) * pos.size
                    : (pos.markPrice - newMarkPrice) * pos.size;

                return {
                    ...pos,
                    markPrice: newMarkPrice,
                    pnl: pos.pnl + pnlDiff,
                    pnlPercent: ((newMarkPrice - pos.entryPrice) / pos.entryPrice) * 100 * (pos.side === 'BUY' ? 1 : -1)
                };
            }));

            // Randomly update balance slightly to simulate PnL propagation
            setBalance(prev => prev + (Math.random() - 0.5) * 2);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const handleClosePosition = useCallback((id: string) => {
        const pos = positions.find(p => p.id === id);
        if (pos) {
            setPositions(prev => prev.filter(p => p.id !== id));
            setBalance(prev => prev + pos.pnl);
            setTotalProfit(prev => prev + pos.pnl);
            toast.success(`Position ${pos.symbol} closed successfully`, {
                description: `Realized PnL: $${pos.pnl.toFixed(2)}`,
            });
        }
    }, [positions]);

    const handleNewOrder = useCallback((data: any) => {
        const newPos: Position = {
            id: Math.random().toString(36).substr(2, 9),
            symbol: data.symbol || 'BTCUSDT',
            side: data.side,
            size: data.quantity,
            entryPrice: 66134.90, // Current mid-price
            markPrice: 66134.90,
            pnl: 0,
            pnlPercent: 0,
        };
        setPositions(prev => [newPos, ...prev]);
        toast.info(`New ${data.side} order executed`, {
            description: `${data.quantity} ${data.symbol} @ ${newPos.entryPrice}`,
        });
    }, []);

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
                        <div className="flex items-center justify-between">
                            <div>
                                <h1 className="text-3xl font-bold text-white">Trading Overview</h1>
                                <p className="text-gray-500 mt-1">Monitor your performance and manage assets in real-time.</p>
                            </div>
                            <div className="flex items-center gap-2 px-4 py-2 bg-success/10 border border-success/20 rounded-full">
                                <Activity className="w-4 h-4 text-success animate-pulse" />
                                <span className="text-xs font-bold text-success uppercase tracking-widest">Network Stable</span>
                            </div>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <StatsCard
                                label="Wallet Balance"
                                value={`$${balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                                change={12.5}
                                icon={Wallet}
                                iconColor="text-primary"
                            />
                            <StatsCard
                                label="Total Profit"
                                value={`${totalProfit >= 0 ? '+' : ''}$${totalProfit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
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

                                <PositionsTable
                                    positions={positions}
                                    onClose={handleClosePosition}
                                />
                            </div>

                            <div className="lg:col-span-1">
                                <TradingTerminal onOrder={handleNewOrder} />
                            </div>
                        </div>
                    </motion.div>
                </main>
            </div>
        </div>
    );
};

export default DashboardPage;
