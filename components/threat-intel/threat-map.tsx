"use client"

import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup,
} from "react-19-simple-maps"
import type { Feature, Geometry } from "geojson"
import world from "world-atlas/countries-110m.json"

import type { ThreatEvent } from "@/lib/threat-data"

type MapGeo = Feature<Geometry> & {
  rsmKey: string
}

interface ThreatMapProps {
  events: ThreatEvent[]
  focus?: "world" | "africa"
  selected?: string
  onSelect: (id: string) => void
}

const MAP_CONFIG = {
  world: {
    scale: 130,
    center: [15, 8] as [number, number],
    height: 360,
  },
  africa: {
    scale: 280,
    center: [20, 2] as [number, number],
    height: 380,
  },
}

export function ThreatMap({
  events,
  focus = "world",
  selected,
  onSelect,
}: ThreatMapProps) {
  const config = MAP_CONFIG[focus]

  const getRadius = (event: ThreatEvent) => {
    if (selected === event.id) return 7
    return event.severity === "critical" ? 5 : 3.5
  }

  const getPulseRadius = (event: ThreatEvent) =>
    event.severity === "critical" ? 10 : 7

  const getColor = (event: ThreatEvent) =>
    event.severity === "critical"
      ? "var(--destructive)"
      : "var(--primary)"

  return (
    <div className="relative overflow-hidden rounded-lg border bg-background/70 scanline">
      <div className="absolute left-3 top-3 z-10 flex items-center gap-2 text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
        <span className="size-1.5 rounded-full bg-primary" />
        Geospatial Signal Layer
      </div>

      <ComposableMap
        projectionConfig={{ scale: config.scale }}
        height={config.height}
        aria-label={`${focus} threat activity map`}
      >
        <ZoomableGroup center={config.center} zoom={1}>
          <Geographies geography={world}>
            {({
              geographies,
            }: {
              geographies: MapGeo[]
            }) =>
              geographies.map((geo: MapGeo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="var(--muted)"
                  stroke="var(--border)"
                  strokeWidth={0.5}
                  style={{
                    default: {
                      outline: "none",
                    },
                    hover: {
                      fill: "var(--accent)",
                      outline: "none",
                    },
                    pressed: {
                      outline: "none",
                    },
                  }}
                />
              ))
            }
          </Geographies>

          {events.map((event) => {
            const color = getColor(event)

            return (
              <Marker
                key={event.id}
                coordinates={[event.longitude, event.latitude]}
              >
                <button
                  type="button"
                  onClick={() => onSelect(event.id)}
                  aria-label={`Select ${event.title}`}
                  className="focus:outline-none"
                >
                  <circle
                    r={getRadius(event)}
                    fill={color}
                    fillOpacity={0.85}
                    stroke="var(--background)"
                    strokeWidth={2}
                    className="cursor-pointer transition-all duration-300"
                  />

                  <circle
                    r={getPulseRadius(event)}
                    fill="none"
                    stroke={color}
                    opacity={0.32}
                  />
                </button>
              </Marker>
            )
          })}
        </ZoomableGroup>
      </ComposableMap>

      <div className="absolute bottom-3 right-3 rounded border bg-background/85 px-2 py-1 font-mono text-[10px] text-muted-foreground backdrop-blur-sm">
        {events.length} SIGNALS IN VIEW
      </div>
    </div>
  )
}