import React, { useState } from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import EarthquakeSearchForm from './components/EarthquakeSearchForm';
import SearchHistoryList from './components/SearchHistoryList';

function App() {
  const [activeView, setActiveView] = useState('search');

  return (
    <div>
      <Navbar bg="dark" variant="dark" expand="md">
        <Navbar.Brand style={{ marginLeft: '1rem' }}>USGS Earthquake Monitor</Navbar.Brand>
        <Nav className="ml-auto" style={{ marginLeft: 'auto', marginRight: '1rem' }}>
          <Nav.Link onClick={() => setActiveView('search')}>Search</Nav.Link>
          <Nav.Link onClick={() => setActiveView('history')}>History</Nav.Link>
        </Nav>
      </Navbar>

      <Container style={{ marginTop: '2rem' }}>
        {activeView === 'search' && <EarthquakeSearchForm />}
        {activeView === 'history' && <SearchHistoryList />}
      </Container>
    </div>
  );
}

export default App;
