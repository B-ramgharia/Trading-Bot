import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export interface Position {
    id: string;
    symbol: string;
    side: 'BUY' | 'SELL';
    size: number;
    entryPrice: number;
    markPrice: number;
    pnl: number;
    pnlPercent: number;
}

interface PositionsTableProps {
    positions: Position[];
    onClose: (id: string) => void;
}

export const PositionsTable: React.FC<PositionsTableProps> = ({ positions, onClose }) => {
    return (
        <div className="glass rounded-xl p-6 border border-white/5 min-h-[300px]">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white">Active Positions</h3>
                <span className="text-xs text-gray-500 font-mono">{positions.length} Open</span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="text-gray-500 text-[10px] uppercase tracking-wider border-b border-white/5">
                            <th className="pb-3 pl-1 font-semibold">Symbol</th>
                            <th className="pb-3 font-semibold">Size</th>
                            <th className="pb-3 font-semibold">Entry Price</th>
                            <th className="pb-3 font-semibold">Mark Price</th>
                            <th className="pb-3 font-semibold">PnL (ROE%)</th>
                            <th className="pb-3 pr-1 text-right font-semibold">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        <AnimatePresence>
                            {positions.length === 0 ? (
                                <motion.tr
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                >
                                    <td colSpan={6} className="py-12 text-center text-gray-600 italic text-sm">
                                        No active positions found
                                    </td>
                                </motion.tr>
                            ) : (
                                positions.map((pos) => (
                                    <motion.tr
                                        key={pos.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                        className="group hover:bg-white/[0.02] transition-colors"
                                    >
                                        <td className="py-4 pl-1">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-bold text-white">{pos.symbol}</span>
                                                <span className={`text-[10px] font-bold ${pos.side === 'BUY' ? 'text-success' : 'text-danger'}`}>
                                                    {pos.side} 20x
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4 text-sm font-medium text-white">
                                            {pos.size} {pos.symbol.replace('USDT', '')}
                                        </td>
                                        <td className="py-4 text-sm font-mono text-gray-400">
                                            ${pos.entryPrice.toLocaleString()}
                                        </td>
                                        <td className="py-4 text-sm font-mono text-white">
                                            ${pos.markPrice.toLocaleString()}
                                        </td>
                                        <td className="py-4">
                                            <div className="flex items-center gap-1.5" title="Unrealized PnL">
                                                <span className={`text-sm font-bold ${pos.pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                                                    {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)} USDT
                                                </span>
                                                <span className={`text-[10px] px-1.5 py-0.5 rounded bg-gray-900 font-bold ${pos.pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                                                    {pos.pnlPercent >= 0 ? '+' : ''}{pos.pnlPercent.toFixed(2)}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4 pr-1 text-right">
                                            <button
                                                onClick={() => onClose(pos.id)}
                                                className="p-2 hover:bg-danger/20 rounded-lg text-gray-500 hover:text-danger transition-all opacity-0 group-hover:opacity-100"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </AnimatePresence>
                    </tbody>
                </table>
            </div>
        </div>
    );
};
