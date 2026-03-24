import React, { useState, useEffect } from 'react';
import { Excalidraw } from '@excalidraw/excalidraw';
import '@excalidraw/excalidraw/index.css'; // Add explicit CSS import

export const CanvasBoard = ({ onInteraction, externalActions }) => {
    const [excalidrawAPI, setExcalidrawAPI] = useState(null);

    useEffect(() => {
        if (!excalidrawAPI || !externalActions) return;

        // When the backend sends an action (like upserting an element)
        if (externalActions.action === 'upsert' && externalActions.elements) {
            excalidrawAPI.updateScene({
                elements: externalActions.elements
            });
        }
    }, [externalActions, excalidrawAPI]);

    return (
        <div style={{ height: '100%', width: '100%' }}>
            <Excalidraw
                excalidrawAPI={(api) => setExcalidrawAPI(api)}
                onChange={(elements, state) => {
                    if (onInteraction) {
                        onInteraction(elements, state);
                    }
                }}
                UIOptions={{
                    canvasActions: {
                        changeViewBackgroundColor: false,
                        clearCanvas: true,
                        loadScene: false,
                        export: false,
                        saveToActiveFile: false,
                        toggleTheme: true,
                        saveAsImage: false,
                    },
                }}
            />
        </div>
    );
};
