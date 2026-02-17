import React from 'react';
import { Card } from 'react-bootstrap';

const DashboardCard = ({ title, icon, children, footer, className = "" }) => {
  return (
    <Card className={`h-100 shadow-sm border rounded-3 bg-light ${className}`}>
      <Card.Body className="p-4">
        {title && (
          <div className="d-flex align-items-center mb-3">
            {icon && <span className="me-2 fs-5 text-primary">{icon}</span>}
            <h6 className="mb-0 fw-bold text-uppercase small text-secondary tracking-wider">
              {title}
            </h6>
          </div>
        )}
        <div className="card-content">
          {children}
        </div>
      </Card.Body>
      {footer && (
        <Card.Footer className="bg-transparent border-0 pt-0 px-4 pb-4">
          {footer}
        </Card.Footer>
      )}
    </Card>
  );
};

export default DashboardCard;