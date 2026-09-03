import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Route, Trip, RouteStop } from '../../types';
import { Bus as BusIcon, Navigation, MapPin, Maximize2, ShieldCheck, Clock, Users, Gauge } from 'lucide-react';

interface LiveBusMapProps {
  routes: Route[];
  activeTrips: Trip[];
  selectedRouteId?: string;
  selectedTripId?: string;
  onSelectRoute?: (routeId: string) => void;
  onSelectTrip?: (tripId: string) => void;
  heightClass?: string;
  showAllRoutesDefault?: boolean;
}

export const LiveBusMap: React.FC<LiveBusMapProps> = ({
  routes,
  activeTrips,
  selectedRouteId,
  selectedTripId,
  onSelectRoute,
  onSelectTrip,
  heightClass = 'h-[500px]',
  showAllRoutesDefault = true
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const routeLayersRef = useRef<L.LayerGroup | null>(null);
  const stopMarkersRef = useRef<L.LayerGroup | null>(null);
  const busMarkersRef = useRef<L.LayerGroup | null>(null);

  const [activeFilterRouteId, setActiveFilterRouteId] = useState<string>(selectedRouteId || 'all');
  const [selectedBusDetail, setSelectedBusDetail] = useState<Trip | null>(null);

  // Synchronize prop updates
  useEffect(() => {
    if (selectedRouteId) {
      setActiveFilterRouteId(selectedRouteId);
    }
  }, [selectedRouteId]);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [12.9716, 77.5946],
        zoom: 14,
        zoomControl: false,
        attributionControl: true
      });

      // Add high-contrast, clean dark CartoDB tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      }).addTo(map);

      // Zoom control bottom-right
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      routeLayersRef.current = L.layerGroup().addTo(map);
      stopMarkersRef.current = L.layerGroup().addTo(map);
      busMarkersRef.current = L.layerGroup().addTo(map);

      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Route Polylines and Stops
  useEffect(() => {
    if (!mapInstanceRef.current || !routeLayersRef.current || !stopMarkersRef.current) return;

    routeLayersRef.current.clearLayers();
    stopMarkersRef.current.clearLayers();

    const displayedRoutes = activeFilterRouteId === 'all'
      ? routes
      : routes.filter(r => r.id === activeFilterRouteId);

    const allCoords: [number, number][] = [];

    displayedRoutes.forEach(route => {
      if (route.pathCoordinates && route.pathCoordinates.length > 0) {
        // Draw route polyline with outer glow + core line
        const polylineBg = L.polyline(route.pathCoordinates, {
          color: route.color || '#3b82f6',
          weight: 7,
          opacity: 0.35,
          lineCap: 'round',
          lineJoin: 'round'
        });

        const polylineCore = L.polyline(route.pathCoordinates, {
          color: route.color || '#3b82f6',
          weight: 4,
          opacity: 0.9,
          dashArray: '8, 8',
          lineCap: 'round'
        });

        polylineCore.bindTooltip(`<b>${route.routeNumber}</b>: ${route.name}`, {
          sticky: true,
          className: 'bg-slate-800 text-slate-900 border-gray-200 px-2 py-1 rounded shadow-sm text-xs'
        });

        polylineCore.on('click', () => {
          if (onSelectRoute) onSelectRoute(route.id);
          setActiveFilterRouteId(route.id);
        });

        polylineBg.addTo(routeLayersRef.current!);
        polylineCore.addTo(routeLayersRef.current!);

        route.pathCoordinates.forEach(coord => allCoords.push(coord));
      }

      // Draw stops
      route.stops.forEach((stop, index) => {
        const isSelected = stop.sequence === 1 || stop.isCampusGate;
        const iconHtml = `
          <div class="flex items-center justify-center">
            <div class="w-6 h-6 rounded-full bg-slate-800 border-2 shadow-md flex items-center justify-center text-[10px] font-bold text-slate-900 transition-transform hover:scale-125" style="border-color: ${route.color || '#3b82f6'};">
              ${stop.sequence}
            </div>
          </div>
        `;

        const customIcon = L.divIcon({
          html: iconHtml,
          className: 'custom-stop-marker',
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        });

        const marker = L.marker([stop.latitude, stop.longitude], { icon: customIcon });

        const popupContent = `
          <div class="p-2 min-w-[180px] text-slate-200 font-sans">
            <div class="flex items-center gap-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              <span class="w-2 h-2 rounded-full" style="background-color: ${route.color};"></span>
              ${route.routeNumber} • Stop #${stop.sequence}
            </div>
            <div class="text-sm font-bold text-slate-900 mb-1">${stop.stopName}</div>
            <div class="text-xs text-slate-600 mb-2">${stop.landmark}</div>
            <div class="bg-slate-100 p-1.5 rounded text-[11px] flex justify-between items-center text-slate-300 font-mono">
              <span>Code: <b>${stop.code}</b></span>
              <span>+${stop.scheduledArrivalDeltaMin} min</span>
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);
        marker.addTo(stopMarkersRef.current!);
      });
    });

    // Adjust bounds if we have coordinates
    if (allCoords.length > 0 && activeFilterRouteId !== 'all') {
      try {
        const bounds = L.latLngBounds(allCoords);
        mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40] });
      } catch (e) {
        // ignore bounds calculation error
      }
    }
  }, [routes, activeFilterRouteId]);

  // Update Live Buses
  useEffect(() => {
    if (!mapInstanceRef.current || !busMarkersRef.current) return;

    busMarkersRef.current.clearLayers();

    const displayedTrips = activeFilterRouteId === 'all'
      ? activeTrips
      : activeTrips.filter(t => t.routeId === activeFilterRouteId);

    displayedTrips.forEach(trip => {
      if (trip.currentLatitude === undefined || trip.currentLongitude === undefined) return;

      const route = routes.find(r => r.id === trip.routeId);
      const routeColor = route?.color || '#10b981';
      const heading = trip.heading || 0;
      const isSelected = selectedTripId === trip.id;

      const busIconHtml = `
        <div class="relative flex items-center justify-center cursor-pointer group">
          <!-- Radar Pulse -->
          <div class="absolute w-12 h-12 rounded-full bg-emerald-500/30 animate-ping"></div>
          
          <!-- Outer Ring with heading arrow -->
          <div class="relative w-10 h-10 rounded-full bg-slate-800 border-2 ${isSelected ? 'border-amber-400 ring-4 ring-amber-400/40' : 'border-emerald-400'} shadow-sm flex items-center justify-center text-slate-900 transition-all transform hover:scale-110">
            <svg class="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M8 6v6"></path>
              <path d="M15 6v6"></path>
              <path d="M2 12h19.6"></path>
              <path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"></path>
              <circle cx="7" cy="18" r="2"></circle>
              <circle cx="17" cy="18" r="2"></circle>
            </svg>
            
            <!-- Direction Indicator Indicator -->
            <div class="absolute -top-1.5 w-3 h-3 bg-emerald-400 rounded-full border border-slate-900 shadow transform" style="transform: rotate(${heading}deg) translateY(-8px);"></div>
          </div>

          <!-- Bus Number Tag -->
          <div class="absolute -bottom-5 whitespace-nowrap bg-slate-800/90 text-emerald-300 text-[10px] font-bold px-1.5 py-0.5 rounded shadow border border-emerald-500/40">
            ${trip.busNumber} • ${trip.speedKmH || 0} km/h
          </div>
        </div>
      `;

      const busDivIcon = L.divIcon({
        html: busIconHtml,
        className: 'custom-bus-marker',
        iconSize: [44, 44],
        iconAnchor: [22, 22]
      });

      const marker = L.marker([trip.currentLatitude, trip.currentLongitude], { icon: busDivIcon, zIndexOffset: 1000 });

      marker.on('click', () => {
        setSelectedBusDetail(trip);
        if (onSelectTrip) onSelectTrip(trip.id);
      });

      marker.addTo(busMarkersRef.current!);
    });
  }, [activeTrips, activeFilterRouteId, selectedTripId, routes]);

  const handleCenterCampus = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([12.9716, 77.5946], 14);
    }
  };

  const handleFocusBus = (trip: Trip) => {
    if (mapInstanceRef.current && trip.currentLatitude && trip.currentLongitude) {
      mapInstanceRef.current.setView([trip.currentLatitude, trip.currentLongitude], 16, {
        animate: true
      });
      setSelectedBusDetail(trip);
      if (onSelectTrip) onSelectTrip(trip.id);
    }
  };

  if (!routes || routes.length === 0) {
    return (
      <div className={`relative w-full rounded-lg border border-gray-200 bg-slate-900 flex items-center justify-center flex-col text-slate-400 ${heightClass}`}>
        <MapPin className="w-12 h-12 mb-3 text-slate-300" />
        <h3 className="font-semibold text-lg text-slate-600 mb-1">No live map data available</h3>
        <p className="text-sm">Route and GPS information will appear here once configured.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full rounded-lg overflow-hidden border border-gray-200 bg-slate-900 shadow-sm flex flex-col">
      {/* Top Map Action Bar */}
      <div className="bg-slate-800/95 backdrop-blur-md px-4 py-3 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3 z-10">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500 "></div>
          <span className="font-semibold text-sm text-slate-900 tracking-wide">Live Campus Radar</span>
          <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-200 text-[11px] font-mono px-2 py-0.5 rounded-full">
            {activeTrips.length} Active Bus GPS Streams
          </span>
        </div>

        {/* Route Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 text-xs">
          <button
            id="map-filter-all"
            onClick={() => setActiveFilterRouteId('all')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              activeFilterRouteId === 'all'
                ? 'bg-emerald-500 text-white shadow-md shadow-sm'
                : 'bg-slate-800 text-slate-600 hover:text-slate-900 hover:bg-slate-900'
            }`}
          >
            All Routes
          </button>
          {routes.map(r => (
            <button
              key={r.id}
              id={`map-filter-${r.id}`}
              onClick={() => setActiveFilterRouteId(r.id)}
              className={`px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all whitespace-nowrap ${
                activeFilterRouteId === r.id
                  ? 'bg-slate-100 text-slate-900 shadow-md font-semibold'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-900'
              }`}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: r.color }}></span>
              {r.routeNumber}
            </button>
          ))}
        </div>

        {/* Map Utility Controls */}
        <div className="flex items-center gap-2">
          <button
            id="btn-center-campus"
            onClick={handleCenterCampus}
            className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-900 text-slate-300 rounded-lg flex items-center gap-1 transition-colors border border-gray-200"
            title="Fit Campus View"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span>Reset View</span>
          </button>
        </div>
      </div>

      {/* Leaflet Map Stage */}
      <div id="campus-live-leaflet-map" ref={mapContainerRef} className={`w-full ${heightClass} relative z-0`} />

      {/* Active Bus Quick Selector Bar (Bottom Overlay) */}
      {activeTrips.length > 0 && (
        <div className="bg-slate-800/90 backdrop-blur-md px-4 py-2.5 border-t border-gray-200/80 flex items-center gap-3 overflow-x-auto">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 shrink-0 flex items-center gap-1">
            <BusIcon className="w-3.5 h-3.5 text-emerald-400" />
            Live Buses:
          </span>
          <div className="flex items-center gap-2">
            {activeTrips.map(trip => (
              <button
                key={trip.id}
                id={`btn-focus-bus-${trip.id}`}
                onClick={() => handleFocusBus(trip)}
                className={`px-3 py-1.5 rounded-xl text-xs flex items-center gap-2 transition-all border shrink-0 ${
                  selectedBusDetail?.id === trip.id
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200'
                    : 'bg-slate-800/70 border-gray-200 text-slate-300 hover:bg-slate-900'
                }`}
              >
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
                <span className="font-bold">{trip.busNumber}</span>
                <span className="text-[11px] text-slate-600 font-mono">({trip.speedKmH || 0} km/h)</span>
                <span className="text-[10px] bg-slate-900 px-1.5 py-0.5 rounded text-slate-300">{trip.routeNumber}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Selected Bus Inspection Drawer */}
      {selectedBusDetail && (
        <div className="absolute bottom-16 left-4 right-4 md:right-auto md:w-96 bg-slate-800/95 backdrop-blur-xl border border-gray-200/80 p-4 rounded-lg shadow-sm text-slate-900 z-20 transition-all animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold">
                <BusIcon className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-900 flex items-center gap-1.5">
                  {selectedBusDetail.busNumber}
                  <span className="text-xs font-normal text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                    Live GPS
                  </span>
                </h4>
                <p className="text-xs text-slate-600">{selectedBusDetail.routeName}</p>
              </div>
            </div>
            <button
              onClick={() => setSelectedBusDetail(null)}
              className="text-slate-600 hover:text-slate-900 text-sm p-1 rounded hover:bg-slate-800"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-3 gap-2 my-3 text-center">
            <div className="bg-slate-800/80 p-2 rounded-xl border border-gray-200/60">
              <div className="text-[10px] uppercase tracking-wider text-slate-600 flex items-center justify-center gap-1 mb-0.5">
                <Gauge className="w-3 h-3 text-emerald-400" /> Speed
              </div>
              <div className="font-mono font-bold text-sm text-emerald-300">{selectedBusDetail.speedKmH || 0} <span className="text-[10px] font-normal text-slate-600">km/h</span></div>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-xl border border-gray-200/60">
              <div className="text-[10px] uppercase tracking-wider text-slate-600 flex items-center justify-center gap-1 mb-0.5">
                <Clock className="w-3 h-3 text-amber-400" /> Delay
              </div>
              <div className={`font-mono font-bold text-sm ${selectedBusDetail.delayMinutes > 2 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {selectedBusDetail.delayMinutes > 0 ? `+${selectedBusDetail.delayMinutes}m` : 'On Time'}
              </div>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-xl border border-gray-200/60">
              <div className="text-[10px] uppercase tracking-wider text-slate-600 flex items-center justify-center gap-1 mb-0.5">
                <Clock className="w-3 h-3 text-sky-400" /> ETA
              </div>
              <div className="font-mono font-bold text-sm text-sky-400">
                {selectedBusDetail.delayMinutes > 0 ? `${selectedBusDetail.delayMinutes + 5} min` : 'ETA unavailable'}
              </div>
            </div>
          </div>

          <div className="text-xs bg-slate-900/80 p-2.5 rounded-xl border border-gray-200 mb-3 space-y-1">
            <div className="flex justify-between text-slate-600">
              <span>Status:</span>
              <span className="font-medium capitalize text-emerald-600 font-bold">{selectedBusDetail.status.replace('_', ' ')}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Driver:</span>
              <span className="font-medium text-slate-800">{selectedBusDetail.driverName}</span>
            </div>
            <div className="flex justify-between text-slate-600 border-t border-gray-200 pt-1 mt-1">
              <span>Current Stop:</span>
              <span className="font-medium text-slate-800 text-right">
                {routes.find(r => r.id === selectedBusDetail.routeId)?.stops[selectedBusDetail.currentStopIndex]?.stopName || `Stop #${selectedBusDetail.currentStopIndex + 1}`}
              </span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Next Stop:</span>
              <span className="font-medium text-slate-800 text-right">
                {routes.find(r => r.id === selectedBusDetail.routeId)?.stops[selectedBusDetail.nextStopIndex]?.stopName || `Stop #${selectedBusDetail.nextStopIndex + 1}`}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleFocusBus(selectedBusDetail)}
              className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-sm shadow-sm"
            >
              <Navigation className="w-3.5 h-3.5" />
              Center Camera on Bus
            </button>
          </div>
        </div>
      )}

      {/* Privacy Guarantee Floating Tag */}
      <div className="absolute top-16 right-4 bg-slate-800/90 backdrop-blur-md border border-gray-200/80 px-3 py-1.5 rounded-full shadow-sm flex items-center gap-1.5 text-[11px] text-slate-300 pointer-events-none z-10">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>Student & Staff GPS: <strong className="text-emerald-400">0% Tracked</strong></span>
      </div>
    </div>
  );
};
