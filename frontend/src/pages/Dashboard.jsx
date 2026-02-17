import React, { useState } from 'react';
import api from '../services/api';
import PreferencesSummary from '../components/PreferencesSummary';
import DashboardCard from '../components/DashboardCard';
import { Container, Row, Col, Spinner } from 'react-bootstrap';
import PreferencesForm from '../components/PreferencesForm';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user, login, loading: authLoading, notify } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [updating, setUpdating] = useState(false);

  console.log("Dashboard rendering. User state is:", user);

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
          {isEditing ? (
            <PreferencesForm
              initialData={user?.preferences}
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
        </Col>

        <Col lg={4}>
          <DashboardCard
            title="Search Insight"
            icon={<i className="bi bi-cpu"></i>}
          >
            <p className="small text-muted mb-0">
              The AI agent is optimizing for <strong>{user?.preferences?.skills?.length || 0}</strong> listed skills.
            </p>
          </DashboardCard>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;