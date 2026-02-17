import React, { useState, useEffect } from 'react';
import { Container, Toast, ToastContainer, Spinner, Alert } from 'react-bootstrap';
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
      const hasCriteria = user.preferences?.skills?.length > 0 || user.preferences?.target_roles?.length > 0;
      if (hasCriteria && results.length === 0) {
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
      const response = await api.post('/jobs/search', criteria);
      setResults(response.data);
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

      {searchError && <Alert variant="danger">{searchError}</Alert>}

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
        <h3 className="mb-4">AI-Matched Results</h3>

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