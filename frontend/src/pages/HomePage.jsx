import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const features = [
    {
        icon: '📊',
        title: 'Mermaid Diagrams',
        description: 'High-quality AI-generated flowcharts and mindmaps render instantly to visualize complex science and math concepts.',
    },
    {
        icon: '🎤',
        title: 'Voice Triage',
        description: 'Coach Leo speaks first to understand if you need Homework help or want to Learn a new topic, guiding your start.',
    },
    {
        icon: '📷',
        title: 'Homework Vision',
        description: 'Point your camera at your homework or upload a photo — the tutor sees it, confirms it, and responds in context.',
    },
    {
        icon: '🤔',
        title: 'Socratic Mirror',
        description: 'Coach Leo never just gives you the answer. It asks guiding questions to help you discover solutions yourself.',
    },
    {
        icon: '🤖',
        title: 'Solution Wrap-ups',
        description: 'Once you discover the solution, Leo provides a complete visual step-by-step summary in the Diagram tab.',
    },
    {
        icon: '🧠',
        title: 'True Understanding',
        description: 'Every interaction is designed to build genuine comprehension, prioritizing your discovery over rote engine answers.',
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
                            <li><span className="check">✓</span> Socratic Triage (Homework or Learning)</li>
                            <li><span className="check">✓</span> Mermaid Diagram & Shared Whiteboard</li>
                            <li><span className="check">✓</span> Live Solution Wrap-ups</li>
                        </ul>
                    </div>
                </section>
            </div>
        </div>
    );
}
