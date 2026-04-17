export default function HotspotsTable({ hotspots }) {
    if (!hotspots || hotspots.length === 0) {
        return <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No hotspot data available</div>
    }

    const getFlagClass = (flag) => {
        const f = String(flag)
        if (f.includes('CRITICAL')) return 'flag-critical'
        if (f.includes('HIGH')) return 'flag-high'
        return 'flag-ok'
    }

    const getFlagLabel = (flag) => {
        const f = String(flag)
        if (f.includes('CRITICAL')) return '🚨 CRITICAL'
        if (f.includes('HIGH')) return '⚠️ HIGH'
        return '✓ OK'
    }

    return (
        <div style={{ overflowX: 'auto' }}>
            <table className="hotspot-table">
                <thead>
                    <tr>
                        <th>Wilaya</th>
                        <th>Commune</th>
                        <th>Zone</th>
                        <th>Policies</th>
                        <th>% Capital</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {hotspots.map((h, i) => (
                        <tr key={i}>
                            <td>{h.WILAYA}</td>
                            <td>{h.COMMUNE}</td>
                            <td>{h.ZONE_SISMIQUE}</td>
                            <td>{h.Policy_Count}</td>
                            <td>{h.Pct_Total_Capital}%</td>
                            <td className={getFlagClass(h.Concentration_Flag)}>
                                {getFlagLabel(h.Concentration_Flag)}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
