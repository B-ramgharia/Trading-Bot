import React, { useState } from 'react';
import { GlassCard } from '../Shared/GlassCard';
import { cn } from '../../components/Shared/GlassCard';
import { toast } from 'sonner';

type OrderType = 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_MARKET';
type Side = 'BUY' | 'SELL';

interface TradingTerminalProps {
    onOrder?: (data: { side: Side; type: OrderType; quantity: number; symbol: string }) => void;
}

export const TradingTerminal: React.FC<TradingTerminalProps> = ({ onOrder }) => {
    const [side, setSide] = useState<Side>('BUY');
    const [type, setType] = useState<OrderType>('MARKET');
    const [quantity, setQuantity] = useState<string>('');
    const [price, setPrice] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async () => {
        if (!quantity || parseFloat(quantity) <= 0) {
            toast.error('Invalid quantity');
            return;
        }

        setIsLoading(true);

        // Simulate execution delay
        await new Promise(resolve => setTimeout(resolve, 800));

        if (onOrder) {
            onOrder({
                side,
                type,
                quantity: parseFloat(quantity),
                symbol: 'BTCUSDT'
            });
        }

        setIsLoading(false);
        setQuantity('');
    };

    return (
        <GlassCard className="h-full flex flex-col gap-6">
            {/* Header with Live Market indicator */}
            <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-white">Order Terminal</h2>
                    <div className="flex items-center gap-1.5 px-2 py-1 bg-primary/10 rounded-md border border-primary/20">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                        <span className="text-[10px] font-bold text-primary uppercase tracking-wider">Live Market</span>
                        <span className="text-xs font-mono text-white">$66,134.90</span>
                    </div>
                </div>

                {/* Side Selector (Buy/Sell) */}
                <div className="flex bg-secondary/50 rounded-lg p-1">
                    <button
                        onClick={() => setSide('BUY')}
                        className={cn(
                            "flex-1 py-1.5 rounded-md text-sm font-medium transition-all",
                            side === 'BUY' ? "bg-success text-white shadow-lg shadow-success/20" : "text-gray-400 hover:text-white"
                        )}
                    >
                        Buy
                    </button>
                    <button
                        onClick={() => setSide('SELL')}
                        className={cn(
                            "flex-1 py-1.5 rounded-md text-sm font-medium transition-all",
                            side === 'SELL' ? "bg-danger text-white shadow-lg shadow-danger/20" : "text-gray-400 hover:text-white"
                        )}
                    >
                        Sell
                    </button>
                </div>
            </div>

            <div className="space-y-4">
                {/* Order Type Selector */}
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

                {/* Amount Input */}
                <div>
                    <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Quantity (BTC)</label>
                    <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        placeholder="0.00"
                        className="w-full bg-white/5 border border-white/5 rounded-lg py-3 px-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-white font-medium"
                    />
                </div>

                {/* Price Input (for Limit/Stop-Limit) */}
                {(type === 'LIMIT' || type === 'STOP') && (
                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block uppercase tracking-wider font-semibold">Price (USDT)</label>
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="0.00"
                            className="w-full bg-white/5 border border-white/5 rounded-lg py-3 px-4 focus:outline-none focus:border-primary/50 focus:bg-white/10 transition-all text-white font-medium"
                        />
                    </div>
                )}

                {/* Stop Price Input */}
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

                {/* Action Button */}
                <div className="pt-4">
                    <button
                        onClick={handleSubmit}
                        disabled={isLoading}
                        className={cn(
                            "w-full py-4 rounded-xl font-bold uppercase tracking-widest shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                            side === 'BUY'
                                ? "bg-success hover:bg-success/90 shadow-success/10"
                                : "bg-danger hover:bg-danger/90 shadow-danger/10"
                        )}
                    >
                        {isLoading ? 'Processing...' : `${side} BTC`}
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
