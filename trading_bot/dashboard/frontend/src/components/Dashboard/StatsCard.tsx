import React from 'react';
import { ArrowUpRight, ArrowDownRight, type LucideIcon } from 'lucide-react';
import { GlassCard } from '../Shared/GlassCard';
import { cn } from '../../components/Shared/GlassCard';

interface StatsCardProps {
    label: string;
    value: string;
    change?: number;
    icon: LucideIcon;
    iconColor: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({ label, value, change, icon: Icon, iconColor }) => {
    return (
        <GlassCard hover className="flex flex-col gap-4">
            <div className="flex items-start justify-between">
                <div className={cn("p-3 rounded-xl bg-opacity-10", iconColor.replace('text-', 'bg-'))}>
                    <Icon className={iconColor} size={24} />
                </div>
                {change !== undefined && (
                    <div className={cn(
                        "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
                        change >= 0 ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
                    )}>
                        {change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {Math.abs(change)}%
                    </div>
                )}
            </div>
            <div>
                <p className="text-gray-500 text-sm font-medium">{label}</p>
                <p className="text-2xl font-bold text-white mt-1">{value}</p>
            </div>
        </GlassCard>
    );
};
