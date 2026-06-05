import { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';
import { Map, View, Feature } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import Point from 'ol/geom/Point';
import { Style, Icon } from 'ol/style';
import { fromLonLat, toLonLat } from 'ol/proj';
import markerIcon from '../assets/marker.png';

const MapComponent = () => {
    const mapRef = useRef();
    const [selectedCoords, setSelectedCoords] = useState(null);

    const markerRef = useRef(new Feature()); 

    useEffect(() => {
        markerRef.current.setStyle(
            new Style({
                image: new Icon({
                    anchor: [0.5, 1],
                    scale: 0.05,      
                    src: markerIcon, 
                }),
            })
        );
        const vectorSource = new VectorSource({
            features: [markerRef.current],
        });
        const vectorLayer = new VectorLayer({
            source: vectorSource,
        });

        const initialMap = new Map({
            target: mapRef.current,
            layers: [
                new TileLayer({ source: new OSM() }),
                vectorLayer,
            ],
            view: new View({
                center: fromLonLat([129.7322, 62.0339]), 
                zoom: 12,
            }),
        });

        initialMap.on('click', (event) => {
            const coords = event.coordinate; 
            markerRef.current.setGeometry(new Point(coords));
            const lonLat = toLonLat(coords);
            setSelectedCoords(lonLat);
        });

        return () => initialMap.setTarget(null);
    }, []);

    return (
        <div className="flex flex-col items-center p-4">
        <h2 className="text-xl font-bold mb-4">Выбор точки доставки (Якутск)</h2>
        
        <div 
            ref={mapRef} 
            className="w-full h-[500px] rounded-lg shadow-lg border border-gray-300 mb-4"
        ></div>

        {selectedCoords && (
            <div className="mt-4 p-3 bg-white border rounded-md shadow-sm">
                <p className="font-semibold text-sm">Точка доставки:</p>
                <div className="flex gap-4 mt-1">
                    <span><strong>Долгота:</strong> {selectedCoords[0].toFixed(6)}</span>
                    <span><strong>Широта:</strong> {selectedCoords[1].toFixed(6)}</span>
                </div>
            </div>
        )}
        </div>
    );
};
export default MapComponent;