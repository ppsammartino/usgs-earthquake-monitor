import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Form, Button, Row, Col } from 'react-bootstrap';
import { URLS } from '../config/api';
import './EarthquakeSearchForm.css';

function EarthquakeSearchForm() {
  const [cities, setCities] = useState([]);
  const [cityId, setCityId] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const response = await axios.get(URLS.CITIES);
        setCities(response.data);
      } catch (err) {
        setError('Failed to load cities');
      }
    };
    fetchCities();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    if (!cityId || !start || !end) {
      setError('Please fill out all fields');
      setLoading(false)
      return;
    }

    try {
      const response = await axios.post(URLS.EARTHQUAKES, {
        city_id: Number(cityId),
        start,
        end,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="earthquake-form-container">
      <h3 className="earthquake-form-title">Search Earthquakes</h3>
      <Form onSubmit={handleSubmit}>
        <Row>
          <Col md={6}>
            <Form.Group controlId="citySelect">
              <Form.Label>Select City</Form.Label>
              <Form.Control
                as="select"
                value={cityId}
                onChange={(e) => setCityId(e.target.value)}
                disabled={loading}
              >
                <option value="">-- Choose a city --</option>
                {cities.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="startDate">
              <Form.Label>Start Date</Form.Label>
              <Form.Control
                type="date"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                disabled={loading}
              />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group controlId="endDate">
              <Form.Label>End Date</Form.Label>
              <Form.Control
                type="date"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                disabled={loading}
              />
            </Form.Group>
          </Col>
        </Row>

        <Button variant="primary" type="submit" style={{ marginTop: '1rem', width: '100%'}} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </Form>

      {error && (
        <div style={{ color: 'red', marginTop: '1rem' }}>
          {error}
        </div>
      )}

      {result && (
        <div className="result-section">
          <p>{result.verbose_msg}</p>
        </div>
      )}
    </div>
  );
}

export default EarthquakeSearchForm;
