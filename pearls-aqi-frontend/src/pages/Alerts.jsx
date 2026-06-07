import { useEffect, useState } from 'react';
import { api } from '../api';
import { aqiLabel, aqiColor } from '../utils';
import Card from '../components/Card';
import SectionTitle from '../components/SectionTitle';
import Loading from '../components/Loading';

const AQI_SCALE = [
    { range: '0 - 20', category: 'Good', impact: 'No health risk. Air quality is satisfactory.', color: '#16a34a' },
    { range: '21 - 40', category: 'Fair', impact: 'Acceptable quality. Minor concern for very sensitive people.', color: '#2563eb' },
    { range: '41 - 60', category: 'Moderate', impact: 'Sensitive groups may experience health effects.', color: '#d97706' },
    { range: '61 - 80', category: 'Poor', impact: 'Everyone may experience health effects.', color: '#ea580c' },
    { range: '81 - 100', category: 'Very Poor', impact: 'Serious health effects for everyone.', color: '#dc2626' },
    { range: '100+', category: 'Extremely Poor', impact: 'Emergency conditions. Serious risk for entire population.', color: '#991b1b' },
];

function AlertBox({ maxAqi, city }) {
    const cat = aqiLabel(maxAqi);

    if (maxAqi > 100) return (
        <div style={{ background: '#fef2f2', border: '1.5px solid #fca5a5', borderRadius: 14, padding: '1.5rem 2rem', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#dc2626' }}>Critical Health Warning</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e3a5f', marginTop: 6 }}>Extremely Poor Air Quality Forecast for {city}</div>
            <div style={{ fontSize: '0.88rem', fontWeight: 300, color: '#475569', marginTop: 8, lineHeight: 1.7 }}>
                Air quality is predicted to reach <strong>Extremely Poor (AQI {maxAqi.toFixed(0)})</strong> over the next 3 days.
                This is a serious health hazard for everyone. Prolonged exposure can cause severe respiratory and cardiovascular effects.
            </div>
            <Recommendations items={['Stay indoors and keep all windows closed', 'Wear N95 masks if outdoor activity is unavoidable', 'Use air purifiers indoors if available', 'Children and elderly must avoid all outdoor activities', 'Seek medical attention if experiencing breathing difficulties']} />
        </div>
    );

    if (maxAqi > 80) return (
        <div style={{ background: '#fef2f2', border: '1.5px solid #fca5a5', borderRadius: 14, padding: '1.5rem 2rem', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#dc2626' }}>Health Warning</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e3a5f', marginTop: 6 }}>Very Poor Air Quality Expected</div>
            <div style={{ fontSize: '0.88rem', fontWeight: 300, color: '#475569', marginTop: 8, lineHeight: 1.7 }}>
                Air quality is predicted to be <strong>Very Poor (AQI {maxAqi.toFixed(0)})</strong>. Everyone may experience health effects.
            </div>
            <Recommendations items={['Avoid prolonged outdoor activities', 'Wear masks when outdoors', 'Keep windows closed during peak pollution hours']} />
        </div>
    );

    if (maxAqi > 60) return (
        <div style={{ background: '#fffbeb', border: '1.5px solid #fcd34d', borderRadius: 14, padding: '1.5rem 2rem', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#d97706' }}>Health Advisory</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e3a5f', marginTop: 6 }}>Poor Air Quality Expected</div>
            <div style={{ fontSize: '0.88rem', fontWeight: 300, color: '#475569', marginTop: 8, lineHeight: 1.7 }}>
                Air quality is predicted to be <strong>Poor (AQI {maxAqi.toFixed(0)})</strong>. Everyone may begin to experience health effects.
            </div>
            <Recommendations items={['Limit prolonged outdoor exertion', 'Sensitive groups should stay indoors']} />
        </div>
    );

    return (
        <div style={{ background: '#f0fdf4', border: '1.5px solid #86efac', borderRadius: 14, padding: '1.5rem 2rem', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#16a34a' }}>All Clear</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e3a5f', marginTop: 6 }}>Good Air Quality Expected</div>
            <div style={{ fontSize: '0.88rem', fontWeight: 300, color: '#475569', marginTop: 8 }}>
                Air quality is predicted to be <strong>{cat} (AQI {maxAqi.toFixed(0)})</strong>. No health impacts expected.
            </div>
        </div>
    );
}

function Recommendations({ items }) {
    return (
        <div style={{ marginTop: '1rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#64748b', marginBottom: 8 }}>Recommendations</div>
            {items.map((item, i) => (
                <div key={i} style={{ fontSize: '0.85rem', fontWeight: 300, color: '#475569', padding: '4px 0 4px 12px', borderLeft: '2px solid #e2e8f0', marginBottom: 6 }}>{item}</div>
            ))}
        </div>
    );
}

export default function Alerts() {
    const [forecast, setForecast] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getForecast('gradient_boosting').then(r => setForecast(r.data)).finally(() => setLoading(false));
    }, []);

    if (loading) return <Loading />;

    const maxAqi = Math.max(...forecast.daily_forecast.map(d => d.predicted_aqi));

    return (
        <div>
            <SectionTitle title="Health Alerts" subtitle="Air quality advisories based on 3-day forecast for Sukkur" />
            <AlertBox maxAqi={maxAqi} city={forecast.city} />

            {/* AQI Scale */}
            <Card>
                <SectionTitle title="European AQI Scale Reference" subtitle="Open-Meteo European Air Quality Index scale" />
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                        <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                            {['AQI Range', 'Category', 'Health Impact'].map(h => (
                                <th key={h} style={{ padding: '0.75rem 1rem', textAlign: 'left', fontWeight: 600, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: 1 }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {AQI_SCALE.map((row, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: row.color }}>{row.range}</td>
                                <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: row.color }}>{row.category}</td>
                                <td style={{ padding: '0.75rem 1rem', fontWeight: 300, color: '#475569' }}>{row.impact}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </Card>
        </div>
    );
}