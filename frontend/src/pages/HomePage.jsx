import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const features = [
    {
        icon: '🎤',
        title: 'Live Voice Tutoring',
        description: 'Speak naturally with Coach Leo in real-time. The AI listens, understands, and guides you step by step.',
    },
    {
        icon: '🤔',
        title: 'Socratic Method',
        description: 'Coach Leo never just gives you the answer. It asks guiding questions to help you discover solutions yourself.',
    },
    {
        icon: '📷',
        title: 'Homework Vision',
        description: 'Point your camera at your homework or upload a photo — the tutor sees it and responds in context.',
    },
    {
        icon: '📐',
        title: 'Live Shared Canvas',
        description: 'Watch Coach Leo draw diagrams, equations, and visual aids on a shared Excalidraw board in real time.',
    },
    {
        icon: '🤖',
        title: 'Multi-Agent AI',
        description: 'Powered by Google ADK with specialised Canvas and Diagram sub-agents orchestrated intelligently.',
    },
    {
        icon: '🧠',
        title: 'Builds Real Understanding',
        description: 'Every interaction is designed to build genuine comprehension, not just rote memorisation.',
    },
];

export default function HomePage() {
    const navigate = useNavigate();

    const startSession = () => {
        navigate('/session');
    };

    return (
        <div className="home-container">
            {/* Animated background blobs */}
            <div className="bg-blob blob-1" />
            <div className="bg-blob blob-2" />
            <div className="bg-blob blob-3" />

            <div className="home-layout">
                {/* ── LEFT: Features ── */}
                <aside className="home-left">
                    <div className="home-brand">
                        <span className="brand-icon">✦</span>
                        <span className="brand-name">Live AI Tutor</span>
                    </div>

                    <h1 className="home-headline">
                        Your personal<br />
                        <span className="headline-accent">Socratic Mirror</span>
                    </h1>
                    <p className="home-subheadline">
                        Not just an answer machine — a coach that guides you to discover solutions yourself.
                    </p>

                    <div className="features-grid">
                        {features.map((f, i) => (
                            <div className="feature-card" key={i} style={{ '--delay': `${i * 80}ms` }}>
                                <span className="feature-icon">{f.icon}</span>
                                <div>
                                    <h3 className="feature-title">{f.title}</h3>
                                    <p className="feature-desc">{f.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </aside>

                {/* ── RIGHT: CTA ── */}
                <section className="home-right">
                    <div className="cta-card">
                        <div className="cta-avatar">
                            <div className="avatar-ring ring-1" />
                            <div className="avatar-ring ring-2" />
                            <div className="avatar-ring ring-3" />
                            <div className="avatar-core">
                                <span className="avatar-emoji">🎓</span>
                            </div>
                        </div>

                        <h2 className="cta-heading">Meet Coach Leo</h2>
                        <p className="cta-body">
                            Ready to think through your homework together?<br />
                            Just press start and Leo will be with you instantly.
                        </p>

                        <button className="start-btn" onClick={startSession}>
                            <span className="start-btn-icon">▶</span>
                            Start Live Session
                        </button>

                        <ul className="cta-checklist">
                            <li><span className="check">✓</span> Microphone turns on automatically</li>
                            <li><span className="check">✓</span> Camera preview ready to snapshot</li>
                            <li><span className="check">✓</span> Shared canvas opens instantly</li>
                        </ul>
                    </div>
                </section>
            </div>
        </div>
    );
}
