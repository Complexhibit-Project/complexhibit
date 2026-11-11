"use client";

import { API_URL } from "@/lib/config";
import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, BarChart2, Download, Eye, RefreshCw, Loader2, 
  TrendingUp, TrendingDown, Calendar, FileDown, Activity
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from "recharts";
import { MetricsPDFButton } from "@/components/pdf/MetricsPDFButton";

interface MetricSummary {
  event_type: string;
  count: number;
}

interface MetricTrend {
  event_type: string;
  current_count: number;
  previous_count: number;
  change_percent: number;
}

interface MetricTimeSeries {
  date: string;
  event_type: string;
  count: number;
}

interface RecentMetric {
  id: number;
  event_type: string;
  payload: any;
  timestamp: string;
  user_id: number | null;
}

type TimeRange = "today" | "week" | "month" | "year" | "all";

const TIME_RANGES: { value: TimeRange; label: string }[] = [
  { value: "today", label: "Today" },
  { value: "week", label: "Last 7 Days" },
  { value: "month", label: "Last 30 Days" },
  { value: "year", label: "Last Year" },
  { value: "all", label: "All Time" },
];

export default function MetricsPage() {
  const router = useRouter();
  const { isAdmin, isLoading: authLoading } = useAuth();
  const [timeRange, setTimeRange] = useState<TimeRange>("month");
  const [trends, setTrends] = useState<MetricTrend[]>([]);
  const [timeseries, setTimeseries] = useState<MetricTimeSeries[]>([]);
  const [recent, setRecent] = useState<RecentMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const dashboardRef = useRef<HTMLDivElement>(null);

  const apiUrl = API_URL;

  useEffect(() => {
    if (!authLoading && !isAdmin) {
      router.push("/");
    }
  }, [authLoading, isAdmin, router]);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const headers = { Authorization: `Bearer ${token}` };

      const [trendsRes, timeseriesRes, recentRes] = await Promise.all([
        fetch(`${apiUrl}/metrics/trends?time_range=${timeRange}`, { headers, cache: 'no-store' }),
        fetch(`${apiUrl}/metrics/timeseries?time_range=${timeRange}`, { headers, cache: 'no-store' }),
        fetch(`${apiUrl}/metrics/recent?time_range=${timeRange}&limit=20`, { headers, cache: 'no-store' })
      ]);

      if (trendsRes.ok) setTrends(await trendsRes.json());
      if (timeseriesRes.ok) setTimeseries(await timeseriesRes.json());
      if (recentRes.ok) setRecent(await recentRes.json());
    } catch (error) {
      console.error("Failed to fetch metrics", error);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, timeRange]);

  useEffect(() => {
    if (isAdmin) {
      fetchMetrics();
    }
  }, [isAdmin, fetchMetrics]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${apiUrl}/metrics/export?time_range=${timeRange}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics_${timeRange}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      }
    } catch (error) {
      console.error("Failed to export", error);
    } finally {
      setExporting(false);
    }
  };

  if (authLoading || !isAdmin) return null;

  // Process timeseries for chart - aggregate by date
  const chartData = timeseries.reduce((acc, item) => {
    const existing = acc.find(d => d.date === item.date);
    if (existing) {
      existing[item.event_type] = item.count;
    } else {
      acc.push({ date: item.date, [item.event_type]: item.count });
    }
    return acc;
  }, [] as Record<string, any>[]);

  const eventTypes = [...new Set(timeseries.map(t => t.event_type))];
  const colors = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  const getIcon = (type: string) => {
    if (type === "download") return <Download className="h-5 w-5" />;
    if (type === "page_view") return <Eye className="h-5 w-5" />;
    return <Activity className="h-5 w-5" />;
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (change < 0) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return null;
  };

  const totalEvents = trends.reduce((sum, t) => sum + t.current_count, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mb-4 transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Home
          </Link>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <BarChart2 className="h-8 w-8 text-indigo-600" />
                Analytics Dashboard
              </h1>
              <p className="mt-1 text-gray-600">Track usage patterns and engagement metrics</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Time Range Selector */}
              <div className="flex items-center gap-2 bg-white rounded-lg border border-gray-200 p-1">
                <Calendar className="h-4 w-4 text-gray-400 ml-2" />
                {TIME_RANGES.map((range) => (
                  <button
                    key={range.value}
                    onClick={() => setTimeRange(range.value)}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                      timeRange === range.value
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {range.label}
                  </button>
                ))}
              </div>
              
              {/* Export Button */}
              <button
                onClick={handleExport}
                disabled={exporting}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 transition-colors"
              >
                <FileDown className={`h-4 w-4 ${exporting ? 'animate-bounce' : ''}`} />
                Export CSV
              </button>

              <MetricsPDFButton targetRef={dashboardRef} />
              
              {/* Refresh Button */}
              <button
                onClick={fetchMetrics}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-24">
            <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
          </div>
        ) : (
          <div ref={dashboardRef} className="bg-white/50 p-4 rounded-xl">
            {/* KPI Cards with Trends */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {/* Total Events Card */}
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm opacity-80">Total Events</div>
                    <div className="text-4xl font-bold mt-1">{totalEvents.toLocaleString()}</div>
                  </div>
                  <div className="h-12 w-12 bg-white/20 rounded-full flex items-center justify-center">
                    <Activity className="h-6 w-6" />
                  </div>
                </div>
              </div>
              
              {/* Individual Metric Cards */}
              {trends.slice(0, 3).map((trend, idx) => (
                <div key={trend.event_type} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-gray-500 capitalize">{trend.event_type.replace('_', ' ')}</div>
                      <div className="text-3xl font-bold text-gray-900 mt-1">{trend.current_count.toLocaleString()}</div>
                      <div className={`flex items-center gap-1 mt-2 text-sm ${
                        trend.change_percent > 0 ? 'text-green-600' : 
                        trend.change_percent < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {getTrendIcon(trend.change_percent)}
                        <span>{trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%</span>
                        <span className="text-gray-400 ml-1">vs prev</span>
                      </div>
                    </div>
                    <div className={`h-12 w-12 rounded-full flex items-center justify-center ${
                      idx === 0 ? 'bg-blue-50 text-blue-600' :
                      idx === 1 ? 'bg-green-50 text-green-600' :
                      'bg-amber-50 text-amber-600'
                    }`}>
                      {getIcon(trend.event_type)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Area Chart - Trends Over Time */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Over Time</h3>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={chartData}>
                      <defs>
                        {eventTypes.map((type, idx) => (
                          <linearGradient key={type} id={`color${type}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={colors[idx % colors.length]} stopOpacity={0.3}/>
                            <stop offset="95%" stopColor={colors[idx % colors.length]} stopOpacity={0}/>
                          </linearGradient>
                        ))}
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fill: '#6B7280', fontSize: 12 }}
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
                      />
                      <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} />
                      <Tooltip 
                        contentStyle={{ borderRadius: 8, border: '1px solid #E5E7EB' }}
                        labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      />
                      <Legend />
                      {eventTypes.map((type, idx) => (
                        <Area 
                          key={type}
                          type="monotone" 
                          dataKey={type} 
                          stroke={colors[idx % colors.length]} 
                          fillOpacity={1}
                          fill={`url(#color${type})`}
                          name={type.replace('_', ' ')}
                        />
                      ))}
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-gray-500">
                    No data available for this time range
                  </div>
                )}
              </div>

              {/* Bar Chart - Event Type Comparison */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Type</h3>
                {trends.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={trends} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 12 }} />
                      <YAxis 
                        type="category" 
                        dataKey="event_type" 
                        tick={{ fill: '#6B7280', fontSize: 12 }}
                        tickFormatter={(value) => value.replace('_', ' ')}
                        width={100}
                      />
                      <Tooltip 
                        contentStyle={{ borderRadius: 8, border: '1px solid #E5E7EB' }}
                        formatter={(value) => [Number(value).toLocaleString(), 'Count']}
                      />
                      <Bar 
                        dataKey="current_count" 
                        fill="#4F46E5" 
                        radius={[0, 4, 4, 0]}
                        name="Current Period"
                      />
                      <Bar 
                        dataKey="previous_count" 
                        fill="#E5E7EB" 
                        radius={[0, 4, 4, 0]}
                        name="Previous Period"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-gray-500">
                    No data available
                  </div>
                )}
              </div>
            </div>

            {/* Recent Activity Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                <span className="text-sm text-gray-500">{recent.length} events</span>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recent.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                          No recent activity found
                        </td>
                      </tr>
                    ) : (
                      recent.map((metric) => (
                        <tr key={metric.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              <span className={`p-1.5 rounded-lg ${
                                metric.event_type === 'download' ? 'bg-green-100 text-green-600' :
                                metric.event_type === 'page_view' ? 'bg-blue-100 text-blue-600' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {getIcon(metric.event_type)}
                              </span>
                              <span className="font-medium text-gray-900 capitalize">
                                {metric.event_type.replace('_', ' ')}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                            {metric.payload ? (
                              <span title={JSON.stringify(metric.payload, null, 2)}>
                                {metric.payload.label || metric.payload.filename || metric.payload.url || JSON.stringify(metric.payload)}
                              </span>
                            ) : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {metric.user_id ? `User #${metric.user_id}` : 'Anonymous'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(metric.timestamp).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
