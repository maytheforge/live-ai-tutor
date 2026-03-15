import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * A custom hook to manage the WebSocket connection to the Gemini Multimodal Live API.
 */
export function useGeminiLive(apiKey) {
    const [isConnected, setIsConnected] = useState(false);
    const [isReceivingAudio, setIsReceivingAudio] = useState(false);
    const [toolCall, setToolCall] = useState(null);
    const wsRef = useRef(null);
    const audioContextRef = useRef(null);
    const streamRef = useRef(null);
    const processorRef = useRef(null);
    const sourceRef = useRef(null);
    const isToolCallPendingRef = useRef(false);

    // Playback state
    const playQueueRef = useRef([]);
    const isPlayingRef = useRef(false);

    // Function to play base64 PCM 24kHz audio from Gemini
    const playNextAudio = useCallback(async () => {
        if (playQueueRef.current.length === 0 || isPlayingRef.current || !audioContextRef.current) {
            setIsReceivingAudio(false);
            return;
        }

        isPlayingRef.current = true;
        setIsReceivingAudio(true);
        const base64Audio = playQueueRef.current.shift();

        try {
            const binaryString = atob(base64Audio);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }

            // 16-bit PCM little endian
            const int16Array = new Int16Array(bytes.buffer);
            const float32Array = new Float32Array(int16Array.length);
            for (let i = 0; i < int16Array.length; i++) {
                float32Array[i] = int16Array[i] / 32768.0;
            }

            const audioBuffer = audioContextRef.current.createBuffer(1, float32Array.length, 24000); // Gemini returns 24kHz
            audioBuffer.getChannelData(0).set(float32Array);

            const source = audioContextRef.current.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContextRef.current.destination);

            source.onended = () => {
                isPlayingRef.current = false;
                playNextAudio();
            };

            source.start();
        } catch (err) {
            console.error("Error playing audio chunk:", err);
            isPlayingRef.current = false;
            playNextAudio();
        }
    }, []);

    const connect = useCallback(async () => {
        if (!apiKey) {
            console.error("Gemini API Key is missing!");
            return;
        }

        try {
            // 1. Get Microphone Access (16kHz for Gemini input)
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const audioCtx = new AudioContext({ sampleRate: 16000 });
            audioContextRef.current = audioCtx;

            const source = audioCtx.createMediaStreamSource(stream);
            sourceRef.current = source;
            // 4096 is a good buffer size for ScriptProcessor
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            processorRef.current = processor;

            console.log("Connecting to Gemini Live API...");
            // Official endpoint for the Multimodal Live API
            const url = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${apiKey}`;
            const ws = new WebSocket(url);

            ws.onopen = () => {
                console.log("Connected to Gemini Live API over WebSocket!");
                setIsConnected(true);

                // Initial setup message (no systemInstruction — not supported by native audio models)
                const setupMessage = {
                    setup: {
                        model: "models/gemini-2.5-flash-native-audio-latest",
                        generationConfig: {
                            responseModalities: ["AUDIO"]
                        },
                        tools: [
                            {
                                functionDeclarations: [
                                    {
                                        name: "generate_diagram",
                                        description: "Draws an educational diagram on the shared canvas as a visual discovery aid. Only use this when the student explicitly requests a visual, or when a diagram would help the student reason through a step — NEVER to reveal the final answer.",
                                        parameters: {
                                            type: "OBJECT",
                                            properties: {
                                                diagram_type: {
                                                    type: "STRING",
                                                    description: "The type of diagram to generate. Must be one of: math_number_line, science_flow, math_equation_steps",
                                                    enum: ["math_number_line", "science_flow", "math_equation_steps"]
                                                },
                                                topic: {
                                                    type: "STRING",
                                                    description: "The specific topic the user wants drawn (e.g., 'Water Cycle', 'Photosynthesis')."
                                                }
                                            },
                                            required: ["diagram_type", "topic"]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                };
                ws.send(JSON.stringify(setupMessage));

                // Inject Socratic persona as a model-role turn (workaround for native audio lacking systemInstruction support)
                // followed by the student's opening greeting
                const initialGreeting = {
                    clientContent: {
                        turns: [
                            {
                                role: "model",
                                parts: [{ text: `You are Coach Leo, a Socratic educational tutor — a "Socratic Mirror". You NEVER directly solve problems or give answers. You guide students step-by-step using questions. RULES: (1) Ask ONE guiding question at a time, never reveal the answer. (2) When a student gets a step right, affirm it and ask what comes next. (3) NEVER say "The answer is", "x equals", or "The solution is". (4) Keep responses short, warm, and encouraging — 1-2 sentences max. (5) Only draw a diagram when the student explicitly asks for one.` }]
                            },
                            {
                                role: "user",
                                parts: [{ text: "Hi! I am ready to study." }]
                            }
                        ],
                        turnComplete: true
                    }
                };
                setTimeout(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify(initialGreeting));
                    }
                }, 500);

                // 2. Start capturing audio and streaming it to WebSocket
                processor.onaudioprocess = (e) => {
                    if (ws.readyState !== WebSocket.OPEN) return;
                    if (isToolCallPendingRef.current) return;

                    const inputData = e.inputBuffer.getChannelData(0);
                    const pcm16 = new Int16Array(inputData.length);
                    let hasAudioData = false;
                    for (let i = 0; i < inputData.length; i++) {
                        let s = Math.max(-1, Math.min(1, inputData[i]));
                        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                        if (pcm16[i] !== 0) hasAudioData = true;
                    }

                    if (!hasAudioData) return; // Don't send absolute silence chunks if unnecessary

                    const buffer = new Uint8Array(pcm16.buffer);
                    // Fast base64 encoding without blowing the stack
                    let binary = '';
                    const chunkSize = 1000;
                    for (let i = 0; i < buffer.length; i += chunkSize) {
                        binary += String.fromCharCode.apply(null, buffer.slice(i, i + chunkSize));
                    }
                    const base64 = btoa(binary);

                    ws.send(JSON.stringify({
                        realtimeInput: {
                            mediaChunks: [{
                                mimeType: "audio/pcm;rate=16000",
                                data: base64
                            }]
                        }
                    }));
                };

                source.connect(processor);
                processor.connect(audioCtx.destination); // Needed for processing to trigger
            };

            ws.onmessage = async (event) => {
                try {
                    let textData = event.data;
                    if (event.data instanceof Blob) {
                        textData = await event.data.text();
                    }
                    const data = JSON.parse(textData);

                    // The Gemini Live API might send a setupComplete message
                    if (data.setupComplete) {
                        console.log("API Setup Complete!");
                    }

                    if (data.serverContent && data.serverContent.modelTurn) {
                        const parts = data.serverContent.modelTurn.parts;
                        for (const part of parts) {
                            if (part.inlineData && part.inlineData.data) {
                                // Push the incoming base64 audio to the playback queue
                                playQueueRef.current.push(part.inlineData.data);
                                if (!isPlayingRef.current) {
                                    playNextAudio();
                                }
                            }
                        }
                    }

                    if (data.toolCall && data.toolCall.functionCalls) {
                        for (const call of data.toolCall.functionCalls) {
                            console.log("Received Function Call from Gemini:", call);
                            isToolCallPendingRef.current = true;
                            setToolCall(call);
                        }
                    }
                } catch (err) {
                    console.error("Error parsing message from Gemini:", err);
                }
            };

            ws.onerror = (error) => {
                console.error("WebSocket Error:", error);
            };

            ws.onclose = (event) => {
                console.log("Disconnected from Gemini Live API. Code:", event.code, "Reason:", event.reason);
                setIsConnected(false);
                cleanupAudio();
            };

            wsRef.current = ws;

        } catch (error) {
            console.error("Failed to establish WebSocket connection or get microphone:", error);
            setIsConnected(false);
        }
    }, [apiKey, playNextAudio]);

    const cleanupAudio = useCallback(() => {
        if (processorRef.current && sourceRef.current) {
            sourceRef.current.disconnect(processorRef.current);
            processorRef.current.disconnect();
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (audioContextRef.current) {
            audioContextRef.current.close().catch(console.error);
        }
        processorRef.current = null;
        sourceRef.current = null;
        streamRef.current = null;
        audioContextRef.current = null;
        playQueueRef.current = [];
        isPlayingRef.current = false;
        setIsReceivingAudio(false);
        isToolCallPendingRef.current = false;
    }, []);

    const disconnect = useCallback(() => {
        console.log("Disconnecting...");
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        cleanupAudio();
        setIsConnected(false);
    }, [cleanupAudio]);

    // Clean up on unmount
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                // We're genuinely unmounting, clean it all up
                try { wsRef.current.close(); } catch (e) { }
            }
            cleanupAudio();
        };
    }, [cleanupAudio]);


    const sendContext = useCallback((base64Image) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.warn("Cannot send context: WebSocket is not open.");
            return;
        }

        // Send the image as a realtime input chunk so the live model sees it instantly
        const message = {
            realtimeInput: {
                mediaChunks: [
                    {
                        mimeType: "image/jpeg",
                        data: base64Image
                    }
                ]
            }
        };
        wsRef.current.send(JSON.stringify(message));
    }, []);

    const sendToolResponse = useCallback((functionResponses) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.warn("Cannot send tool response: WebSocket is not open.");
            return;
        }

        const message = {
            toolResponse: {
                functionResponses: [
                    {
                        name: functionResponses.name,
                        id: functionResponses.id,
                        response: functionResponses.response
                    }
                ]
            }
        };
        wsRef.current.send(JSON.stringify(message));
        isToolCallPendingRef.current = false;
    }, []);

    return {
        isConnected,
        isReceivingAudio,
        connect,
        disconnect,
        sendContext,
        sendToolResponse,
        toolCall,
        clearToolCall: () => setToolCall(null)
    };
}
