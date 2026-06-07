import { NavLink } from 'react-router-dom';

const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/history', label: 'History' },
    { to: '/analysis', label: 'Analysis' },
    { to: '/alerts', label: 'Alerts' },
];

const styles = {
    nav: {
        background: 'white',
        borderBottom: '1px solid #e2e8f0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
    },
    inner: {
        maxWidth: 1200,
        margin: '0 auto',
        padding: '0 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 64,
    },
    brand: {
        fontSize: '1.1rem',
        fontWeight: 700,
        color: '#1e3a5f',
        letterSpacing: '-0.3px',
    },
    sub: {
        fontSize: '0.75rem',
        fontWeight: 300,
        color: '#94a3b8',
        marginTop: 2,
    },
    links: {
        display: 'flex',
        gap: '0.25rem',
    },
    link: {
        padding: '0.5rem 1rem',
        borderRadius: 8,
        fontSize: '0.875rem',
        fontWeight: 500,
        color: '#64748b',
        transition: 'all 0.15s',
    },
    activeLink: {
        background: '#eff6ff',
        color: '#2563eb',
        fontWeight: 600,
    },
};

export default function Navbar() {
    return (
        <nav style={styles.nav}>
            <div style={styles.inner}>
                <div>
                    <div style={styles.brand}>Pearls AQI Predictor</div>
                    <div style={styles.sub}>Sukkur, Sindh, Pakistan</div>
                </div>
                <div style={styles.links}>
                    {links.map(l => (
                        <NavLink
                            key={l.to}
                            to={l.to}
                            end={l.to === '/'}
                            style={({ isActive }) => ({
                                ...styles.link,
                                ...(isActive ? styles.activeLink : {}),
                            })}
                        >
                            {l.label}
                        </NavLink>
                    ))}
                </div>
            </div>
        </nav>
    );
}