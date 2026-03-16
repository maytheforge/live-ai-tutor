/// <reference types="vite/client" />
import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { CanvasBoard } from '../components/CanvasBoard';
import { useGeminiLive } from '../hooks/useGeminiLive';
import { Video, Mic, Share2, Sparkles, Upload, ArrowLeft } from 'lucide-react';
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

    // Auto-start the voice session when this page mounts
    useEffect(() => {
        const timer = setTimeout(() => {
            connect();
        }, 800); // slight delay so webcam can initialize
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
                const args = toolCall.args;
                const diagramType = args.diagram_type;
                const topic = args.topic || args.diagram_type;

                console.log('Gemini asked to draw diagram:', diagramType, 'about:', topic);
                setTutorMessage(`Drawing a diagram about ${topic}...`);

                // Respond to Gemini IMMEDIATELY to avoid 1008 disconnect
                sendToolResponse({
                    name: 'generate_diagram',
                    id: toolCall.id,
                    response: {
                        result: {
                            status: 'success',
                            message: 'Diagram generation started. Remind the user it might take a few seconds to appear.',
                        },
                    },
                });
                clearToolCall();

                try {
                    const backendUrl = `http://${window.location.hostname}:8000/interact`;
                    const response = await axios.post(backendUrl, {
                        student_id: 'demo_student',
                        message: `The user wants a diagram about: ${topic}`,
                        request_diagram: diagramType,
                    });
                    if (response.data.canvas_action) {
                        setExternalCanvasActions(response.data.canvas_action);
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

    const toggleVoice = () => {
        if (isLive) {
            disconnect();
        } else {
            connect();
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

            // Show the detected topic first, then the Socratic response
            if (response.data.vision_topic) {
                setTutorMessage(`I can see: "${response.data.vision_topic}". ${response.data.tutor_response || ''}`.trim());
            } else if (response.data.tutor_response) {
                setTutorMessage(response.data.tutor_response);
            }
            if (response.data.canvas_action) setExternalCanvasActions(response.data.canvas_action);
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
                // Show the detected topic alongside the Socratic response
                if (response.data.vision_topic) {
                    setTutorMessage(`I can see: "${response.data.vision_topic}". ${response.data.tutor_response || ''}`.trim());
                } else if (response.data.tutor_response) {
                    setTutorMessage(response.data.tutor_response);
                }
                if (response.data.canvas_action) setExternalCanvasActions(response.data.canvas_action);
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

                {/* Right Panel: Shared Canvas */}
                <section className="right-panel">
                    <div className="canvas-header">
                        <h2>Shared Board</h2>
                        <button className="icon-btn"><Share2 size={16} /> Share</button>
                    </div>
                    <div className="canvas-wrapper">
                        <CanvasBoard externalActions={externalCanvasActions} />
                    </div>
                </section>
            </main>
        </div>
    );
}
