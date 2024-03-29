import React, { useRef, useState } from 'react';

const HeyGenAvatar = ({ apiKey }) => {
    const SERVER_URL = 'https://api.heygen.com';
    const videoRef = useRef(null);
    const [sessionData, setSessionData] = useState(null);

    const createNewSession = async () => {
        console.log('Creating new session...');
        const response = await fetch(`${SERVER_URL}/v1/streaming.new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Api-Key': apiKey,
            },
            body: JSON.stringify({ quality: 'high' }),
        });

        const data = await response.json();
        console.log('createNewSession response:', data);

        if (!response.ok) {
            throw new Error(`Failed to create session: ${data.message}`);
        }

        if (!data.data || !data.data.sdp) {
            console.error('Invalid session data:', data);
            throw new Error('Invalid session data received from the API');
        }

        setSessionData(data.data);

        const peerConnection = new RTCPeerConnection();
        peerConnection.ontrack = (event) => {
            console.log('Track event received:', event);
            if (videoRef.current) {
                videoRef.current.srcObject = event.streams[0];
            }
        };

        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.data.sdp));
        console.log('Remote description set');

        const answer = await peerConnection.createAnswer();
        console.log('Answer created');
        await peerConnection.setLocalDescription(answer);
        console.log('Local description set');

        return { peerConnection, sessionData: data.data };
    };

    const startSession = async (peerConnection, sessionData) => {
        console.log('Starting session...');
        const startResponse = await fetch(`${SERVER_URL}/v1/streaming.start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Api-Key': apiKey,
            },
            body: JSON.stringify({
                session_id: sessionData.session_id,
                sdp: peerConnection.localDescription,
            }),
        });

        const startData = await startResponse.json();
        console.log('startSession response:', startData);

        peerConnection.onicecandidate = ({ candidate }) => {
            console.log('ICE candidate event:', candidate);
            if (candidate) {
                fetch(`${SERVER_URL}/v1/streaming.ice`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Api-Key': apiKey,
                    },
                    body: JSON.stringify({
                        session_id: sessionData.session_id,
                        candidate: candidate.candidate,
                        sdpMid: candidate.sdpMid,
                        sdpMLineIndex: candidate.sdpMLineIndex,
                    }),
                }).then(response => console.log('ICE candidate sent', response))
                    .catch(error => console.error('Error sending ICE candidate', error));
            }
        };
    };

    const driveAvatarToSpeak = async (sessionId) => {
        console.log('Driving avatar to speak...');
        const text = "Hello Julia, I'm Rachel, how are you?";
        const response = await fetch(`${SERVER_URL}/v1/streaming.task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Api-Key': apiKey,
            },
            body: JSON.stringify({ session_id: sessionId, text }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error sending message:', errorData.message, 'Code:', errorData.code);
            throw new Error(`HTTP ${response.status}: ${errorData.message}`);
        }

        const data = await response.json();
        console.log('Avatar speak successful:', data);
    };

    const handleStartSession = async () => {
        try {
            console.log('Handle start session invoked');
            const { peerConnection, sessionData } = await createNewSession();
            await startSession(peerConnection, sessionData);

            // Check if peerConnection is in stable state before sending task
            if (peerConnection.signalingState === "stable") {
                console.log('Signaling state is stable, sending task');
                await driveAvatarToSpeak(sessionData.session_id);
            } else {
                console.error('Signaling state is not stable:', peerConnection.signalingState);
            }
        } catch (error) {
            console.error('Error in handling the session:', error);
        }
    };

    return (
        <div>
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', height: 'auto' }}></video>
            <button onClick={handleStartSession}>Start Session</button>
        </div>
    );
};

export default HeyGenAvatar;
