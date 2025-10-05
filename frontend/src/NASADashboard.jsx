import React, { useState } from 'react';
import { Search, Book, Rocket, TrendingUp, Database, Sparkles, ArrowRight, Filter, X } from 'lucide-react';
import './NASADashboard.css';

function NASABioscienceDashboard() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const suggestions = [
    "microgravity effects on bone density",
    "plant growth in space",
    "radiation exposure impacts",
    "muscle atrophy in astronauts",
    "immune system changes",
    "cardiovascular adaptations",
    "Mars mission health risks",
    "ISS biological experiments",
    "space-grown crops",
    "cellular aging in microgravity",
    "DNA damage from cosmic radiation",
    "sleep patterns in space"
  ];

  const filterCategories = [
    { id: 'mission', label: 'Mission', options: ['ISS', 'Apollo', 'SpaceX', 'Mars Missions'] },
    { id: 'topic', label: 'Research Area', options: ['Human Health', 'Plant Biology', 'Microbiology', 'Radiation'] },
    { id: 'year', label: 'Year', options: ['2020-2025', '2015-2019', '2010-2014', 'Before 2010'] }
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          filters: selectedFilters,
          limit: 20
        })
      });
      
      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setSearchResults(data.results);
      setShowSuggestions(false);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Make sure the backend is running on http://localhost:8000');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    setTimeout(() => {
      handleSearch();
    }, 100);
  };

  const toggleFilter = (filter) => {
    setSelectedFilters(prev =>
      prev.includes(filter) ? prev.filter(f => f !== filter) : [...prev, filter]
    );
  };

  const filteredSuggestions = suggestions.filter(s =>
    s.toLowerCase().includes(searchQuery.toLowerCase()) && searchQuery.length > 0
  );

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className={`stat-card stat-card-${color}`}>
      <div className="stat-card-content">
        <div className="stat-info">
          <p className="stat-label">{label}</p>
          <p className="stat-value">{value}</p>
        </div>
        <Icon className="stat-icon" size={32} />
      </div>
    </div>
  );

  return (
    <div className="dashboard">
      <div className="header">
        <div className="header-content">
          <div className="header-title-section">
            <div className="logo-container">
              <Rocket size={40} />
            </div>
            <div>
              <h1 className="main-title">
                NASA Bioscience Research Explorer
              </h1>
              <p className="subtitle">
                Explore decades of space biology experiments • Powered by AI Knowledge Graphs
              </p>
            </div>
          </div>

          <div className="search-container">
            <div className="search-wrapper">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                placeholder="Search NASA bioscience publications... (e.g., 'microgravity effects on bone density')"
                className="search-input"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Search className="search-icon" size={24} />
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="search-button"
              >
                Search
              </button>
            </div>

            {showSuggestions && searchQuery && filteredSuggestions.length > 0 && (
              <div className="suggestions-dropdown">
                <div className="suggestions-header">
                  <Sparkles size={16} />
                  <span>Suggested searches</span>
                </div>
                {filteredSuggestions.slice(0, 8).map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="suggestion-item"
                  >
                    <Search size={16} />
                    <span>{suggestion}</span>
                    <ArrowRight size={16} className="suggestion-arrow" />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="stats-grid">
            <StatCard icon={Book} label="Publications" value="608" color="blue" />
            <StatCard icon={Database} label="Experiments" value="1,203" color="purple" />
            <StatCard icon={Rocket} label="Missions" value="156" color="indigo" />
            <StatCard icon={TrendingUp} label="Citations" value="45.2K" color="pink" />
          </div>
        </div>
      </div>

      <div className="main-content">
        {searchResults.length > 0 && (
          <div className="filters-section">
            <div className="filters-header">
              <Filter size={20} />
              <span>Refine Results</span>
            </div>
            <div className="filters-container">
              {filterCategories.map(category =>
                category.options.map(option => (
                  <button
                    key={option}
                    onClick={() => toggleFilter(option)}
                    className={`filter-button ${selectedFilters.includes(option) ? 'filter-active' : ''}`}
                  >
                    {option}
                    {selectedFilters.includes(option) && <X size={12} />}
                  </button>
                ))
              )}
            </div>
          </div>
        )}

        {isSearching && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Searching NASA bioscience database...</p>
          </div>
        )}

        {!isSearching && searchResults.length > 0 && (
          <div className="results-section">
            <div className="results-count">
              Found <span className="count-highlight">{searchResults.length}</span> publications
            </div>
            <div className="results-list">
              {searchResults.map(paper => (
                <div key={paper.id} className="paper-card">
                  <div className="paper-header">
                    <h3 className="paper-title">{paper.title}</h3>
                    <span className="paper-year">{paper.year}</span>
                  </div>
                  
                  <p className="paper-authors">{paper.authors}</p>
                  <p className="paper-summary">{paper.summary}</p>
                  
                  <div className="paper-footer">
                    <div className="paper-tags">
                      {paper.tags && paper.tags.map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                    <div className="paper-actions">
                      <span className="citations">{paper.citations || 0} citations</span>
                      <button className="view-paper-btn">
                        View Full Paper
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!isSearching && searchResults.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">
              <Search size={48} />
            </div>
            <h2 className="empty-title">Start Exploring NASA Bioscience Research</h2>
            <p className="empty-description">
              Search through decades of space biology experiments from NASA missions. 
              Enter keywords related to human health, plant biology, microbiology, or radiation effects.
            </p>
            <div className="quick-suggestions">
              {suggestions.slice(0, 6).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="quick-suggestion-btn"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default NASABioscienceDashboard;