import { useEffect, useRef } from 'react'

function getColor(loss, maxLoss) {
    const t = loss / maxLoss
    if (t > 0.7) return '#ef4444'
    if (t > 0.4) return '#f59e0b'
    if (t > 0.2) return '#facc15'
    return '#10b981'
}

function drawScatterCircle(canvas, losses) {
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1
    const size = 280
    canvas.width = size * dpr
    canvas.height = size * dpr
    canvas.style.width = size + 'px'
    canvas.style.height = size + 'px'
    ctx.scale(dpr, dpr)

    const cx = size / 2
    const cy = size / 2
    const radius = size / 2 - 10
    const maxLoss = Math.max(...losses)

    // Clear
    ctx.clearRect(0, 0, size, size)

    // Outer ring glow
    const glow = ctx.createRadialGradient(cx, cy, radius - 5, cx, cy, radius + 5)
    glow.addColorStop(0, 'rgba(59, 130, 246, 0.15)')
    glow.addColorStop(1, 'transparent')
    ctx.fillStyle = glow
    ctx.fillRect(0, 0, size, size)

    // Circle border
    ctx.beginPath()
    ctx.arc(cx, cy, radius, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(100, 140, 255, 0.3)'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // Inner dark fill
    ctx.beginPath()
    ctx.arc(cx, cy, radius - 1, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(10, 14, 26, 0.6)'
    ctx.fill()

    // Scatter dots inside circle
    const n = Math.min(losses.length, 800)
    const step = Math.max(1, Math.floor(losses.length / n))

    for (let i = 0; i < losses.length; i += step) {
        // Random position inside circle using rejection sampling
        let x, y
        do {
            x = (Math.random() * 2 - 1) * (radius - 8)
            y = (Math.random() * 2 - 1) * (radius - 8)
        } while (x * x + y * y > (radius - 8) * (radius - 8))

        const loss = losses[i]
        const color = getColor(loss, maxLoss)
        const dotSize = 2 + (loss / maxLoss) * 3

        ctx.beginPath()
        ctx.arc(cx + x, cy + y, dotSize, 0, Math.PI * 2)
        ctx.fillStyle = color
        ctx.globalAlpha = 0.75
        ctx.fill()
    }
    ctx.globalAlpha = 1

    // Center label
    ctx.fillStyle = '#f0f4ff'
    ctx.font = '600 11px Inter'
    ctx.textAlign = 'center'
    ctx.fillText('MONTE CARLO', cx, cy - 6)
    ctx.font = '800 14px Inter'
    ctx.fillText(`${losses.length} sims`, cx, cy + 12)
}

export default function MonteCarloChart({ mcData, loading, onRun, wilaya, zone }) {
    const canvasRef = useRef(null)

    useEffect(() => {
        if (mcData && canvasRef.current) {
            drawScatterCircle(canvasRef.current, mcData.losses)
        }
    }, [mcData])

    const fmt = (n) => new Intl.NumberFormat('fr-DZ', { maximumFractionDigits: 0 }).format(n)

    return (
        <div className="glass-card">
            <div className="card-title">
                <span className="card-icon">🎲</span>
                Monte Carlo Disaster Simulation
            </div>

            <div className="monte-carlo-viz">
                {mcData ? (
                    <>
                        <div className="mc-circle-container">
                            <canvas ref={canvasRef} />
                        </div>
                        <div className="mc-stats">
                            <div className="mc-stat">
                                <div className="mc-stat-label">Average Loss</div>
                                <div className="mc-stat-value avg">{fmt(mcData.avg_loss)} DZD</div>
                            </div>
                            <div className="mc-stat">
                                <div className="mc-stat-label">95th Percentile</div>
                                <div className="mc-stat-value worst">{fmt(mcData.worst_case_95)} DZD</div>
                            </div>
                            <div className="mc-stat">
                                <div className="mc-stat-label">Median Loss</div>
                                <div className="mc-stat-value median">{fmt(mcData.median_loss)} DZD</div>
                            </div>
                            <div className="mc-stat">
                                <div className="mc-stat-label">Simulations</div>
                                <div className="mc-stat-value simulations">{mcData.n_simulations.toLocaleString()}</div>
                            </div>
                        </div>
                    </>
                ) : (
                    <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                        <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎯</div>
                        <p style={{ fontSize: '13px', maxWidth: '240px', margin: '0 auto', lineHeight: 1.6 }}>
                            Simulate 1,000 random earthquake events in <strong style={{ color: 'var(--text-primary)' }}>{wilaya}</strong> to
                            predict GAM's potential financial loss.
                        </p>
                    </div>
                )}

                <button className="run-btn" onClick={onRun} disabled={loading}>
                    {loading ? 'Simulating...' : '⚡ Run Simulation'}
                </button>
            </div>
        </div>
    )
}
