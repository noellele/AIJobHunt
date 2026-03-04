import React, { useState, useEffect } from 'react';
import { Container, Spinner, Alert } from 'react-bootstrap';
import api from '../services/api';
import Results from './Results';
import PreferencesSummary from '../components/PreferencesSummary';
import PreferencesForm from '../components/PreferencesForm';
import { useAuth } from '../context/AuthContext';


const Search = () => {
  const { user, login, notify } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchError, setSearchError] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (user) {
      const hasSkills = user.preferences?.skills?.length > 0;
      const hasRoles = user.preferences?.target_roles?.length > 0;
      const hasCriteria = hasSkills || hasRoles;
      if (!hasCriteria) {
      setIsEditing(true);
    } else if (results.length === 0) {
      handleSearch(user.preferences);
    }
    
    setLoading(false);
  }
  }, [user]);

  const handlePreferenceUpdate = async (formData) => {
    try {
      const response = await api.put('/auth/preferences', formData);
      const token = localStorage.getItem('token');
      login(token, response.data);
      notify("Preferences saved successfully!");
      setIsEditing(false);
      await handleSearch(formData);
    } catch (err) {
      notify("Failed to save preferences.", "danger");
    }
  };

const handleSearch = async (criteria) => {
  setSearching(true);
  setSearchError("");
  try {
    const payload = {
      _id: user._id || user.id, 
      preferences: criteria
    };
    const response = await api.post('/ml/job-matches', payload);
    console.log("Matches found:", response.data.matches?.length);
    
    setResults(response.data.matches || []); 
  } catch (err) {
    console.error("Search API Error:", err);
    const message = err.response?.data?.detail || "Failed to fetch job matches.";
    setSearchError(message);
  } finally {
    setSearching(false);
  }
};

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2">Loading your search criteria...</p>
      </Container>
    );
  }

  return (
    <Container className='mx-auto m-5'>
      <h2 className="fw-bold mb-4">Job Search</h2>

      {isEditing ? (
        <PreferencesForm
          initialData={user?.preferences}
          onSearch={handlePreferenceUpdate}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <PreferencesSummary
          preferences={user?.preferences}
          onEdit={() => setIsEditing(true)}
        />
      )}

      <hr className="my-5" />

      {/* Search  Results*/}
      <div className="results-section">

        {searching ? (
          <div className="text-center py-5">
            <Spinner animation="grow" variant="primary" />
            <p className="text-muted mt-2">Searching for matches...</p>
          </div>
        ) : (
          <Results results={results} />
        )}
      </div>
    </Container>
  );
}
export default Search;