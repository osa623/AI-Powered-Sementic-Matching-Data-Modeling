import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [activeTab, setActiveTab] = useState('add');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const API_BASE_URL = 'http://localhost:8000';

  // Add FOUND Item to Database
  const handleAddItem = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const itemId = `FOUND-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const response = await axios.post(`${API_BASE_URL}/index`, {
        id: itemId,
        description: description,
        category: category
      });

      setMessage(`✅ Found item added successfully! ID: ${response.data.item_id}`);
      setCategory('');
      setDescription('');
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Search for LOST Item (matches against FOUND items)
  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setSearchResults([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/search`, {
        text: description,
        category: category,
        limit: 10
      });

      if (response.data.matches && response.data.matches.length > 0) {
        setSearchResults(response.data.matches);
        setMessage(`✅ Found ${response.data.total_matches} matching found items`);
      } else {
        setMessage('❌ No matching found items in database');
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔍 Smart Lost & Found System</h1>
        <p>AI-Powered Semantic Matching Engine</p>
      </header>

      <div className="container">
        {/* Tab Navigation */}
        <div className="tabs">
          <button 
            className={activeTab === 'add' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('add')}
          >
            ➕ Add Found Item
          </button>
          <button 
            className={activeTab === 'search' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('search')}
          >
            🔎 Search My Lost Item
          </button>
        </div>

        {/* Add Found Item Form */}
        {activeTab === 'add' && (
          <div className="form-container">
            <h2>Add Found Item to Database</h2>
            <p className="info-text">📦 Found a wallet? Add it here so owners can find it!</p>
            <form onSubmit={handleAddItem}>
              <div className="form-group">
                <label htmlFor="category">Category:</label>
                <select 
                  id="category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  required
                >
                  <option value="">Select Category</option>
                  <option value="Wallet">Wallet</option>
                  <option value="Phone">Phone</option>
                  <option value="ID Card">ID Card</option>
                  <option value="Bag">Bag</option>
                  <option value="Umbrella">Umbrella</option>
                  <option value="Keys">Keys</option>
                  <option value="Laptop">Laptop</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description:</label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the FOUND item (English, Sinhala, or Singlish)&#10;Example: 'Black leather wallet with ID cards' or 'rathu wallet ekak thiyanawa'"
                  rows="4"
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? '⏳ Adding to Database...' : '➕ Add Found Item'}
              </button>
            </form>
          </div>
        )}

        {/* Search for Lost Item Form */}
        {activeTab === 'search' && (
          <div className="form-container">
            <h2>Search for Your Lost Item</h2>
            <p className="info-text">🔍 Lost your wallet? Search against all found items in our database!</p>
            <form onSubmit={handleSearch}>
              <div className="form-group">
                <label htmlFor="search-category">Category:</label>
                <select 
                  id="search-category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  required
                >
                  <option value="">Select Category</option>
                  <option value="Wallet">Wallet</option>
                  <option value="Phone">Phone</option>
                  <option value="ID Card">ID Card</option>
                  <option value="Bag">Bag</option>
                  <option value="Umbrella">Umbrella</option>
                  <option value="Keys">Keys</option>
                  <option value="Laptop">Laptop</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="search-description">Description of Your Lost Item:</label>
                <textarea
                  id="search-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your LOST item (English, Sinhala, or Singlish)&#10;Example: 'Brown leather wallet with blue cards' or 'mama rathu wallet ekak hoya giya'"
                  rows="4"
                  required
                />
              </div>

              <button type="submit" className="btn btn-search" disabled={loading}>
                {loading ? '⏳ Searching Database...' : '🔎 Find My Item'}
              </button>
            </form>

            {/* Search Results - Matching Found Items */}
            {searchResults.length > 0 && (
              <div className="results-container">
                <h3>🎯 Matching Found Items (AI Semantic Similarity):</h3>
                <p className="results-info">The AI has analyzed {searchResults.length} potentially matching items</p>
                {searchResults.map((result, index) => (
                  <div key={index} className="result-card">
                    <div className="result-header">
                      <span className="result-id">Found Item ID: {result.id}</span>
                      <span className={`result-score ${result.score >= 70 ? 'high-match' : result.score >= 50 ? 'medium-match' : 'low-match'}`}>
                        Similarity: {result.score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="result-body">
                      <p><strong>Category:</strong> {result.category}</p>
                      <p><strong>Description:</strong> {result.description}</p>
                      <p className="match-reason"><em>🤖 {result.reason}</em></p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Message Display */}
        {message && (
          <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;