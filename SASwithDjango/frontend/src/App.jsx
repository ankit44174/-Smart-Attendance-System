import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Signup from './components/signup';
import Login from './components/login';
import RecognizedFaces from './components/recognizedFaces';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(localStorage.getItem('accessToken'));

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route
          path="/upload-video"
          element={isAuthenticated ? <RecognizedFaces /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
};

export default App;
