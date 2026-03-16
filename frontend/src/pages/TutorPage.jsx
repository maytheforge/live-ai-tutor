/// <reference types="vite/client" />
import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { CanvasBoard } from '../components/CanvasBoard';
import MermaidPanel from '../components/MermaidPanel';
import { useGeminiLive } from '../hooks/useGeminiLive';
import { Video, Mic, Sparkles, Upload, ArrowLeft, BarChart2, PenTool } from 'lucide-react';
import '../App.css';

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

export default function TutorPage() {
    const navigate = useNavigate();
    const webcamRef = useRef(null);
    const uploadInputRef = useRef(null);
    const { isConnected, connect, disconnect, sendContext, sendToolResponse, toolCall, clearToolCall } = useGeminiLive(GEMINI_API_KEY);

    const [tutorMessage, setTutorMessage] = useState('Starting your session with Coach Leo...');
    const [externalCanvasActions, setExternalCanvasActions] = useState(null);
    const [lastSnapshot, setLastSnapshot] = useState(null);
    const [uploadedImage, setUploadedImage] = useState(null);

    // Mermaid diagram state
    const [mermaidDiagram, setMermaidDiagram] = useState(null); // { mermaid, title }
    const [activeTab, setActiveTab] = useState('diagram'); // 'diagram' | 'whiteboard'

    // Auto-start the voice session when this page mounts
    useEffect(() => {
        const timer = setTimeout(() => { connect(); }, 800);
        return () => clearTimeout(timer);
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Update greeting once connected
    useEffect(() => {
        if (isConnected) {
            setTutorMessage("Hi! I'm Coach Leo. Show me your homework on camera or upload a photo and let's get started!");
        }
    }, [isConnected]);

    // Handle tool calls coming from the Gemini Live audio agent
    useEffect(() => {
        if (!toolCall) return;

        const executeTool = async () => {
            if (toolCall.name === 'generate_diagram') {
                const { diagram_type, topic } = toolCall.args;
                const topicLabel = topic || diagram_type;

                setTutorMessage(`Drawing a diagram about ${topicLabel}...`);

                // Respond immediately to avoid 1008 disconnect
                sendToolResponse({
                    name: 'generate_diagram',
                    id: toolCall.id,
                    response: { result: { status: 'success', message: 'Diagram generation started.' } },
                });
                clearToolCall();

                try {
                    const backendUrl = `http://${window.location.hostname}:8000/interact`;
                    const response = await axios.post(backendUrl, {
                        student_id: 'demo_student',
                        message: `The user wants a diagram about: ${topicLabel}`,
                        request_diagram: topicLabel,  // human-readable topic (e.g. 'Water Cycle')
                    });
                    if (response.data.mermaid_diagram) {
                        setMermaidDiagram(response.data.mermaid_diagram);
                        setActiveTab('diagram');
                    } else if (response.data.canvas_action) {
                        setExternalCanvasActions(response.data.canvas_action);
                        setActiveTab('whiteboard');
                    }
                } catch (error) {
                    console.error('Error executing diagram tool:', error);
                }
            } else {
                clearToolCall();
            }
        };

        executeTool();
    }, [toolCall, sendToolResponse, clearToolCall]);

    const isLive = isConnected;

    const toggleVoice = () => { isLive ? disconnect() : connect(); };

    // Helper: apply API response to state
    const applyResponse = (data) => {
        if (data.vision_topic) {
            setTutorMessage(`I can see: "${data.vision_topic}". ${data.tutor_response || ''}`.trim());
        } else if (data.tutor_response) {
            setTutorMessage(data.tutor_response);
        }
        if (data.mermaid_diagram) {
            setMermaidDiagram(data.mermaid_diagram);
            setActiveTab('diagram');
        } else if (data.canvas_action && data.canvas_action.action !== 'noop') {
            setExternalCanvasActions(data.canvas_action);
            setActiveTab('whiteboard');
        }
    };

    // Webcam snapshot
    const captureAndUnderstand = useCallback(async () => {
        if (!webcamRef.current) return;
        const imageSrc = webcamRef.current.getScreenshot();
        if (!imageSrc) return;

        try {
            setTutorMessage('Analyzing your homework...');
            setLastSnapshot(imageSrc);
            setUploadedImage(null);

            const base64Image = imageSrc.split(',')[1];
            if (isLive) sendContext(base64Image);

            const backendUrl = `http://${window.location.hostname}:8000/interact`;
            const response = await axios.post(backendUrl, {
                student_id: 'demo_student',
                message: 'Can you help me with this problem?',
                image_data: base64Image,
            });
            applyResponse(response.data);
        } catch (error) {
            console.error('Error interacting with tutor:', error);
            setTutorMessage("Oops, I had trouble seeing that. Can you adjust the paper?");
        }
    }, [webcamRef, isLive, sendContext]);

    // File upload
    const handleFileUpload = useCallback(async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        e.target.value = '';

        const reader = new FileReader();
        reader.onload = async (loadEvent) => {
            const dataUrl = loadEvent.target.result;
            const base64Image = dataUrl.split(',')[1];

            setUploadedImage(dataUrl);
            setLastSnapshot(null);
            setTutorMessage('Analyzing your uploaded homework...');

            if (isLive) sendContext(base64Image);

            try {
                const backendUrl = `http://${window.location.hostname}:8000/interact`;
                const response = await axios.post(backendUrl, {
                    student_id: 'demo_student',
                    message: 'Can you help me with this problem?',
                    image_data: base64Image,
                });
                applyResponse(response.data);
            } catch (error) {
                console.error('Error sending uploaded image to tutor:', error);
                setTutorMessage("Oops, I had trouble reading that file. Please try another image.");
            }
        };
        reader.readAsDataURL(file);
    }, [isLive, sendContext]);

    return (
        <div className="app-container">
            {/* Header */}
            <header className="app-header">
                <div className="logo">
                    <button className="back-btn" onClick={() => { disconnect(); navigate('/'); }} title="Back to Home">
                        <ArrowLeft size={18} />
                    </button>
                    <Sparkles className="icon-gold" />
                    <h1>Live AI Tutor</h1>
                </div>
                <div className="status-indicators">
                    <span className={`status-dot ${isLive ? 'live' : 'offline'}`} />
                    {isLive ? 'Coach Leo: Active' : 'Coach Leo: Connecting...'}
                </div>
            </header>

            {/* Main Workspace */}
            <main className="workspace">
                {/* Left Panel */}
                <aside className="left-panel">
                    <div className="camera-container">
                        <Webcam
                            audio={false}
                            ref={webcamRef}
                            screenshotFormat="image/jpeg"
                            videoConstraints={{ facingMode: 'environment' }}
                            className="webcam-view"
                        />
                        <div className="camera-controls">
                            <button
                                className={`control-btn ${isLive ? 'active-red' : ''}`}
                                onClick={toggleVoice}
                                title={isLive ? 'Stop voice session' : 'Start voice session'}
                            >
                                <Mic size={20} />
                            </button>
                            <button className="control-btn primary" onClick={captureAndUnderstand} title="Take a snapshot">
                                <Video size={20} /> Snapshot
                            </button>
                            <button
                                className="control-btn upload-btn"
                                onClick={() => uploadInputRef.current?.click()}
                                title="Upload a homework photo"
                            >
                                <Upload size={20} /> Upload
                            </button>
                            <input
                                ref={uploadInputRef}
                                type="file"
                                accept="image/*"
                                style={{ display: 'none' }}
                                onChange={handleFileUpload}
                            />
                        </div>
                    </div>

                    <div className="tutor-chat">
                        <h3>Coach Leo</h3>
                        <div className="message-bubble">
                            <p>{tutorMessage}</p>
                        </div>
                        {(uploadedImage || lastSnapshot) && (
                            <div className="snapshot-context">
                                <h4>{uploadedImage ? 'Uploaded Homework:' : 'Context Shared with Tutor:'}</h4>
                                <img
                                    src={uploadedImage || lastSnapshot}
                                    alt="Homework Context"
                                    className="snapshot-thumbnail"
                                />
                            </div>
                        )}
                    </div>
                </aside>

                {/* Right Panel: Tabbed — Diagram | Whiteboard */}
                <section className="right-panel">
                    {/* Tab bar */}
                    <div className="panel-tabs">
                        <button
                            className={`tab-btn ${activeTab === 'diagram' ? 'tab-active' : ''}`}
                            onClick={() => setActiveTab('diagram')}
                        >
                            <BarChart2 size={15} /> Diagram
                            {mermaidDiagram && <span className="tab-badge" />}
                        </button>
                        <button
                            className={`tab-btn ${activeTab === 'whiteboard' ? 'tab-active' : ''}`}
                            onClick={() => setActiveTab('whiteboard')}
                        >
                            <PenTool size={15} /> Whiteboard
                        </button>
                    </div>

                    {/* Tab content */}
                    <div className="canvas-wrapper">
                        {activeTab === 'diagram' ? (
                            <MermaidPanel
                                mermaidCode={mermaidDiagram?.mermaid}
                                title={mermaidDiagram?.title}
                            />
                        ) : (
                            <CanvasBoard externalActions={externalCanvasActions} />
                        )}
                    </div>
                </section>
            </main>
        </div>
    );
}
