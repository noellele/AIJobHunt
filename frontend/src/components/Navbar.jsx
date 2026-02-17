import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import LogoutButton from './LogoutButton';

const AppNavbar = () => {
  const { user } = useAuth();

  return (
    <Navbar bg="white" expand="lg" className="shadow-sm border-bottom py-3">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold fs-4 text-primary me-5">
          AI Job Hunt
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        <Navbar.Collapse id="basic-navbar-nav">
          {/* Main Navigation Links */}
          <Nav className="me-auto gap-lg-4">
            {user && <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>}
            {user && <Nav.Link as={Link} to="/search">Search</Nav.Link>}
            <Nav.Link as={Link} to="/about">About</Nav.Link>
          </Nav>

          {/* Account Actions */}
          <Nav className="align-items-center gap-3">
            {user ? (
              <>
                <span className="small text-muted d-none d-xl-inline">
                  Signed in as <strong>{user.name || 'User'}</strong>
                </span>
                <LogoutButton />
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline-primary btn-sm px-3">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm px-3 text-white">
                  Sign Up
                </Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default AppNavbar;