export function aqiLabel(aqi) {
    aqi = parseFloat(aqi);
    if (aqi <= 20) return 'Good';
    if (aqi <= 40) return 'Fair';
    if (aqi <= 60) return 'Moderate';
    if (aqi <= 80) return 'Poor';
    if (aqi <= 100) return 'Very Poor';
    return 'Extremely Poor';
}

export function aqiColor(cat) {
    const colors = {
        'Good': '#16a34a',
        'Fair': '#2563eb',
        'Moderate': '#d97706',
        'Poor': '#ea580c',
        'Very Poor': '#dc2626',
        'Extremely Poor': '#991b1b',
    };
    return colors[cat] || '#64748b';
}

export function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

export function formatDateTime(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}