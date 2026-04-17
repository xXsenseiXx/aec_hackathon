import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { ScatterplotLayer } from '@deck.gl/layers'

const INITIAL_VIEW = {
    center: [3.0, 32.0],
    zoom: 4.5,
    pitch: 45,
    bearing: 0,
}

// Free dark tile style — no API key needed
const DARK_STYLE = {
    version: 8,
    sources: {
        'carto-dark': {
            type: 'raster',
            tiles: [
                'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
                'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
                'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            ],
            tileSize: 256,
            attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
        },
    },
    layers: [
        {
            id: 'carto-dark-layer',
            type: 'raster',
            source: 'carto-dark',
            minzoom: 0,
            maxzoom: 19,
        },
    ],
}

export default function SeismicMap({ wilayas, selectedWilaya }) {
    const containerRef = useRef(null)
    const mapRef = useRef(null)
    const overlayRef = useRef(null)

    // Initialize map once
    useEffect(() => {
        if (!containerRef.current) return

        const map = new maplibregl.Map({
            container: containerRef.current,
            style: DARK_STYLE,
            ...INITIAL_VIEW,
            attributionControl: false,
        })

        map.addControl(new maplibregl.NavigationControl(), 'top-left')

        const overlay = new MapboxOverlay({ layers: [] })
        map.addControl(overlay)

        mapRef.current = map
        overlayRef.current = overlay

        return () => {
            map.remove()
            mapRef.current = null
            overlayRef.current = null
        }
    }, [])

    // Update deck.gl layer when data changes
    useEffect(() => {
        if (!overlayRef.current || wilayas.length === 0) return

        // Radius comes from backend in METERS (35km, 25km, 15km, 10km)
        // so circles are tied to the earth and zoom with the map
        const layer = new ScatterplotLayer({
            id: 'wilayas',
            data: wilayas,
            pickable: true,

            opacity: 1,
            stroked: true,
            filled: true,
            radiusUnits: 'meters',

            getPosition: d => [d.lon, d.lat],

            // Shrink the physical radius slightly to reduce crazy overlaps
            getRadius: d => d.radius * 0.7,

            // FIX: Bypass the JSON string bug. We use the radius to determine the zone,
            // and manually pass beautiful Tailwind RGB colors with a very low Alpha (30 out of 255)
            getFillColor: d => {
                if (d.name === selectedWilaya) return [59, 130, 246, 100]; // Glowing Blue

                if (d.radius >= 30000) return [239, 68, 68, 30];    // Zone 3: Red (Glassy & Transparent)
                if (d.radius >= 20000) return [245, 158, 11, 30];   // Zone 2: Orange
                if (d.radius >= 12000) return [250, 204, 21, 30];   // Zone 1: Yellow
                return [16, 185, 129, 30];                          // Zone 0: Green
            },

            // FIX: Make the borders 100% solid (Alpha = 255). 
            // This is the secret to seeing overlapping zones clearly!
            getLineColor: d => {
                if (d.name === selectedWilaya) return [255, 255, 255, 255]; // Solid White

                if (d.radius >= 30000) return [239, 68, 68, 255];   // Solid Red Border
                if (d.radius >= 20000) return [245, 158, 11, 255];  // Solid Orange Border
                if (d.radius >= 12000) return [250, 204, 21, 255];  // Solid Yellow Border
                return [16, 185, 129, 255];                         // Solid Green Border
            },

            getLineWidth: d => d.name === selectedWilaya ? 4 : 2,
            lineWidthMinPixels: 2, // Keeps the borders visible even when zoomed out

            updateTriggers: {
                getFillColor: [selectedWilaya],
                getLineColor: [selectedWilaya],
                getLineWidth: [selectedWilaya],
            },
        })

        overlayRef.current.setProps({ layers: [layer] })
    }, [wilayas, selectedWilaya])

    return (
        <div className="map-container">
            <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
            <div className="map-legend">
                <div className="map-legend-item">
                    <span className="map-legend-dot" style={{ background: '#ef4444' }}></span>
                    Zone III — High
                </div>
                <div className="map-legend-item">
                    <span className="map-legend-dot" style={{ background: '#f59e0b' }}></span>
                    Zone II — Medium
                </div>
                <div className="map-legend-item">
                    <span className="map-legend-dot" style={{ background: '#facc15' }}></span>
                    Zone I — Low
                </div>
                <div className="map-legend-item">
                    <span className="map-legend-dot" style={{ background: '#10b981' }}></span>
                    Zone 0 — Very Low
                </div>
            </div>
        </div>
    )
}
