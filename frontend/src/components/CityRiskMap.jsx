import { divIcon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'

const RISK_LABELS = {
  low: 'Low',
  caution: 'Caution',
  extreme_caution: 'Extreme caution',
  danger: 'Danger',
  extreme_danger: 'Extreme danger',
}

function MapFocus({ location }) {
  const map = useMap()
  const previousLocationId = useRef(location?.id)

  useEffect(() => {
    if (location && previousLocationId.current !== location.id) {
      previousLocationId.current = location.id
      map.flyTo([location.latitude, location.longitude], 7, {
        duration: 0.6,
      })
    }
  }, [location, map])

  return null
}

function CityRiskMap({ cities, selectedId, weatherById, onSelect }) {
  const markers = useMemo(
    () =>
      cities.map((city) => {
        const risk = weatherById[city.id]?.data?.current?.heat_risk?.risk_level
        const markerRisk = RISK_LABELS[risk] ? risk : 'unavailable'
        return {
          ...city,
          markerRisk,
          icon: divIcon({
            className: 'city-risk-marker-wrapper',
            html: `<span class="city-risk-marker risk-${markerRisk}"></span>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
          }),
        }
      }),
    [cities, weatherById],
  )

  const selectedLocation = cities.find((city) => city.id === selectedId)

  return (
    <MapContainer
      aria-label="Interactive city heat-risk map"
      center={[22.7, 79.0]}
      className="city-risk-map"
      maxZoom={12}
      minZoom={3}
      scrollWheelZoom
      zoom={4.5}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {selectedLocation && <MapFocus location={selectedLocation} />}
      {markers.map((city) => {
        const record = weatherById[city.id]
        const current = record?.data?.current
        const risk = current?.heat_risk
        const riskLabel = risk?.risk_level
          ? RISK_LABELS[risk.risk_level] ?? 'Unavailable'
          : 'Not applicable'
        return (
          <Marker
            alt={`${city.name}: ${riskLabel} indicative heat risk`}
            eventHandlers={{ click: () => onSelect(city.id) }}
            icon={city.icon}
            key={city.id}
            position={[city.latitude, city.longitude]}
            title={`${city.name} — ${riskLabel}`}
          >
            <Popup>
              <div className="map-popup">
                <strong>{city.name}</strong>
                <span>{[city.admin1, city.country].filter(Boolean).join(', ')}</span>
                {record?.loading ? (
                  <span>Loading current conditions…</span>
                ) : record?.error ? (
                  <span className="map-popup-error">Weather unavailable</span>
                ) : current ? (
                  <>
                    <span>
                      {current.temperature_c.toFixed(1)} °C air temperature
                    </span>
                    <span>
                      {risk?.heat_index_c == null
                        ? 'Heat Index not applicable'
                        : `${risk.heat_index_c.toFixed(1)} °C Heat Index · ${riskLabel}`}
                    </span>
                  </>
                ) : (
                  <span>Current conditions are not available.</span>
                )}
                <span className="map-popup-coordinates">
                  {city.latitude.toFixed(3)}°, {city.longitude.toFixed(3)}°
                </span>
              </div>
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}

export default CityRiskMap
