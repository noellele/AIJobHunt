import React from 'react';
import { Container, Button, Row, Col, Stack } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import FeatureGrid from '../components/FeatureGrid';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user } = useAuth();

  const homeFeatures = [
    {
      title: "Set Your Criteria",
      text: "Define your ideal roles, must-have skills, and salary requirements in seconds.",
      icon: "bi-sliders"
    },
    {
      title: "AI Discovery",
      text: "Our AI scans job metadata to find matches that align with your unique profile.",
      icon: "bi-search"
    },
    {
      title: "Land the Role",
      text: "Focus your energy on applying to high-signal leads instead of sorting through noise.",
      icon: "bi-check-circle"
    }
  ];

  return (
    <div className="home-page">
      <section className="bg-white py-5 mb-5 border-bottom">
        <Container className="py-5">
          <Row className="justify-content-center text-center">
            <Col lg={8}>
              <h1 className="display-3 fw-bold text-dark mb-4">
                Your Personal <span className="text-primary">Career Scout</span>
              </h1>
              <p className="fs-4 text-secondary mb-5 px-lg-5">
                Precision matching for the modern professional.
              </p>
              <Stack direction="horizontal" gap={3} className="justify-content-center">
                {user ? (
                  <Button as={Link} to="/register" size="lg" className="px-4 fw-bold shadow-sm">
                    Get Started
                  </Button>
                ) : (
                  <>
                    <Button as={Link} to="/register" size="lg" className="px-4 fw-bold shadow-sm">
                      Get Started
                    </Button>
                    <Button as={Link} to="/login" variant="outline-primary" size="lg" className="px-4 fw-bold">
                      Sign In
                    </Button>
                  </>
                )}
              </Stack>
            </Col>
          </Row>
        </Container>
      </section>

      <Container className="py-5">
        <div className="text-center mb-5">
          <h2 className="fw-bold">How It Works</h2>
          <p className="text-muted">A streamlined path to your next opportunity.</p>
        </div>
        
        <FeatureGrid items={homeFeatures} columns={4} />

        <div className="bg-light rounded-4 p-5 text-center mt-5 shadow-sm border">
          <h3 className="fw-bold mb-3">Ready to bridge the gap?</h3>
          <p className="text-secondary mb-4 mx-auto" style={{ maxWidth: '600px' }}>
            Join professionals who are using automated discovery to reclaim their time and land roles that actually fit their capabilities.
          </p>
          <Button as={Link} to="/about" variant="link" className="text-decoration-none fw-bold">
            Learn more about our vision <i className="bi bi-arrow-right ms-1"></i>
          </Button>
        </div>
      </Container>
    </div>
  );
};

export default Home;