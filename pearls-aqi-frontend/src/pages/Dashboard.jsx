import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../api';
import { aqiLabel, aqiColor, formatDate } from '../utils';
import Card from '../components/Card';
import SectionTitle from '../components/SectionTitle';
import Loading from '../components/Loading';

export default function Dashboard() {
    const [current, setCurrent] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [model, setModel] = useState('gradient_boosting');
    const [loading, setLoading] = useState(true);

    const models = [
        { value: 'gradient_boosting', label: 'Gradient Boosting' },
        { value: 'random_forest', label: 'Random Forest' },
        { value: 'ridge', label: 'Ridge Regression' },
    ];

    useEffect(() => {
        setLoading(true);
        Promise.all([api.getCurrent(), api.getForecast(model)])
            .then(([c, f]) => {
                setCurrent(c.data);
                setForecast(f.data);
            })
            .finally(() => setLoading(false));
    }, [model]);

    if (loading) return <Loading />;

    const cat = aqiLabel(current.aqi);
    const color = aqiColor(cat);

    return (
        <div>
            {/* Current AQI Header */}
            <Card style={{
                background: 'linear-gradient(135deg, #e8f4fd 0%, #dbeafe 100%)',
                border: '1px solid #bfdbfe',
                marginBottom: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '1rem',
            }}>
                <div>
                    <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#1e3a5f', letterSpacing: '-0.5px' }}>
                        Current Air Quality
                    </h1>
                    <p style={{ fontSize: '0.85rem', fontWeight: 300, color: '#5b7fa6', marginTop: 4 }}>
                        {current.city}, Sindh, Pakistan &nbsp;|&nbsp; {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                    <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem' }}>
                        <Stat label="Temperature" value={`${current.temperature}°C`} />
                        <Stat label="Humidity" value={`${current.humidity}%`} />
                        <Stat label="Wind" value={`${current.wind_speed} m/s`} />
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '4.5rem', fontWeight: 900, lineHeight: 1, color }}>{current.aqi}</div>
                    <div style={{ fontSize: '1rem', fontWeight: 600, color, marginTop: 4 }}>{cat}</div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 300, color: '#5b7fa6', marginTop: 4 }}>European AQI Scale</div>
                </div>
            </Card>

            {/* Model Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 500, color: '#64748b' }}>Prediction Model:</span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {models.map(m => (
                        <button
                            key={m.value}
                            onClick={() => setModel(m.value)}
                            style={{
                                padding: '0.4rem 0.9rem',
                                borderRadius: 8,
                                border: '1px solid',
                                borderColor: model === m.value ? '#2563eb' : '#e2e8f0',
                                background: model === m.value ? '#eff6ff' : 'white',
                                color: model === m.value ? '#2563eb' : '#64748b',
                                fontWeight: model === m.value ? 600 : 400,
                                fontSize: '0.8rem',
                                cursor: 'pointer',
                                fontFamily: 'Inter, sans-serif',
                            }}
                        >
                            {m.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* 3-Day Forecast Cards */}
            <SectionTitle title="3-Day Forecast" subtitle={`Predicted AQI using ${models.find(m => m.value === model)?.label}`} />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                {forecast.daily_forecast.map((day, i) => {
                    const c = aqiColor(day.category);
                    return (
                        <Card key={i} style={{ borderTop: `4px solid ${c}` }}>
                            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#94a3b8', marginBottom: 6 }}>
                                {i === 0 ? 'Tomorrow' : `Day ${i + 1}`}
                            </div>
                            <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: 8 }}>{formatDate(day.date)}</div>
                            <div style={{ fontSize: '3rem', fontWeight: 900, lineHeight: 1, color: c }}>{day.predicted_aqi}</div>
                            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: c, marginTop: 4 }}>{day.category}</div>
                            <div style={{ fontSize: '0.78rem', fontWeight: 300, color: '#94a3b8', marginTop: 12, paddingTop: 12, borderTop: '1px solid #f1f5f9' }}>
                                {day.temperature?.toFixed(1)}°C &nbsp;|&nbsp; {Math.round(day.humidity)}% humidity
                            </div>
                        </Card>
                    );
                })}
            </div>

            {/* 72-hour trend */}
            <Card>
                <SectionTitle title="72-Hour AQI Trend" subtitle="Forecast intervals (3-hourly)" />
                <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={forecast.hourly_forecast}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="hour" tickFormatter={h => `${h}:00`} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <Tooltip
                            contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
                            formatter={(v) => [v, 'AQI']}
                        />
                        <Line type="monotone" dataKey="predicted_aqi" stroke="#2563eb" strokeWidth={2} dot={false} />
                    </LineChart>
                </ResponsiveContainer>
            </Card>
        </div>
    );
}

function Stat({ label, value }) {
    return (
        <div>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8' }}>{label}</div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: '#1e3a5f', marginTop: 2 }}>{value}</div>
        </div>
    );
}