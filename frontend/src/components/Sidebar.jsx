const ZONE_LABELS = {
    0: 'Zone 0 — Very Low Risk',
    1: 'Zone I — Low Risk',
    2: 'Zone II — Medium Risk',
    3: 'Zone III — High Risk',
}

const BUILDING_TYPES = [
    'Bien immobilier',
    '2 - Installation Commerciale',
    '1 - Installation Industrielle',
]

export default function Sidebar({
    buildingType, setBuildingType,
    wilaya, setWilaya,
    commune, setCommune,
    capitalAssure, setCapitalAssure,
    wilayas, zone,
}) {
    const wilayaNames = wilayas.map(w => w.name).sort()

    const formatDZD = (val) => {
        return new Intl.NumberFormat('fr-DZ').format(val) + ' DZD'
    }

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon">G</div>
                <h1>
                    GAM Assurances
                    <span>CATNAT Risk Engine</span>
                </h1>
            </div>

            <div className="sidebar-section">
                <label>Building Type</label>
                <select value={buildingType} onChange={e => setBuildingType(e.target.value)}>
                    {BUILDING_TYPES.map(t => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </select>
            </div>

            <div className="sidebar-section">
                <label>Wilaya</label>
                <select value={wilaya} onChange={e => { setWilaya(e.target.value); setCommune(e.target.value) }}>
                    {wilayaNames.map(w => (
                        <option key={w} value={w}>{w}</option>
                    ))}
                </select>
            </div>

            <div className="sidebar-section">
                <label>Commune</label>
                <input
                    type="text"
                    value={commune}
                    onChange={e => setCommune(e.target.value)}
                    placeholder="Enter commune name"
                />
            </div>

            <div className="sidebar-section">
                <label>Capital Assuré</label>
                <div className="capital-display">{formatDZD(capitalAssure)}</div>
                <input
                    type="range"
                    className="capital-slider"
                    min={100000}
                    max={500000000}
                    step={100000}
                    value={capitalAssure}
                    onChange={e => setCapitalAssure(Number(e.target.value))}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>100K</span>
                    <span>500M</span>
                </div>
            </div>

            <div className={`zone-badge zone-${zone}`}>
                <span className="zone-dot"></span>
                <div>
                    <div style={{ fontSize: '11px', fontWeight: 400, opacity: 0.7 }}>RPA 99 Seismic Zone</div>
                    <div>{ZONE_LABELS[zone]}</div>
                </div>
            </div>
        </aside>
    )
}
