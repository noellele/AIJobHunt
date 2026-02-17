import React from 'react';
import { Card, Badge, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const PreferencesSummary = ({ preferences, onEdit }) => {
  if (!preferences) {
    return (
      <Card className="shadow-sm border-0 text-center p-4">
        <Card.Body>
          <p className="text-muted">No search preferences set yet.</p>
          <Link to="/search" className="btn btn-outline-primary btn-sm">
            Set Preferences
          </Link>
        </Card.Body>
      </Card>
    );
  }

  const { target_roles, desired_locations, skills, salary_min, salary_max } = preferences;

  return (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Header className="bg-white border-0 pt-4 px-4">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0 fw-bold">Search Preferences</h5>
          <button 
            onClick={onEdit} 
            className="btn btn-link text-decoration-none small fw-bold p-0"
          >
            Edit
          </button>
        </div>
      </Card.Header>
      <Card.Body className="px-4 pb-4">
        <Row className="g-4">
          {/* Roles & Locations */}
          <Col md={6}>
            <div className="mb-3">
              <label className="text-uppercase small fw-bold text-muted d-block mb-2">Target Roles</label>
              {target_roles?.length > 0 ? (
                target_roles.map((role, i) => (
                  <Badge key={i} pill bg="primary" className="me-1 mb-1 fw-medium">
                    {role}
                  </Badge>
                ))
              ) : <span className="text-muted small">Not specified</span>}
            </div>
            <div>
              <label className="text-uppercase small fw-bold text-muted d-block mb-2">Locations</label>
              {desired_locations?.length > 0 ? (
                desired_locations.map((loc, i) => (
                  <Badge key={i} pill bg="info" className="me-1 mb-1 fw-medium text-white">
                    {loc}
                  </Badge>
                ))
              ) : <span className="text-muted small">Not specified</span>}
            </div>
          </Col>

          {/* Skills & Salary */}
          <Col md={6}>
            <div className="mb-3">
              <label className="text-uppercase small fw-bold text-muted d-block mb-2">Key Skills</label>
              {skills?.length > 0 ? (
                skills.map((skill, i) => (
                  <Badge key={i} pill bg="secondary" className="me-1 mb-1 fw-medium">
                    {skill}
                  </Badge>
                ))
              ) : <span className="text-muted small">Not specified</span>}
            </div>
            <div>
              <label className="text-uppercase small fw-bold text-muted d-block mb-2">Salary Range</label>
              <p className="mb-0 fw-bold text-dark">
                ${salary_min?.toLocaleString() || '0'} — ${salary_max?.toLocaleString() || 'Any'}
              </p>
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default PreferencesSummary;