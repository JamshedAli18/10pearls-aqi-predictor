export default function Card({ children, style = {} }) {
    return (
        <div style={{
            background: 'white',
            borderRadius: 16,
            padding: '1.5rem',
            boxShadow: '0 1px 8px rgba(100,150,200,0.08)',
            border: '1px solid #e2e8f0',
            ...style
        }}>
            {children}
        </div>
    );
}