import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import PremiumCard from './components/PremiumCard'
import SeismicMap from './components/SeismicMap'
import MonteCarloChart from './components/MonteCarloChart'
import PMLScenarios from './components/PMLScenarios'
import HotspotsTable from './components/HotspotsTable'

const API = ''  // proxy through vite

export default function App() {
    // Input state
    const [buildingType, setBuildingType] = useState('Bien immobilier')
    const [wilaya, setWilaya] = useState('ALGER')
    const [commune, setCommune] = useState('ALGER')
    const [capitalAssure, setCapitalAssure] = useState(10000000)

    // Data state
    const [wilayas, setWilayas] = useState([])
    const [prediction, setPrediction] = useState(null)
    const [mcData, setMcData] = useState(null)
    const [mcLoading, setMcLoading] = useState(false)
    const [hotspots, setHotspots] = useState([])
    const [pmlScenarios, setPmlScenarios] = useState([])

    // Load static data
    useEffect(() => {
        fetch(`${API}/api/wilayas`).then(r => r.json()).then(setWilayas)
        fetch(`${API}/api/hotspots`).then(r => r.json()).then(setHotspots)
        fetch(`${API}/api/pml-scenarios`).then(r => r.json()).then(setPmlScenarios)
    }, [])

    // Real-time prediction on any input change
    const fetchPrediction = useCallback(async () => {
        try {
            const res = await fetch(`${API}/api/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: buildingType,
                    wilaya,
                    commune,
                    capital_assure: capitalAssure,
                }),
            })
            const data = await res.json()
            setPrediction(data)
        } catch (err) {
            console.error('Prediction error:', err)
        }
    }, [buildingType, wilaya, commune, capitalAssure])

    useEffect(() => {
        const timer = setTimeout(fetchPrediction, 200)
        return () => clearTimeout(timer)
    }, [fetchPrediction])

    // Monte Carlo simulation
    const runMonteCarlo = async () => {
        setMcLoading(true)
        try {
            const res = await fetch(`${API}/api/monte-carlo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wilaya, capital_assure: capitalAssure }),
            })
            const data = await res.json()
            setMcData(data)
        } catch (err) {
            console.error('Monte Carlo error:', err)
        }
        setMcLoading(false)
    }

    // Get zone for current wilaya
    const currentWilaya = wilayas.find(w => w.name === wilaya)
    const zone = currentWilaya?.zone ?? 0

    return (
        <div className="app-layout">
            <Sidebar
                buildingType={buildingType}
                setBuildingType={setBuildingType}
                wilaya={wilaya}
                setWilaya={setWilaya}
                commune={commune}
                setCommune={setCommune}
                capitalAssure={capitalAssure}
                setCapitalAssure={setCapitalAssure}
                wilayas={wilayas}
                zone={zone}
            />

            <main className="main-content">
                <div className="main-header">
                    <h2>🛡️ GAM CATNAT Risk Dashboard</h2>
                    <div className="header-badge">
                        <span className="live-dot"></span>
                        Powered by CatBoost AI &amp; RPA 99
                    </div>
                </div>

                <div className="grid-2">
                    <PremiumCard prediction={prediction} />
                    <div className="glass-card">
                        <div className="card-title">
                            <span className="card-icon">🗺️</span>
                            3D Seismic Risk Map — Algeria
                        </div>
                        <SeismicMap wilayas={wilayas} selectedWilaya={wilaya} />
                    </div>
                </div>

                <div className="grid-2">
                    <MonteCarloChart
                        mcData={mcData}
                        loading={mcLoading}
                        onRun={runMonteCarlo}
                        wilaya={wilaya}
                        zone={zone}
                    />
                    <div className="glass-card">
                        <div className="card-title">
                            <span className="card-icon">💥</span>
                            Probable Maximum Loss Scenarios
                        </div>
                        <PMLScenarios scenarios={pmlScenarios} />
                    </div>
                </div>

                <div className="glass-card">
                    <div className="card-title">
                        <span className="card-icon">📊</span>
                        Portfolio Concentration Hotspots
                    </div>
                    <HotspotsTable hotspots={hotspots} />
                </div>
            </main>
        </div>
    )
}
