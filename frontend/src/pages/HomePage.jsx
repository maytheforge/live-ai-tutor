import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const features = [
    {
        icon: '📊',
        title: 'Visual Diagrams',
        description: 'AI-generated flowcharts and mindmaps render instantly to visually explain complex science and math concepts.',
    },
    {
        icon: '🎤',
        title: 'Live Voice Tutoring',
        description: 'Speak and listen in real-time with Coach Leo as he guides you through your learning journey.',
    },
    {
        icon: '📷',
        title: 'Homework Vision',
        description: 'Point your camera at your homework or upload a photo — the tutor sees it and identifies the problem instantly.',
    },
    {
        icon: '📐',
        title: 'Shared Whiteboard',
        description: 'An interactive canvas available for you and Leo to sketch, highlight, and work through problems visually.',
    },
    {
        icon: '🤖',
        title: 'Solution Wrap-ups',
        description: 'Once you discover the solution, Leo provides a complete visual step-by-step summary for you to keep.',
    },
    {
        icon: '🧠',
        title: 'True Understanding',
        description: 'Focused on building genuine comprehension, prioritizing your discovery over immediate answers.',
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
                            <li><span className="check">✓</span> Live Voice Tutoring</li>
                            <li><span className="check">✓</span> Visual Diagrams & Shared Whiteboard</li>
                            <li><span className="check">✓</span> Live Solution Wrap-ups</li>
                        </ul>
                    </div>
                </section>
            </div>
        </div>
    );
}
