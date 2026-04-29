import React, { useState, useEffect } from 'react'

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setResult(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Error uploading file. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <button className="theme-toggle" onClick={toggleTheme}>
        {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
      </button>
      
      <div className="header">
        <h1>AI Document Intelligence</h1>
        <p>Extract structured data from your documents instantly</p>
      </div>
      
      <div className="upload-card">
        <div className="file-input-wrapper">
          <input 
            type="file" 
            onChange={handleFileChange}
            accept="image/*,application/pdf"
          />
          <div className="upload-icon">📄</div>
          <h3>Drag & Drop or Click to Upload</h3>
          <p style={{ color: '#94a3b8', margin: '8px 0' }}>Supports PDF, JPG, PNG</p>
          {file && (
            <div className="file-name">
              {file.name}
            </div>
          )}
        </div>
        
        <button 
          className="btn"
          onClick={handleUpload}
          disabled={loading || !file}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : "Analyze Document"}
        </button>
      </div>

      {result && result.data && (
        <div className="results-section">
          <div className="results-card">
            <h2>✨ Extracted Information</h2>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Extracted Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.data).map(([key, value]) => (
                  <tr key={key}>
                    <td className="field-name">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </td>
                    <td className="field-value">
                      {value !== null ? value.toString() : <span style={{ color: '#ef4444' }}>Not Found</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="results-card">
            <h2><span style={{ fontSize: '1.2rem', color: '#818cf8', paddingRight: '8px' }}>{`{ }`}</span> Raw JSON Response</h2>
            <div className="json-view">
              <pre>{JSON.stringify(result.data, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
