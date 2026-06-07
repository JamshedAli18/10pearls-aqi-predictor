import { useEffect, useState } from 'react';
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import SectionTitle from '../components/SectionTitle';
import Loading from '../components/Loading';

export default function History() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getHistorical(2160).then(r => {
            setData(r.data.data.reverse());
        }).finally(() => setLoading(false));
    }, []);

    if (loading) return <Loading />;

    // daily average
    const dailyMap = {};
    data.forEach(d => {
        const date = d.timestamp?.split('T')[0] || d.timestamp?.split(' ')[0];
        if (!dailyMap[date]) dailyMap[date] = { aqi: [], temp: [], pm10: [], pm2_5: [] };
        dailyMap[date].aqi.push(d.aqi);
        if (d.temperature) dailyMap[date].temp.push(d.temperature);
        if (d.pm10) dailyMap[date].pm10.push(d.pm10);
        if (d.pm2_5) dailyMap[date].pm2_5.push(d.pm2_5);
    });

    const daily = Object.entries(dailyMap).map(([date, v]) => ({
        date,
        aqi: parseFloat((v.aqi.reduce((a, b) => a + b, 0) / v.aqi.length).toFixed(1)),
        temp: v.temp.length ? parseFloat((v.temp.reduce((a, b) => a + b, 0) / v.temp.length).toFixed(1)) : null,
        pm10: v.pm10.length ? parseFloat((v.pm10.reduce((a, b) => a + b, 0) / v.pm10.length).toFixed(1)) : null,
        pm2_5: v.pm2_5.length ? parseFloat((v.pm2_5.reduce((a, b) => a + b, 0) / v.pm2_5.length).toFixed(1)) : null,
    })).sort((a, b) => a.date.localeCompare(b.date));

    // monthly average
    const monthMap = {};
    daily.forEach(d => {
        const m = d.date.slice(0, 7);
        if (!monthMap[m]) monthMap[m] = [];
        monthMap[m].push(d.aqi);
    });
    const monthly = Object.entries(monthMap).map(([month, vals]) => ({
        month,
        aqi: parseFloat((vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1))
    }));

    const avgAqi = (data.reduce((a, b) => a + b.aqi, 0) / data.length).toFixed(0);
    const maxAqi = Math.max(...data.map(d => d.aqi));
    const minAqi = Math.min(...data.map(d => d.aqi));

    return (
        <div>
            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                {[
                    { label: 'Average AQI', value: avgAqi, color: '#2563eb' },
                    { label: 'Max AQI', value: maxAqi, color: '#dc2626' },
                    { label: 'Min AQI', value: minAqi, color: '#16a34a' },
                    { label: 'Total Records', value: data.length, color: '#7c3aed' },
                ].map((s, i) => (
                    <Card key={i} style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: s.color }}>{s.value}</div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 4 }}>{s.label}</div>
                    </Card>
                ))}
            </div>

            {/* Daily AQI */}
            <Card style={{ marginBottom: '1.5rem' }}>
                <SectionTitle title="Daily Average AQI" subtitle="Last 3 months" />
                <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={daily}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} tickFormatter={d => d.slice(5)} />
                        <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                        <Line type="monotone" dataKey="aqi" stroke="#2563eb" strokeWidth={2} dot={false} />
                    </LineChart>
                </ResponsiveContainer>
            </Card>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                {/* Temperature */}
                <Card>
                    <SectionTitle title="Temperature Trend" subtitle="Last 3 months (°C)" />
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={daily.filter(d => d.temp)}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} tickFormatter={d => d.slice(5)} />
                            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                            <Line type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={2} dot={false} name="Temp (°C)" />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>

                {/* PM10 + PM2.5 */}
                <Card>
                    <SectionTitle title="PM10 and PM2.5" subtitle="Last 3 months (µg/m³)" />
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={daily.filter(d => d.pm10)}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} tickFormatter={d => d.slice(5)} />
                            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                            <Legend wrapperStyle={{ fontSize: 11 }} />
                            <Line type="monotone" dataKey="pm10" stroke="#dc2626" strokeWidth={2} dot={false} name="PM10" />
                            <Line type="monotone" dataKey="pm2_5" stroke="#f59e0b" strokeWidth={2} dot={false} name="PM2.5" />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Monthly Average */}
            <Card>
                <SectionTitle title="Monthly Average AQI" subtitle="Average per month" />
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={monthly}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                        <Bar dataKey="aqi" fill="#3b82f6" radius={[4, 4, 0, 0]} name="AQI" />
                    </BarChart>
                </ResponsiveContainer>
            </Card>
        </div>
    );
}