import { useState, useEffect } from 'react';
import api from '../services/api';
import { Container, Row, Col, Spinner, Stack, Badge } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';
import PreferencesSummary from '../components/PreferencesSummary';
import DashboardCard from '../components/DashboardCard';
import DataPullControl from '../components/DataPullControl';
import PreferencesForm from '../components/PreferencesForm';
import SavedJobs from '../components/SavedJobs';

const Dashboard = () => {
  const { user, login, loading: authLoading, notify } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [updating, setUpdating] = useState(false);

  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    const fetchUserStats = async () => {
      const userId = user?.id || user?._id;
      if (!userId) return;

      try {
        const response = await api.get(`/user-stats/${userId}/stats`);
        setStats(response.data);
      } catch (error) {
        // 404 is valid for new user; no search = no stats
        if (error.response && error.response.status === 404) {
          console.log("No search has been run, therefore no gap analysis has been performed.");
          setStats(null);
        } else {
          console.error("Actual error fetching stats:", error);
        }
      } finally {
        setLoadingStats(false);
      }
    };

    if (user) fetchUserStats();
  }, [user]);

  const handleUpdate = async (formData) => {
    setUpdating(true);
    try {
      const response = await api.put('/auth/preferences', formData);
      const token = localStorage.getItem('token');
      login(token, response.data);
      notify("Preferences saved successfully!")
      setIsEditing(false);
    } catch (error) {
      notify("Failed to save preferences.", "danger");
    } finally {
      setUpdating(false);
    }
  };

  if (authLoading) {
    return (
      <Container className="d-flex justify-content-center align-items-center vh-100">
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }

  if (!user) {
    return (
      <Container className="mt-5 text-center">
        <Spinner animation="grow" size="sm" variant="secondary" />
        <p className="text-muted">Loading preferences...</p>
      </Container>
    );
  }

  return (
    <Container className="my-4 animate-fade-in">
      <h2 className="mb-4 fw-bold">Welcome, {user?.name?.split(' ')[0] || 'User'}</h2>
      <Row className="g-4">
        <Col lg={8}>
          <Stack gap={4}>
            {isEditing ? (
              <PreferencesForm
                initialData={user?.preferences || {
                  target_roles: [],
                  skills: [],
                  desired_locations: [],
                  salary_min: 0,
                  salary_max: 150000
                }}
                onSearch={handleUpdate}
                onCancel={() => setIsEditing(false)}
                isSubmitting={updating}
              />
            ) : (
              <PreferencesSummary
                preferences={user?.preferences}
                onEdit={() => setIsEditing(true)}
              />
            )}

            <DashboardCard
              title="Saved for Later"
              icon={<i className="bi bi-bookmark-heart"></i>}
            >
              <SavedJobs />
            </DashboardCard>
          </Stack>
        </Col>

        <Col lg={4}>
          <Stack gap={4}>
            <DashboardCard
              title="Search Insight"
              icon={<i className="bi bi-cpu"></i>}
            >
              <div className="mb-3">
                <p className="small text-muted mb-2 fw-bold" style={{ fontSize: '0.7rem', letterSpacing: '0.05rem' }}>
                  AI GAP ANALYSIS
                </p>

                {loadingStats ? (
                  <div className="text-center py-2">
                    <Spinner animation="border" size="sm" variant="secondary" />
                  </div>
                ) : !stats ? (
                  /* STATE 1: No Search History (Blue) */
                  <div className="p-3 rounded bg-light border-start border-4 border-info shadow-sm">
                    <p className="small mb-1 text-dark fw-medium">
                      No insights available yet.
                    </p>
                    <p className="small text-muted mb-0">
                      Run your first search to see which skills the AI suggests for your target roles.
                    </p>
                  </div>
                ) : stats.top_missing_skill ? (
                  /* STATE 2: Skills Gap Found (Yellow) */
                  <div className="p-3 rounded bg-light border-start border-4 border-warning shadow-sm">
                    <p className="small mb-2 text-dark">
                      Boost your match rate by adding:
                    </p>
                    <Badge bg="warning" text="dark" className="fs-6 px-3 py-2 rounded-pill shadow-sm text-truncate">
                      {stats.top_missing_skill}
                    </Badge>
                    <p className="text-muted mt-2 mb-0" style={{ fontSize: '0.65rem' }}>
                      Based on your recent match history.
                    </p>
                  </div>
                ) : (
                  /* STATE 3: Search Run & No Gaps (Green) */
                  <div className="p-3 rounded bg-light border-start border-4 border-success">
                    <p className="small mb-0 text-success fw-medium">
                      <i className="bi bi-check-circle-fill me-2"></i>
                      Your skills are perfectly aligned with your target roles!
                    </p>
                  </div>
                )}
              </div>
              <p className="small text-muted mb-0">
                The AI agent is optimizing for <strong>{user?.preferences?.skills?.length || 0}</strong> listed skills.
              </p>
            </DashboardCard>
            <DataPullControl />
          </Stack>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;