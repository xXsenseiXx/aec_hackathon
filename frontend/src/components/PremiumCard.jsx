export default function PremiumCard({ prediction }) {
    if (!prediction) {
        return (
            <div className="glass-card">
                <div className="card-title">
                    <span className="card-icon">🤖</span>
                    AI Premium Prediction
                </div>
                <div className="loading-spinner"><div className="spinner"></div></div>
            </div>
        )
    }

    const fmt = (n) => new Intl.NumberFormat('fr-DZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)

    return (
        <div className="glass-card">
            <div className="card-title">
                <span className="card-icon">🤖</span>
                AI Premium Prediction
            </div>

            <div className="premium-result">
                <div className="premium-label">Recommended Premium</div>
                <div className="premium-value">{fmt(prediction.final_premium)} DZD</div>
            </div>

            <div className="premium-details">
                <span>Base AI: {fmt(prediction.base_prediction)} DZD</span>
                <span>{prediction.zone_label}</span>
                <span>Multiplier: ×{prediction.multiplier}</span>
            </div>

            {prediction.hotspot_warning && (
                <div className={`alert alert-${prediction.hotspot_warning.level === 'CRITICAL' ? 'critical' : 'high'}`}>
                    <span className="alert-icon">
                        {prediction.hotspot_warning.level === 'CRITICAL' ? '🚨' : '⚠️'}
                    </span>
                    <div>
                        <strong>PORTFOLIO {prediction.hotspot_warning.level}:</strong>{' '}
                        {prediction.hotspot_warning.message}
                    </div>
                </div>
            )}
        </div>
    )
}
