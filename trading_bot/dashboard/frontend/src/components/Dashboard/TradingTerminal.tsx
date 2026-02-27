import React, { useState } from 'react';
import { GlassCard } from '../Shared/GlassCard';
import { cn } from '../../components/Shared/GlassCard';

type OrderType = 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_MARKET';
type Side = 'BUY' | 'SELL';

export const TradingTerminal: React.FC = () => {
    const [side, setSide] = useState<Side>('BUY');
    const [type, setType] = useState<OrderType>('MARKET');

    return (
        <GlassCard className="h-full flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Order Terminal</h2>
                <div className="flex bg-secondary/50 rounded-lg p-1">
                    <button
                        onClick={() => setSide('BUY')}
                        className={cn(
                            "px-4 py-1.5 rounded-md text-sm font-medium transition-all",
                            side === 'BUY' ? "bg-success text-white" : "text-gray-400 hover:text-white"
                        )}
                    >
                        Buy
                    </button>
                    <button
                        onClick={() => setSide('SELL')}
                        className={cn(
                            "px-4 py-1.5 rounded-md text-sm font-medium transition-all",
                            side === 'SELL' ? "bg-danger text-white" : "text-gray-400 hover:text-white"
                        )}
                    >
                        Sell
                    </button>
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Order Type</label>
                    <div className="grid grid-cols-2 gap-2">
                        {(['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET'] as OrderType[]).map((t) => (
                            <button
                                key={t}
                                onClick={() => setType(t)}
                                className={cn(
                                    "py-2 rounded-lg text-xs font-medium border transition-all",
                                    type === t
                                        ? "bg-primary/10 border-primary text-primary"
                                        : "bg-white/5 border-white/5 text-gray-400 hover:border-white/20"
                                )}
                            >
                                {t.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Quantity (BTC)</label>
                    <input
                        type="number"
                        placeholder="0.00"
                        className="w-full bg-white/5 border border-white/5 rounded-lg py-3 px-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-white font-medium"
                    />
                </div>

                {(type === 'LIMIT' || type === 'STOP') && (
                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Price (USDT)</label>
                        <input
                            type="number"
                            placeholder="0.00"
                            className="w-full bg-white/5 border border-white/5 rounded-lg py-3 px-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-white font-medium"
                        />
                    </div>
                )}

                {(type === 'STOP' || type === 'STOP_MARKET') && (
                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Stop Price</label>
                        <input
                            type="number"
                            placeholder="0.00"
                            className="w-full bg-white/5 border border-white/5 rounded-lg py-3 px-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-white font-medium"
                        />
                    </div>
                )}

                <div className="pt-4">
                    <button className={cn(
                        "w-full py-4 rounded-xl font-bold uppercase tracking-widest shadow-lg transition-all active:scale-95",
                        side === 'BUY'
                            ? "bg-success hover:bg-success/90 shadow-success/20"
                            : "bg-danger hover:bg-danger/90 shadow-danger/20"
                    )}>
                        {side} BTC
                    </button>
                    <div className="flex justify-between mt-3 text-xs text-gray-500 px-1">
                        <span>Available: 0.00 USDT</span>
                        <span className="text-primary hover:underline cursor-pointer">Max</span>
                    </div>
                </div>
            </div>
        </GlassCard>
    );
};
