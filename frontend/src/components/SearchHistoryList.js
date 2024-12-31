import React, { useEffect, useState } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';
import { Button } from 'react-bootstrap';
import { URLS } from '../config/api';
import './SearchHistoryList.css';

function SearchHistoryList() {
  const [history, setHistory] = useState([]);
  const [count, setCount] = useState(0);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory(page, pageSize);
  }, [page, pageSize]);

  const fetchHistory = async (pageNumber, size) => {
    setError(null);
    try {
      const response = await axios.get(`${URLS.EARTHQUAKES}?page=${pageNumber}&page_size=${size}`);
      const data = response.data;
      setCount(data.count);
      setNextUrl(data.next);
      setPrevUrl(data.previous);
      setHistory(data.results || []);
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load history');
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A';
    return dayjs(isoString).format('D MMMM YYYY, HH:mm');
  };

  const goNext = () => {
    if (nextUrl) {
      setPage(page + 1);
    }
  };

  const goPrev = () => {
    if (prevUrl && page > 1) {
      setPage(page - 1);
    }
  };

  return (
    <div className="history-search-container">
      <h3>Search History</h3>
      {error && <div style={{ color: 'red' }}>{error}</div>}

      {/* Page Size Selector */}
      <div style={{ marginBottom: '1rem' }}>
        <label>Page Size: </label>
        <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="20">20</option>
        </select>
      </div>

      <div className="results-list">
        {history.map((item) => (
          <div className="history-item" key={item.id}>
            <strong>City:</strong> {item.city_name || item.city} <br />
            <strong>Nearest EQ:</strong> {item.nearest_earthquake_location || 'N/A'} <br />
            <strong>Magnitude:</strong> {item.nearest_earthquake_magnitude || 'N/A'} <br />
            <strong>Time:</strong> {formatDate(item.nearest_earthquake_time)} <br />
            <strong>Description:</strong> {item.verbose_msg}
          </div>
        ))}
      </div>

      <div style={{marginTop: '1rem', display: 'flex', justifyContent: 'space-between'}}>
        <Button variant="secondary" onClick={goPrev} disabled={!prevUrl || page <= 1}>
          Previous
        </Button>
        <span style={{marginLeft: '1rem'}}>Page {page} / {totalPages} - Total Results: {count}</span>
        <Button variant="secondary" onClick={goNext} disabled={!nextUrl}>
          Next
        </Button>
      </div>
    </div>
  );
}

export default SearchHistoryList;
