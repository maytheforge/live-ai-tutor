/// <reference types="vite/client" />
import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { CanvasBoard } from './components/CanvasBoard';
import { useGeminiLive } from './hooks/useGeminiLive';
import { Video, Mic, Share2, Sparkles, Upload } from 'lucide-react';
import './App.css';

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

function App() {
    const webcamRef = useRef(null);
    const uploadInputRef = useRef(null);
    const { isConnected, connect, disconnect, sendContext, sendToolResponse, toolCall, clearToolCall } = useGeminiLive(GEMINI_API_KEY);

    const [tutorMessage, setTutorMessage] = useState("Hi! Show me your homework on the camera or upload a photo.");
    const [externalCanvasActions, setExternalCanvasActions] = useState(null);
    const [lastSnapshot, setLastSnapshot] = useState(null);
    const [uploadedImage, setUploadedImage] = useState(null); // tracks the uploaded file preview

    // Handle tool calls coming from the Gemini Live audio agent
    useEffect(() => {
        if (!toolCall) return;

        const executeTool = async () => {
            if (toolCall.name === "generate_diagram") {
                const args = toolCall.args;
                const diagramType = args.diagram_type;
                const topic = args.topic || args.diagram_type;

                console.log("Gemini asked to draw diagram:", diagramType, "about:", topic);
                setTutorMessage(`Drawing a diagram about ${topic}...`);

                // Respond to Gemini IMMEDIATELY so it doesn't disconnect with Code 1008 while waiting for the slow Python LLM backend!
                sendToolResponse({
                    name: "generate_diagram",
                    id: toolCall.id,
                    response: {
                        result: {
                            status: "success",
                            message: "Diagram generation started. Remind the user it might take a few seconds to appear."
                        }
                    }
                });

                // Clear state immediately to prevent re-renders hitting the same call
                clearToolCall();

                try {
                    const backendUrl = `http://${window.location.hostname}:8000/interact`;
                    const response = await axios.post(backendUrl, {
                        student_id: "demo_student",
                        message: `The user wants a diagram about: ${topic}`,
                        request_diagram: diagramType
                    });

                    if (response.data.canvas_action) {
                        setExternalCanvasActions(response.data.canvas_action);
                    }
                } catch (error) {
                    console.error("Error executing diagram tool:", error);
                }
            } else {
                clearToolCall();
            }
        };

        executeTool();
    }, [toolCall, sendToolResponse, clearToolCall]);

    // Sync our local "isLive" UI state with the hook's true connection state
    const isLive = isConnected;

    const toggleVoice = () => {
        if (isLive) {
            disconnect();
        } else {
            connect();
        }
    };

    // Pass handleToolCall and sendToolResponse as late deps by updating the hook signature or accessing it dynamically.
    // We already extracted sendToolResponse above.

    // Function to simulate sending an image down to the backend
    const captureAndUnderstand = useCallback(async () => {
        if (!webcamRef.current) return;

        const imageSrc = webcamRef.current.getScreenshot();
        if (!imageSrc) return;

        try {
            setTutorMessage("Thinking...");
            setLastSnapshot(imageSrc); // Show the snapshot to the user

            // Send context to the Gemini Live audio session so it can 'see' the image
            const base64Image = imageSrc.split(',')[1];
            if (isLive) {
                sendContext(base64Image);
            }

            // Call our FastAPI backend using the dynamic hostname so it works over LAN
            const backendUrl = `http://${window.location.hostname}:8000/interact`;
            const response = await axios.post(backendUrl, {
                student_id: "demo_student",
                message: "Can you help me with this problem?",
                image_data: base64Image, // Send base64 data to backend for canvas parsing
                request_diagram: "science_flow" // Trigger the Diagram Agent for demo purposes
            });

            if (response.data.tutor_response) {
                setTutorMessage(response.data.tutor_response);
            }

            if (response.data.canvas_action) {
                setExternalCanvasActions(response.data.canvas_action);
            }

        } catch (error) {
            console.error("Error interacting with tutor:", error);
            setTutorMessage("Oops, I had trouble seeing that. Can you adjust the paper?");
        }
    }, [webcamRef, isLive, sendContext]);

    // Handle file upload as an alternative to webcam snapshot
    const handleFileUpload = useCallback(async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Reset input so same file can be re-selected
        e.target.value = '';

        const reader = new FileReader();
        reader.onload = async (loadEvent) => {
            const dataUrl = loadEvent.target.result; // e.g. "data:image/jpeg;base64,..."
            const base64Image = dataUrl.split(',')[1];

            setUploadedImage(dataUrl);
            setLastSnapshot(null); // clear webcam snapshot when a file is uploaded
            setTutorMessage('Looking at your uploaded homework...');

            // Send image to the active Gemini Live voice session
            if (isLive) {
                sendContext(base64Image);
            }

            try {
                const backendUrl = `http://${window.location.hostname}:8000/interact`;
                const response = await axios.post(backendUrl, {
                    student_id: 'demo_student',
                    message: 'Can you help me with this problem?',
                    image_data: base64Image,
                });

                if (response.data.tutor_response) {
                    setTutorMessage(response.data.tutor_response);
                }
                if (response.data.canvas_action) {
                    setExternalCanvasActions(response.data.canvas_action);
                }
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
                    <Sparkles className="icon-gold" />
                    <h1>Live Homework Tutor</h1>
                </div>
                <div className="status-indicators">
                    <span className={`status-dot ${isLive ? 'live' : 'offline'}`}></span>
                    {isLive ? 'Gemini Live: Active' : 'Gemini Live: Offline'}
                </div>
            </header>

            {/* Main Workspace */}
            <main className="workspace">
                {/* Left Panel: Camera & Tutor Chat */}
                <aside className="left-panel">
                    <div className="camera-container">
                        <Webcam
                            audio={false}
                            ref={webcamRef}
                            screenshotFormat="image/jpeg"
                            videoConstraints={{ facingMode: "environment" }}
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
                            {/* Hidden file input — triggered by Upload button */}
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
                        <h3>Tutor Avatar</h3>
                        <div className="message-bubble">
                            <p>{tutorMessage}</p>
                        </div>
                        {/* Show either uploaded file OR webcam snapshot as context preview */}
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

export default App;
