import { useLocation, Link } from 'react-router-dom';
import { Container, Alert, Button } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import JobCard from '../components/JobCard';
import api from '../services/api';

const Results = ({ results }) => {
  const location = useLocation();
  const { user, loading } = useAuth();
  const [savedJobIds, setSavedJobIds] = useState(new Set());
  const filters = location.state?.filters;

  useEffect(() => {
    const fetchSavedJobs = async () => {
      if (!user?.id) return;
      try {
        const response = await api.get(`/interactions/user/${user.id}`);
        if (response.status === 200) {
          const interactions = response.data;
          const savedIds = new Set(
            interactions
              .filter(i => i.interaction_type === 'saved')
              .map(i => i.job_id)
          );
          setSavedJobIds(savedIds);
        }
      } catch (error) {
        console.error("Error loading saved jobs:", error);
      }
    };

    fetchSavedJobs();
  }, [user]);

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2 text-muted">Loading your profile...</p>
      </Container>
    );
  }

  if (!results || results.length === 0) {
    return <div className="text-center">
      <p className="text-center text-muted">No matches found. Try adjusting your skills.</p>
      <Button as={Link} to="/dashboard" variant="outline-secondary">
        Edit Preferences
      </Button>
    </div>
  }

  const formatCurrency = (value) => {
    return value ? value.toLocaleString() : '0';
  };

  return (
    <Container className="mt-2 text-center">
      <h2 className="fw-bold my-3">Matching Jobs ({results.length})</h2>

      {filters && (
        <Alert variant="info" className="text-start d-inline-block shadow-sm">
          <strong>Searching for:</strong> {filters.target_roles.join(', ')} <br />
          <strong>Skills:</strong> {filters.skills.join(', ')} <br />
          <strong>Location:</strong> {filters.desired_locations.join(', ') || 'Anywhere'} <br />
          <strong>Salary Range:</strong> ${formatCurrency(filters.salary_min)} — ${formatCurrency(filters.salary_max)}
        </Alert>
      )}

      <div className="job-list">
        {results.map((job, index) => {
          const currentId = job.job_id || job._id || job.id;

          return (
            <JobCard
              key={currentId}
              job={{ ...job, id: currentId }}
              initialSaved={savedJobIds.has(currentId)}
              onUnsave={() => {
                setSavedJobIds(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(currentId);
                  return newSet;
                });
              }}
            />
          );
        })}
        2. Verify your /ml/job-matches
      </div>

    </Container>
  );
};

export default Results;