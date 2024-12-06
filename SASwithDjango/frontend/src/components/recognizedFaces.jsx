import React, { useState } from 'react';
import axios from 'axios';

function RecognizedFaces() {
  const [faces, setFaces] =useState([]);
  const [loading, setLoading] = useState(false);
  const [videoFile, setVideoFile] =useState(null);
  const [sessionId, setSessionId] =useState(null);

  const handleFileChange = (event)=> {
    const file = event.target.files[0];
    setVideoFile(file);
  };

  const handleGetRecognizedFaces = async ()=> {
    if (!videoFile) {
      alert("Please select a video file first.");
      return;
    }

    const formData= new FormData();
    formData.append('video', videoFile);

    setLoading(true);

    try {
      alert("Video uploaded successfully and processing started.");
      const uploadResponse = await axios.post('http://localhost:8000/api/upload/', formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      const { session_id } = uploadResponse.data;
      setSessionId(session_id);

      const facesResponse = await axios.get(`http://localhost:8000/api/recognized-faces/?session_id=${session_id}`,{
        headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
        params: { session_id },
      });
      setFaces(facesResponse.data.recognized_faces);
    } catch (error) {
      console.log('Error processing video:', error);
      alert("Failed to process video. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div >
      <h1>Smart Attendance System</h1>
      <input type="file" onChange={handleFileChange} accept="video/*" />

      <button onClick={handleGetRecognizedFaces} disabled={loading}>
        {loading ?"Processing..." :"Get Attendance"}
      </button>

      {loading && <p>Processing video, please wait...</p>}
      <ul>
        {faces.map((name, index) =>(
          <li key={index}>{name}</li>
        ))}
      </ul>
    </div>
  );
}

export default RecognizedFaces;
