import { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Form, Button, Row, Col, Card, InputGroup } from 'react-bootstrap';
import { TagsInput } from "react-tag-input-component";
import usePlacesAutocomplete from "use-places-autocomplete";
import { useJsApiLoader } from "@react-google-maps/api";
import {Combobox, ComboboxInput, ComboboxPopover, ComboboxList, ComboboxOption} from "@reach/combobox";
import { Badge, Stack } from 'react-bootstrap';
import "@reach/combobox/styles.css";

const libraries = ["places"];

// Helper component for Google Places
const LocationAutocomplete = ({ value, onChange }) => {
  const {
    ready,
    value: inputValue,
    suggestions: { status, data },
    setValue,
    clearSuggestions,
  } = usePlacesAutocomplete({
    requestOptions: { types: ["(cities)"] },
    debounce: 300,
  });

  const handleSelect = (address) => {
    setValue(address, false);
    clearSuggestions();
    if (!value.includes(address)) {
      onChange([...value, address]);
    }
    setValue("");
  };

  const removeLocation = (locToRemove) => {
    onChange(value.filter((loc) => loc !== locToRemove));
  };

  return (
    <div className="location-autocomplete-container">
      <Stack direction="horizontal" gap={2} className="flex-wrap mb-3">
        {value.length > 0 ? (
          value.map((loc) => (
            <Badge 
              key={loc} 
              bg="light" 
              text="dark" 
              className="border p-2 d-flex align-items-center fw-normal"
            >
              {loc}
              <Button
                variant="link"
                className="p-0 ms-2 text-danger leading-none"
                style={{ textDecoration: 'none', lineHeight: 1 }}
                onClick={() => removeLocation(loc)}
              >
                &times;
              </Button>
            </Badge>
          ))
        ) : (
          <span className="small text-muted italic">No locations added yet.</span>
        )}
      </Stack>

      <Combobox onSelect={handleSelect}>
        <ComboboxInput
          value={inputValue}
          onChange={(e) => setValue(e.target.value)}
          disabled={!ready}
          className="form-control"
          placeholder="Type a city to add (e.g. San Francisco, CA)"
          onBlur={() => setValue("")}
        />
        <ComboboxPopover style={{ zIndex: 9999 }}>
          <ComboboxList className="border shadow-sm rounded">
            {status === "OK" &&
              data.map(({ place_id, description }) => (
                <ComboboxOption 
                  key={place_id} 
                  value={description} 
                  className="p-2 border-bottom"
                />
              ))}
          </ComboboxList>
        </ComboboxPopover>
      </Combobox>
    </div>
  );
};

const PreferencesForm = ({ onSearch, initialData, onCancel }) => {
  const [roleInput, setRoleInput] = useState("");
  const [skillInput, setSkillInput] = useState("");

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

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries,
  });

  useEffect(() => {
    if (initialData) reset(initialData);
  }, [initialData, reset]);

  if (!isLoaded) {
    return (
      <Card className="shadow-sm border-0 mb-4">
        <Card.Body className="p-4 text-center">
          <h4 className="mb-4 fw-bold text-primary">Loading Search Preferences...</h4>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </Card.Body>
      </Card>
    );
  }

  const onSubmit = (data) => {
    onSearch({
      ...data,
      salary_min: Number(data.salary_min),
      salary_max: Number(data.salary_max)
    });
  };

  return (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Body className="p-4">
        <h4 className="mb-4 fw-bold text-primary">Job Search Preferences</h4>
        <Form onSubmit={handleSubmit(onSubmit)}>

          {/* Roles Input */}
          <Form.Group className="mb-4">
            <Form.Label className="small fw-bold text-muted">Target Job Titles</Form.Label>
            <Controller
              name="target_roles"
              control={control}
              rules={{ required: "At least one role is required" }}
              render={({ field }) => (
                <TagsInput
                  value={field.value}
                  onChange={field.onChange}
                  onInputChange={(val) => setRoleInput(val)}
                  separators={[",", "Tab"]}
                  placeHolder="Add..."
                />
              )}
            />
            {errors.target_roles && <div className="text-danger small mt-1">{errors.target_roles.message}</div>}
            <Form.Text className="text-muted" style={{ fontSize: '0.75rem' }}>
              Press <strong>Comma</strong> or <strong>Tab</strong> to add a title.
            </Form.Text>
          </Form.Group>

          <Row>
            {/* Google Places Location Input */}
            <Col md={6}>
              <Form.Group className="mb-4">
                <Form.Label className="small fw-bold text-muted">Preferred Locations</Form.Label>
                <Controller
                  name="desired_locations"
                  control={control}
                  render={({ field }) => (
                    <LocationAutocomplete value={field.value} onChange={field.onChange} />
                  )}
                />
              </Form.Group>
            </Col>

            {/* Skills Input */}
            <Col md={6}>
              <Form.Group className="mb-4">
                <Form.Label className="small fw-bold text-muted">Key Skills</Form.Label>
                <Controller
                  name="skills"
                  control={control}
                  render={({ field }) => (
                    <TagsInput
                      value={field.value}
                      onChange={field.onChange}
                      onInputChange={(val) => setSkillInput(val)}
                      onBlur={() => {
                        if (skillInput.trim() && !field.value.includes(skillInput.trim())) {
                          field.onChange([...field.value, skillInput.trim()]);
                          setSkillInput("");
                        }
                      }}
                      separators={[",", "Tab"]}
                      placeHolder="Add..."
                    />
                  )}
                />
                <Form.Text className="text-muted" style={{ fontSize: '0.75rem' }}>
                  Press <strong>Comma</strong> or <strong>Tab</strong> to add a skill.
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

          {/* Salary Section */}
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Min Salary</Form.Label>
                <InputGroup>
                  <InputGroup.Text>$</InputGroup.Text>
                  <Form.Control
                    type="number"
                    {...register('salary_min')}
                    isInvalid={!!errors.salary_min}
                  />
                </InputGroup>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="small fw-bold text-muted">Max Salary</Form.Label>
                <InputGroup>
                  <InputGroup.Text>$</InputGroup.Text>
                  <Form.Control
                    type="number"
                    {...register('salary_max', {
                      validate: (val) => Number(val) >= Number(watch('salary_min')) || "Must be higher than min"
                    })}
                    isInvalid={!!errors.salary_max}
                  />
                  <Form.Control.Feedback type="invalid">{errors.salary_max?.message}</Form.Control.Feedback>
                </InputGroup>
              </Form.Group>
            </Col>
          </Row>

          <div className="d-flex justify-content-center gap-3 mt-4">
            <Button variant="primary" type="submit" className="px-5 fw-bold" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Preferences'}
            </Button>
            <Button variant="outline-secondary" onClick={onCancel} className="px-5">Cancel</Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default PreferencesForm;