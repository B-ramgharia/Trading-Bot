import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Utility to merge class names */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface GlassCardProps {
    children: React.ReactNode;
    className?: string;
    hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className, hover = false }) => {
    return (
        <div className={cn(
            "glass rounded-xl p-6 transition-all duration-300",
            hover && "hover:bg-white/[0.08] hover:border-white/10 hover:shadow-2xl hover:shadow-black/20",
            className
        )}>
            {children}
        </div>
    );
};
