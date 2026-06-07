import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import SectionTitle from '../components/SectionTitle';
import Loading from '../components/Loading';

const SHAP_DATA = [
    { feature: 'aqi_lag_1', importance: 9.03 },
    { feature: 'aqi_change_rate', importance: 0.75 },
    { feature: 'aqi_lag_3', importance: 0.50 },
    { feature: 'aqi_rolling_mean_24', importance: 0.08 },
    { feature: 'aqi_lag_24', importance: 0.02 },
    { feature: 'pm10', importance: 0.021 },
    { feature: 'pm2_5', importance: 0.014 },
    { feature: 'temperature', importance: 0.005 },
    { feature: 'humidity', importance: 0.003 },
    { feature: 'hour', importance: 0.002 },
].sort((a, b) => b.importance - a.importance);

const MODELS = [
    { model: 'Gradient Boosting', r2: 0.9917, rmse: 1.2187, mae: 0.3714, verdict: 'No overfitting', status: 'Primary' },
    { model: 'Random Forest', r2: 0.9846, rmse: 1.6580, mae: 0.5181, verdict: 'No overfitting', status: 'Secondary' },
    { model: 'Ridge Regression', r2: 0.8862, rmse: 4.5046, mae: 2.5873, verdict: 'No overfitting', status: 'Secondary' },
    { model: 'Lasso', r2: 0.8833, rmse: 4.5620, mae: 2.5094, verdict: 'No overfitting', status: 'Trained' },
    { model: 'ElasticNet', r2: 0.8789, rmse: 4.6471, mae: 2.6446, verdict: 'No overfitting', status: 'Trained' },
    { model: 'LSTM', r2: -24.49, rmse: 67.358, mae: 61.343, verdict: 'Overfitting', status: 'Experimental' },
];

const POLLUTANT_COLORS = ['#dc2626', '#f59e0b', '#2563eb', '#16a34a', '#7c3aed'];

export default function Analysis() {
    const [current, setCurrent] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getCurrent().then(r => setCurrent(r.data)).finally(() => setLoading(false));
    }, []);

    if (loading) return <Loading />;

    const pollutants = Object.entries(current.pollutants).map(([key, val], i) => ({
        name: key.toUpperCase().replace('_', '.'),
        value: parseFloat(val?.toFixed(2) || 0),
        color: POLLUTANT_COLORS[i],
    }));

    return (
        <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                {/* SHAP */}
                <Card>
                    <SectionTitle title="SHAP Feature Importance" subtitle="Ridge model — mean absolute SHAP value" />
                    <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={SHAP_DATA} layout="vertical" margin={{ left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                            <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: '#64748b' }} width={130} />
                            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                            <Bar dataKey="importance" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Importance" />
                        </BarChart>
                    </ResponsiveContainer>
                </Card>

                {/* Pollutants */}
                <Card>
                    <SectionTitle title="Current Pollutant Levels" subtitle={`Live data for ${current.city} — µg/m³`} />
                    <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={pollutants}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                            <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Concentration">
                                {pollutants.map((p, i) => <Cell key={i} fill={p.color} />)}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Model Performance Table */}
            <Card>
                <SectionTitle title="Model Performance" subtitle="Evaluation metrics for all trained models" />
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                                {['Model', 'R² Score', 'RMSE', 'MAE', 'Verdict', 'Status'].map(h => (
                                    <th key={h} style={{ padding: '0.75rem 1rem', textAlign: 'left', fontWeight: 600, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: 1 }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {MODELS.map((m, i) => (
                                <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#1e3a5f' }}>{m.model}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: m.r2 > 0.9 ? '#16a34a' : '#dc2626' }}>{m.r2.toFixed(4)}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: '#475569' }}>{m.rmse.toFixed(4)}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: '#475569' }}>{m.mae.toFixed(4)}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: m.verdict === 'No overfitting' ? '#16a34a' : '#dc2626' }}>{m.verdict}</td>
                                    <td style={{ padding: '0.75rem 1rem' }}>
                                        <span style={{
                                            padding: '2px 10px', borderRadius: 20, fontSize: '0.75rem', fontWeight: 600,
                                            background: m.status === 'Primary' ? '#eff6ff' : m.status === 'Secondary' ? '#f0fdf4' : '#f8fafc',
                                            color: m.status === 'Primary' ? '#2563eb' : m.status === 'Secondary' ? '#16a34a' : '#94a3b8',
                                        }}>{m.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}