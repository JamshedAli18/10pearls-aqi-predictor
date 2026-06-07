export default function SectionTitle({ title, subtitle }) {
    return (
        <div style={{ marginBottom: '1.2rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#1e3a5f' }}>{title}</h2>
            {subtitle && <p style={{ fontSize: '0.82rem', fontWeight: 300, color: '#94a3b8', marginTop: 4 }}>{subtitle}</p>}
        </div>
    );
}