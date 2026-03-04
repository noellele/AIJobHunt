import { Card, Badge, Button, Stack, Row, Col, Spinner } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const JobCard = ({ job, initialSaved, onUnsave }) => {
  const title = job.title || "Position Title";
  const company = job.company || "Company Name";
  const location = job.location || job.job_location || "Remote / Not Listed";
  const salary_range = job.salary_range || {};
  const externalUrl = job.url || job.job_url || "#";
  const { user } = useAuth();
  const [isSaved, setIsSaved] = useState(initialSaved);
  const [isLoading, setIsLoading] = useState(false);
  const [matchData, setMatchData] = useState(null);

  const fetchMatchScore = async (uId, jId) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    try {
      const res = await api.get(
        `/ml/matches/user/${uId}/job/${jId}`,
        { signal: controller.signal }
      );
      setMatchData(res.data);
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error("Error fetching match score:", err);
      }
      setMatchData({ score: 0, missing_skills: [] });
    } finally {
      clearTimeout(timeoutId);
    }
  };

  useEffect(() => {
    setIsSaved(initialSaved);
    const effectiveJobId = job.job_id || job._id || job.id;
    const effectiveUserId = user?.id;

    if (effectiveUserId && effectiveJobId && effectiveJobId !== "undefined") {
      fetchMatchScore(effectiveUserId, effectiveJobId);
    }
  }, [initialSaved, job, user?.id]);

  const missingSkills = matchData?.missing_skills || [];

  const handleSaveJob = async () => {
    if (!user?.id || isSaved || isLoading) return;
    setIsLoading(true);
    try {
      const response = await api.post(`/interactions/`, {
        user_id: user.id,
        job_id: job.job_id || job.id || job._id,
        interaction_type: 'saved'
      });
      if (response.status === 200 || response.status === 201) {
        setIsSaved(true);
      }
    } catch (error) {
      console.error("Save failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

const handleUnsaveJob = async () => {
  if (!user?.id || isLoading) return;
  
  const jobId = (job.job_id || job._id || job.id)?.toString().trim();
  const userId = user.id.toString().trim();

  setIsLoading(true);
  try {
    // encodeURIComponent handles any weird characters or spaces
    await api.delete(`/interactions/user/${encodeURIComponent(userId)}/job/${encodeURIComponent(jobId)}`);
    
    setIsSaved(false);
    if (onUnsave) onUnsave();
  } catch (error) {
    console.error("Unsave failed:", error.response?.data || error.message);
  } finally {
    setIsLoading(false);
  }
};

  const getScoreColor = (score) => {
    const s = score * 100;
    if (s >= 80) return 'success';
    if (s >= 50) return 'warning';
    return 'danger';
  };

  const formatSalary = (num) => {
    if (!num) return null;
    const integerVal = Math.floor(num);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(integerVal);
  };


  return (
    <Card className="mb-3 border-0 shadow-sm hover-shadow transition-all w-100 text-start">
      <Card.Body className="p-4">
        <Row className="align-items-center">
          <Col xs="auto" className="pe-4 border-end">
            <div className="ms-3" style={{ width: '55px' }}>
              {!matchData ? (
                <div className="d-flex align-items-center justify-content-center" style={{ height: '55px' }}>
                  <Spinner animation="border" size="sm" variant="secondary" />
                </div>
              ) : (
                <>
                  <div
                    className={`d-flex align-items-center justify-content-center border border-2 border-${getScoreColor(matchData.score)} rounded-circle shadow-sm`}
                    style={{ width: '55px', height: '55px', backgroundColor: '#fff' }}
                  >
                    <span className={`fw-bold text-${getScoreColor(matchData.score)}`} style={{ fontSize: '0.9rem' }}>
                      {matchData.score !== null ? `${Math.round(matchData.score * 100)}%` : "0%"}
                    </span>
                  </div>
                  <div className="text-muted fw-bold mt-1" style={{ fontSize: '0.6rem', letterSpacing: '0.5px', textAlign: 'center' }}>
                    AI MATCH
                  </div>
                </>
              )}
            </div>
          </Col>

          <Col className="ps-4">
            <Card.Title className="mb-1 fw-bold text-primary fs-5">
              {title}
            </Card.Title>
            <Card.Subtitle className="mt-1 mb-3 text-muted fw-medium">
              <i className="bi bi-building me-1"></i> {company}
              <span className="mx-2 text-silver">|</span>
              <i className="bi bi-geo-alt me-1"></i> {location}
            </Card.Subtitle>
          </Col>

          <Col xs="auto" className="text-end">
            <div className="fw-bold text-success fs-5">
              {salary_range?.min
                ? `${formatSalary(salary_range.min)}${salary_range.max ? ` - ${formatSalary(salary_range.max)}` : ''}`
                : "Salary not listed"}
            </div>
          </Col>
        </Row>

        <hr className="my-3 opacity-10" />

        <div className="d-flex align-items-baseline mb-3">
          <i className='bi bi-lightning-fill text-warning me-2 mt-1'></i>
          <div className="small fw-bold text-muted mb-2 uppercase tracking-wider" style={{ fontSize: '0.75rem' }}>
            MISSING SKILLS:
          </div>
          <Stack direction="horizontal" gap={2} className="flex-wrap mx-2">
            {matchData && missingSkills.length > 0 ? (
              missingSkills.map((skill, index) => (
                <Badge key={index} pill bg="light" text="dark" className="border fw-normal text-secondary" style={{ fontSize: '0.7rem' }}>
                  {skill}
                </Badge>
              ))
            ) : matchData ? (
              <span className="text-success small" style={{ fontSize: '0.75rem' }}>
                <i className="bi bi-check-circle-fill me-1"></i> You have all required skills!
              </span>
            ) : (
              <span className="text-muted small">Calculating gaps...</span>
            )}
          </Stack>
        </div>

        <div className="d-flex justify-content-between align-items-center mt-auto pt-2">
          <Button
            variant="outline-primary"
            size="sm"
            className="fw-bold px-3"
            onClick={() => window.open(externalUrl, '_blank', 'noopener,noreferrer')}
          >
            View Posting <i className="bi bi-box-arrow-up-right ms-1"></i>
          </Button>

          <div className="d-flex align-items-center">
            {isSaved ? (
              <Stack direction="horizontal" gap={3}>
                <span className="text-success small fw-medium">
                  <i className="bi bi-bookmark-check-fill me-1"></i> Saved
                </span>
                <Button variant="outline-danger" size="sm" className="py-1 px-2" style={{ fontSize: '0.7rem' }} onClick={handleUnsaveJob} disabled={isLoading}>
                  {isLoading ? <Spinner animation="border" size="sm" /> : "Unsave"}
                </Button>
              </Stack>
            ) : (
              <Button variant="link" className="text-decoration-none p-0 small text-muted" onClick={handleSaveJob} disabled={isLoading}>
                {isLoading ? <Spinner animation="border" size="sm" /> : (
                  <><i className="bi bi-bookmark me-1"></i> Save for later</>
                )}
              </Button>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}

export default JobCard;