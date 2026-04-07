import React, { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';

import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { fromLonLat } from 'ol/proj';

const MapComponent = () => {
    const mapRef = useRef(null);
    const [map, setMap] = useState(null);

    useEffect(() => {
        const osmLayer = new TileLayer({
            source: new OSM(),
        });

        const vectorSource = new VectorSource();
        const vectorLayer = new VectorLayer({
            source: vectorSource,
        });

        // Создание карты
        const initialMap = new Map({
            target: mapRef.current,
            layers: [osmLayer, vectorLayer],
            view: new View({
                center: fromLonLat([37.6176, 55.7558]), // Координаты центра (Москва)
                zoom: 10,
            }),
        });

        setMap(initialMap);

        // Очистка при размонтировании компонента
        return () => initialMap.setTarget(null);
    }, []);

// Функция для добавления маркера (точки)
const addMarker = (longitude, latitude, color = 'blue') => {
    if (!map) return;
    const vectorSource = map.getLayers().getArray()[1].getSource();

    const marker = new Feature({
        geometry: new Point(fromLonLat([longitude, latitude])),
    });

    marker.setStyle(new Style({
        image: new CircleStyle({
            radius: 8,
            fill: new Fill({ color: color }),
            stroke: new Stroke({ color: 'white', width: 2 }),
        }),
    }));

    vectorSource.addFeature(marker);
    return marker;
};

// Функция для построения маршрута между двумя точками
const buildRoute = async (startLonLat, endLonLat) => {
    if (!map) return;
    const vectorSource = map.getLayers().getArray()[1].getSource();

  // 1. Добавляем маркеры начала и конца
    const startMarker = addMarker(startLonLat[0], startLonLat[1], 'green');
    const endMarker = addMarker(endLonLat[0], endLonLat[1], 'red');

  // 2. Запрос к OSRM API для получения маршрута
    const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${startLonLat[0]},${startLonLat[1]};${endLonLat[0]},${endLonLat[1]}?overview=full&geometries=geojson`;

    try {
        const response = await fetch(osrmUrl);
        const data = await response.json();
        
        if (data.code === 'Ok') {
            const route = data.routes[0];
            const routeGeometry = route.geometry;
            
            // 3. Отображаем маршрут на карте
            const routeFeature = new Feature({
                geometry: new LineString(routeGeometry.coordinates.map(coord => fromLonLat(coord))),
            });
            
            routeFeature.setStyle(new Style({
                stroke: new Stroke({
                color: '#2563eb', // Синий цвет линии
                width: 5,
                }),
            }));
        
            vectorSource.addFeature(routeFeature);
        
        // 4. (Опционально) Подгоняем карту под маршрут
            const extent = routeFeature.getGeometry().getExtent();
            map.getView().fit(extent, { padding: [50, 50, 50, 50] });
            
            console.log(`Дистанция маршрута: ${(route.distance / 1000).toFixed(2)} км`);
        }
    } catch (error) {
        console.error('Ошибка при построении маршрута:', error);
    }
};
    return <div ref={mapRef} style={{ width: '100%', height: '500px' }} />;
};

export default MapComponent;