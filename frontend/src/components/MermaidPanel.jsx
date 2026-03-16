import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import './MermaidPanel.css';

// Initialise mermaid once
mermaid.initialize({
    startOnLoad: false,
    theme: 'neutral',
    fontFamily: 'Inter, -apple-system, sans-serif',
    fontSize: 14,
    flowchart: { curve: 'basis', padding: 20 },
    securityLevel: 'loose',
});

let _diagramCounter = 0;

export default function MermaidPanel({ mermaidCode, title }) {
    const containerRef = useRef(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!mermaidCode || !containerRef.current) return;

        const renderDiagram = async () => {
            setLoading(true);
            setError(null);
            const id = `mermaid-diagram-${++_diagramCounter}`;
            try {
                const { svg } = await mermaid.render(id, mermaidCode);
                if (containerRef.current) {
                    containerRef.current.innerHTML = svg;
                }
            } catch (err) {
                console.error('[MermaidPanel] Render error:', err);
                setError('Could not render diagram. The AI may have produced invalid syntax.');
            } finally {
                setLoading(false);
            }
        };

        renderDiagram();
    }, [mermaidCode]);

    if (!mermaidCode) {
        return (
            <div className="mermaid-placeholder">
                <div className="placeholder-icon">📊</div>
                <p>Ask Coach Leo to draw a diagram and it will appear here.</p>
                <p className="placeholder-hint">
                    Try: <em>"Can you draw a diagram of the water cycle?"</em>
                </p>
            </div>
        );
    }

    return (
        <div className="mermaid-panel">
            {title && <h3 className="mermaid-title">{title}</h3>}
            {loading && <div className="mermaid-loading">Rendering diagram…</div>}
            {error && <div className="mermaid-error">{error}</div>}
            <div className="mermaid-svg-container" ref={containerRef} />
        </div>
    );
}
