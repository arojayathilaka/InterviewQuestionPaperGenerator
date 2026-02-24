import React, { useState, useEffect } from 'react';
import { paperAPI } from '../services/api';

const statusColors = {
  completed: 'bg-green-100 text-green-800',
  processing: 'bg-yellow-100 text-yellow-800',
  queued: 'bg-blue-100 text-blue-800',
  failed: 'bg-red-100 text-red-800',
};

const PapersList = ({ userId, onViewPaper, onClose }) => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPapers = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await paperAPI.listUserPapers(userId);
      setPapers(response.papers || []);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [userId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          <span className="ml-4 text-gray-700">Loading your papers...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">My Generated Papers</h2>
        <div className="flex gap-2">
          <button
            onClick={fetchPapers}
            className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
          >
            🔄 Refresh
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-600 hover:text-gray-800 font-semibold text-sm"
            >
              ✕ Close
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {papers.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-semibold">No papers yet</p>
          <p className="text-sm mt-2">Generate your first interview question paper to see it here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {papers.map((paper) => (
            <div
              key={paper.paper_id}
              className="border rounded-lg p-4 hover:shadow-md transition duration-200 cursor-pointer"
              onClick={() => onViewPaper && onViewPaper(paper.paper_id)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 capitalize">
                    {paper.topic}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {paper.created_at
                      ? new Date(paper.created_at).toLocaleString()
                      : 'Unknown date'}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${
                    statusColors[paper.status] || 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {paper.status}
                </span>
              </div>

              <div className="flex gap-6 mt-3 text-sm text-gray-600">
                {paper.questions_count != null && (
                  <span>📝 {paper.questions_count} questions</span>
                )}
                {paper.difficulty_level && (
                  <span className="capitalize">📊 {paper.difficulty_level}</span>
                )}
                {paper.duration_minutes && (
                  <span>⏱️ {paper.duration_minutes} min</span>
                )}
              </div>

              {paper.difficulty_distribution && (
                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                  {Object.entries(paper.difficulty_distribution).map(([k, v]) => (
                    <span key={k} className="capitalize">
                      {k}: {v}
                    </span>
                  ))}
                </div>
              )}

              <p className="text-xs text-gray-400 mt-2 font-mono">{paper.paper_id}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PapersList;
