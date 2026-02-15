import { useEffect, useMemo, useState } from "react";
import { Doughnut } from 'react-chartjs-2';

import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

export default function Daily() {
  const [stats, setDaily] = useState({});
  const [error, setError] = useState("");

  async function fetchDaily() {
    try {
      const res = await fetch("http://localhost:8000/daily");
      if (!res.ok) throw new Error("Server Error");
      const data = await res.json();
      setDaily(data);
      setError("");
    } catch (err) {
      setError("Err.");
      setDaily({});
      return;
    }
  }

  function format_time(time: number) {
    const h = Math.floor(time / 3600);
    const m = Math.floor((time % 3600) / 60);
    const s = Math.floor(time % 60);
    return `${h > 0 ? h + 'h ' : ''}${m}m ${s}s`;
  }

  const values = Object.values(stats);
  const totalSeconds = values.reduce((acc, curr) => (acc as number) + (curr as number), 0);
  const formattedTotal = format_time((totalSeconds as number));


  useEffect(() => {
    let intervalId: number | undefined;
    let isPolling = false;

    function startPolling() {
      if (isPolling) return;
      isPolling = true;

      fetchDaily();
      intervalId = window.setInterval(fetchDaily, 1000);
    }

    function stopPolling() {
      if (!isPolling) return;
      isPolling = false;
      clearInterval(intervalId);
    }

    function handleVisibility() {
      if (document.hidden) stopPolling();
      else startPolling();
    }

    startPolling();
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);

  const COLORS = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(199, 56, 86, 1)',
    'rgba(36, 96, 168, 1)',
    'rgba(233, 182, 60, 1)',
    'rgba(47, 140, 140, 1)',
    'rgba(124, 75, 215, 1)',
    'rgba(217, 124, 50, 1)',
    'rgba(90, 200, 120, 1)',
    'rgba(200, 90, 200, 1)',
    'rgba(110, 110, 110, 1)',
  ]
  const HOVER_COLORS = [
    'rgba(255, 99, 132, 0.7)',
    'rgba(54, 162, 235, 0.7)',
    'rgba(255, 206, 86, 0.7)',
    'rgba(75, 192, 192, 0.7)',
    'rgba(153, 102, 255, 0.7)',
    'rgba(255, 159, 64, 0.7)',
    'rgba(199, 56, 86, 0.7)',
    'rgba(36, 96, 168, 0.7)',
    'rgba(233, 182, 60, 0.7)',
    'rgba(47, 140, 140, 0.7)',
    'rgba(124, 75, 215, 0.7)',
    'rgba(217, 124, 50, 0.7)',
    'rgba(90, 200, 120, 0.7)',
    'rgba(200, 90, 200, 0.7)',
    'rgba(110, 110, 110, 0.7)',
  ];

  const chartData = useMemo(() => {
    const keys = Object.keys(stats);
    const dataValues = Object.values(stats);

    return {
      labels: keys,
      datasets: [
        {
          label: "Time Spent",
          data: dataValues,
          backgroundColor: keys.map((_, i) => COLORS[i % COLORS.length]),
          hoverBackgroundColor: keys.map((_, i) => HOVER_COLORS[i % HOVER_COLORS.length]),
          hoverOffset: 15,
          borderColor: '#1e293b',
          borderWidth: 2,
        }
      ],
    };
  }, [stats]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 500,
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.raw;
            return ` Time: ${format_time(value)}`;
          }
        }
      },
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
          font: { size: 14 }
        }
      }
    },
    cutout: '55%'
  };


  return (
    <div className="flex flex-col items-center text-white bg-slate-800 rounded-xl p-6">
      <h1 className="text-2xl mb-4 font-bold">Daily Time Stats</h1>

      {error && <p className="text-red-400 mb-2">{error}</p>}

      {/* Ensure this container has a fixed height or square-ish dimensions */}
      <div className="relative w-full h-[400px] flex items-center justify-center">

        {/* Wrap the Doughnut in its own full-size div */}
        <div className="w-full h-full">
          <Doughnut data={chartData} options={chartOptions} />
        </div>

        {/* Center Label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-slate-400 text-xs uppercase tracking-widest mb-1 mt-4">Total Time</span>
          <span className="text-4xl font-mono font-bold leading-none">{formattedTotal}</span>
        </div>

      </div>
    </div>
  );
}
