import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Form, Button, Row, Col, Card, InputGroup } from 'react-bootstrap';
import { TagsInput } from "react-tag-input-component";

const PreferencesForm = ({ onSearch, initialData, onCancel }) => {
  const {
    control,
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting }
  } = useForm({
    defaultValues: {
      target_roles: [],
      desired_locations: [],
      skills: [],
      salary_min: 0,
      salary_max: 200000
    }
  });

  useEffect(() => {
    if (initialData) {
      reset(initialData);
    }
  }, [initialData, reset]);

  const onSubmit = (data) => {
    const formattedData = {
      ...data,
      salary_min: Number(data.salary_min),
      salary_max: Number(data.salary_max)
    };
    onSearch(formattedData);
  };


  return (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Body className="p-4">
        <h4 className="mb-4 fw-bold">Job Search Preferences</h4>
        <Form onSubmit={handleSubmit(onSubmit)}>

          {/* Tag Input for Roles */}
          <Form.Group className="mb-3">
            <Form.Label className="small fw-bold text-muted">Target Job Titles</Form.Label>
            <Controller
              name="target_roles"
              control={control}
              rules={{ required: "At least one role is required" }}
              render={({ field }) => (
                <TagsInput
                  value={field.value}
                  onChange={field.onChange}
                  name="roles"
                  placeHolder="Press Enter to add roles (e.g. Software Engineer)"
                />
              )}
            />
            {errors.target_roles && <div className="text-danger small mt-1">{errors.target_roles.message}</div>}
          </Form.Group>

          <Row>
            {/* Tag Input for Locations */}
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Preferred Locations</Form.Label>
                <Controller
                  name="desired_locations"
                  control={control}
                  render={({ field }) => (
                    <TagsInput
                      value={field.value}
                      onChange={field.onChange}
                      placeHolder="e.g. Seattle, Remote"
                    />
                  )}
                />
              </Form.Group>
            </Col>

            {/* Tag Input for Skills */}
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Key Skills</Form.Label>
                <Controller
                  name="skills"
                  control={control}
                  render={({ field }) => (
                    <TagsInput
                      value={field.value}
                      onChange={field.onChange}
                      placeHolder="e.g. Python, React"
                    />
                  )}
                />
              </Form.Group>
            </Col>
          </Row>

          {/* Salary inputs */}
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Minimum Salary ($)</Form.Label>
                <InputGroup hasValidation>
                  <InputGroup.Text>$</InputGroup.Text>
                  <Form.Control
                    type="number"
                    {...register('salary_min', {
                      min: { value: 0, message: 'Salary cannot be negative' },
                      max: { value: 500000, message: 'Max $500k' }
                    })}
                    isInvalid={!!errors.salary_min}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.salary_min?.message}
                  </Form.Control.Feedback>
                </InputGroup>
              </Form.Group>
            </Col>
            
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Maximum Salary ($)</Form.Label>
                <InputGroup hasValidation>
                  <InputGroup.Text>$</InputGroup.Text>
                  <Form.Control
                    type="number"
                    {...register('salary_max', {
                      validate: (value) => {
                        const min = watch('salary_min');
                        if (value && min && Number(value) < Number(min)) {
                          return "Must be ≥ Minimum";
                        }
                        if (Number(value) > 500000) return "Max $500k";
                        return true;
                      }
                    })}
                    isInvalid={!!errors.salary_max}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.salary_max?.message}
                  </Form.Control.Feedback>
                </InputGroup>
              </Form.Group>
            </Col>
          </Row>

          <div className="d-flex justify-content-center gap-3 mt-4">
            <Button 
              variant="primary" 
              type="submit" 
              className="px-5 fw-bold"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Preferences'}
            </Button>
            <Button 
              variant='outline-secondary' 
              onClick={onCancel} 
              className="px-5 fw-bold"
            >
              Cancel
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default PreferencesForm;