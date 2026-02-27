import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, type IChartApi } from 'lightweight-charts';

export const PriceChart: React.FC = () => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);

    const [error, setError] = React.useState<string | null>(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        let chart: any = null;
        try {
            chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: 'transparent' },
                    textColor: '#9CA3AF',
                },
                grid: {
                    vertLines: { color: 'rgba(197, 203, 206, 0.05)' },
                    horzLines: { color: 'rgba(197, 203, 206, 0.05)' },
                },
                width: chartContainerRef.current.clientWidth,
                height: 480,
                timeScale: {
                    borderVisible: false,
                    timeVisible: true,
                    secondsVisible: false,
                },
                rightPriceScale: {
                    borderVisible: false,
                },
            });

            const candlestickSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#0ecb81',
                downColor: '#f6465d',
                borderVisible: false,
                wickUpColor: '#0ecb81',
                wickDownColor: '#f6465d',
            });

            candlestickSeries.setData([
                { time: '2023-01-01', open: 16500, high: 17000, low: 16400, close: 16800 },
                { time: '2023-01-02', open: 16800, high: 17200, low: 16700, close: 17100 },
                { time: '2023-01-03', open: 17100, high: 17500, low: 17000, close: 17300 },
                { time: '2023-01-04', open: 17300, high: 17800, low: 17200, close: 17700 },
                { time: '2023-01-05', open: 17700, high: 17600, low: 17100, close: 17200 },
                { time: '2023-01-06', open: 17200, high: 17400, low: 16900, close: 17000 },
            ]);

            chartRef.current = chart;

            const handleResize = () => {
                if (chartContainerRef.current && chartRef.current) {
                    chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
                }
            };

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                if (chart) chart.remove();
            };
        } catch (err) {
            console.error("Chart initialization failed:", err);
            setError(err instanceof Error ? err.message : String(err));
        }
    }, []);

    if (error) {
        return (
            <div className="flex items-center justify-center h-[480px] bg-red-500/5 rounded-xl border border-red-500/20 p-8 text-center">
                <div>
                    <p className="text-red-400 font-bold mb-2">Chart Error</p>
                    <p className="text-gray-500 text-sm max-w-md">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full relative p-4">
            <div className="absolute top-6 left-6 z-10">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    BTC / USDT <span className="text-success text-sm font-medium">+2.4%</span>
                </h3>
            </div>
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
};
