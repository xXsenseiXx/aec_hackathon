export default function PMLScenarios({ scenarios }) {
    if (!scenarios || scenarios.length === 0) {
        return <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No PML scenario data available</div>
    }

    const fmt = (n) => {
        const str = String(n).replace(',', '.')
        const num = parseFloat(str)
        if (isNaN(num)) return n
        if (num > 1e9) return (num / 1e9).toFixed(2) + 'B'
        if (num > 1e6) return (num / 1e6).toFixed(1) + 'M'
        if (num > 1e3) return (num / 1e3).toFixed(0) + 'K'
        return num.toFixed(0)
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {scenarios.map((s, i) => (
                <div key={i} className="pml-card">
                    <div className="pml-header">
                        <span className={`pml-zone-tag zone-${s.Focus_Zone}`}>{s.Focus_Zone}</span>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            M{String(s.Magnitude).replace(',', '.')}
                        </span>
                    </div>
                    <div className="pml-title">{s.Scenario_Name}</div>
                    <div className="pml-value">{fmt(s.Total_PML)} DZD</div>
                    <div className="pml-desc">
                        {s.Affected_Policies?.toLocaleString()} policies affected · {s.Description}
                    </div>
                </div>
            ))}
        </div>
    )
}
