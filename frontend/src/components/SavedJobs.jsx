import React, { useState, useEffect } from 'react';
import { Spinner, Alert, Button, Stack } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import JobCard from './JobCard';
import api from '../services/api';

const SavedJobs = () => {
  const { user } = useAuth();
  const [savedJobs, setSavedJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSaved = async () => {
      if (!user?.id) {
        setLoading(false);
        return;
      }
      try {
        const res = await api.get(`/interactions/user/${user.id}`);
        const interactions = await res.data;
        const savedIds = interactions
          .filter(i => i.interaction_type === 'saved')
          .map(i => i.job_id);

        if (savedIds.length === 0) {
          setSavedJobs([]);
          return;
        }
        const jobsRes = await api.get(`/jobs/`);
        const allJobs = await jobsRes.data;
        setSavedJobs(allJobs.filter(j => savedIds.includes(j.id || j._id)));
      } catch (err) {
        console.error("Failed to load saved jobs", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSaved();
  }, [user?.id]);

  if (loading) return <Spinner animation="border" size="sm" />;

  if (savedJobs.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-muted small">No saved jobs yet.</p>
        <Button as={Link} to="/search" variant="outline-primary" size="sm">
          Find Jobs
        </Button>
      </div>
    );
  }

  return (
    <Stack gap={3}>
      {savedJobs.map(job => (
        <JobCard 
          key={job.id || job._id} 
          job={job} 
          initialSaved={true}
          onUnsave={() => setSavedJobs(prev => prev.filter(j => (j.id || j._id) !== (job.id || job._id)))}
        />
      ))}
    </Stack>
  );
};

export default SavedJobs;