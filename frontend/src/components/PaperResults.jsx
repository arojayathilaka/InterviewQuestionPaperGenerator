import React, { useState, useEffect } from 'react';
import { paperAPI } from '../services/api';

const PaperResults = ({ paperId, onClose }) => {
  const [paper, setPaper] = useState(null);
  const [jsonPreview, setJsonPreview] = useState(null);
  const [previewError, setPreviewError] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    if (!paperId) return;

    let isCancelled = false;
    let pollInterval = null;

    const fetchPaperStatus = async () => {
      try {
        const statusResponse = await paperAPI.getPaperStatus(paperId);
        if (isCancelled) return;
        setStatus(statusResponse.status);

        if (statusResponse.status === 'completed') {
          const paperResponse = await paperAPI.getPaper(paperId);
          if (!isCancelled) setPaper(paperResponse);
          // Stop polling — we're done
          if (pollInterval) clearInterval(pollInterval);
        } else if (statusResponse.status === 'failed') {
          // Stop polling — terminal state
          if (pollInterval) clearInterval(pollInterval);
        }
        if (!isCancelled) setLoading(false);
      } catch (err) {
        if (!isCancelled) {
          setError(err.response?.data?.detail?.message || 'Failed to fetch paper');
          setLoading(false);
        }
      }
    };

    fetchPaperStatus();

    // Poll for status every 5 seconds if not completed
    pollInterval = setInterval(fetchPaperStatus, 5000);

    return () => {
      isCancelled = true;
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [paperId]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <span className="ml-4 text-gray-700">Generating your paper...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <p className="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Question Paper</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-gray-800 font-semibold"
          >
            ✕ Close
          </button>
        )}
      </div>

      {status === 'completed' && paper ? (
        <>
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="text-lg font-semibold text-gray-800">{paper.topic}</p>
            <p className="text-sm text-gray-600 mt-2">
              Generated: {new Date(paper.created_at).toLocaleString()}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded">
              <p className="text-gray-600 font-semibold">Total Questions</p>
              <p className="text-2xl font-bold text-blue-600">{paper.questions_count}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded">
              <p className="text-gray-600 font-semibold">Status</p>
              <p className="text-2xl font-bold text-green-600 capitalize">{paper.status}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded">
              <p className="text-gray-600 font-semibold">Paper ID</p>
              <p className="text-sm font-mono text-gray-700 break-all">{paper.paper_id}</p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Difficulty Distribution</h3>
            <div className="grid grid-cols-3 gap-4">
              {paper.difficulty_distribution && Object.entries(paper.difficulty_distribution).map(
                ([difficulty, count]) => (
                  <div key={difficulty} className="p-4 border rounded-lg">
                    <p className="text-gray-600 capitalize font-semibold">{difficulty}</p>
                    <p className="text-3xl font-bold text-blue-600">{count}</p>
                  </div>
                )
              )}
            </div>
          </div>

          <div className="mb-6 flex gap-4">
            <button
              className="inline-block bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
              onClick={async () => {
                try {
                  const data = await paperAPI.getPaperContent(paper.paper_id);
                  // Build a text file from the formatted_content or questions
                  let text = '';
                  if (data.formatted_content?.formatted_paper) {
                    text = data.formatted_content.formatted_paper;
                  } else {
                    text = `Interview Questions: ${data.topic || paper.topic}\n`;
                    text += `Duration: ${data.duration_minutes || ''} minutes\n\n`;
                    // Parse questions
                    let questions = [];
                    if (data.questions) {
                      for (const q of data.questions) {
                        if (q.question_text || q.question) {
                          questions.push(q);
                        } else if (q.raw) {
                          try {
                            const cleaned = q.raw.replace(/^```json\s*/i, '').replace(/```\s*$/, '').trim();
                            const parsed = JSON.parse(cleaned);
                            if (Array.isArray(parsed)) questions.push(...parsed);
                            else questions.push(parsed);
                          } catch (e) {}
                        }
                      }
                    }
                    questions.forEach((q, i) => {
                      text += `Q${i + 1}. ${q.question_text || q.question}\n`;
                      if (q.options) {
                        q.options.forEach((opt, j) => {
                          text += `   ${String.fromCharCode(97 + j)}) ${opt}\n`;
                        });
                      }
                      if (q.correct_answer || q.answer) {
                        text += `   Answer: ${q.correct_answer || q.answer}\n`;
                      }
                      if (q.explanation) {
                        text += `   Explanation: ${q.explanation}\n`;
                      }
                      text += '\n';
                    });
                  }
                  // Create and download text file
                  const blob = new Blob([text], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${paper.paper_id}.txt`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                } catch (err) {
                  setPreviewError(err.response?.data?.detail?.message || err.message || 'Failed to download paper');
                }
              }}
            >
              📥 Download Paper
            </button>
            <button
              className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
              onClick={async () => {
                setPreviewError('');
                setJsonPreview(null);
                try {
                  const data = await paperAPI.getPaperContent(paper.paper_id);
                  setJsonPreview(data);
                } catch (err) {
                  setPreviewError(err.response?.data?.detail?.message || err.message || 'Failed to preview paper');
                }
              }}
            >
              👁️ Preview Paper
            </button>
          </div>
          {previewError && (
            <div className="mb-4 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
              {previewError}
            </div>
          )}
          {jsonPreview && (() => {
            // Parse questions from the raw field if needed
            let parsedQuestions = [];
            if (jsonPreview.questions) {
              for (const q of jsonPreview.questions) {
                if (q.question_text) {
                  parsedQuestions.push(q);
                } else if (q.question) {
                  parsedQuestions.push(q);
                } else if (q.raw) {
                  try {
                    const cleaned = q.raw.replace(/^```json\s*/i, '').replace(/```\s*$/, '').trim();
                    const parsed = JSON.parse(cleaned);
                    if (Array.isArray(parsed)) {
                      parsedQuestions.push(...parsed);
                    } else {
                      parsedQuestions.push(parsed);
                    }
                  } catch (e) {
                    // skip unparseable
                  }
                }
              }
            }

            return (
              <div className="mb-6 p-6 bg-white border rounded-lg shadow-sm overflow-y-auto max-h-[600px]">
                <h4 className="text-xl font-bold mb-4 text-gray-800 border-b pb-2">
                  📋 {jsonPreview.formatted_content?.title || jsonPreview.topic || 'Paper Preview'}
                </h4>
                <div className="flex gap-6 mb-4 text-sm text-gray-600">
                  <span>⏱️ Duration: {jsonPreview.duration_minutes} minutes</span>
                  {jsonPreview.formatted_content?.total_marks && (
                    <span>📊 Total Marks: {jsonPreview.formatted_content.total_marks}</span>
                  )}
                </div>
                {jsonPreview.formatted_content?.instructions && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-gray-700">
                    <strong>Instructions:</strong> {jsonPreview.formatted_content.instructions}
                  </div>
                )}

                {parsedQuestions.length > 0 ? (
                  <ol className="list-none space-y-5">
                    {parsedQuestions.map((q, idx) => (
                      <li key={idx} className="p-4 bg-gray-50 rounded-lg border">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-semibold text-gray-800">
                            Q{idx + 1}. {q.question_text || q.question}
                          </span>
                          {q.difficulty_level && (
                            <span className={`text-xs px-2 py-1 rounded-full font-semibold ml-2 whitespace-nowrap ${
                              q.difficulty_level === 'easy' ? 'bg-green-100 text-green-700' :
                              q.difficulty_level === 'hard' ? 'bg-red-100 text-red-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>
                              {q.difficulty_level}
                            </span>
                          )}
                        </div>
                        {q.topic && (
                          <div className="text-xs text-gray-400 mb-2">Topic: {q.topic}</div>
                        )}
                        {q.options && Array.isArray(q.options) && q.options.length > 0 && (
                          <ul className="ml-4 mt-2 space-y-1">
                            {q.options.map((opt, i) => (
                              <li key={i} className="text-gray-700 text-sm">
                                <span className="font-medium text-gray-500 mr-1">{String.fromCharCode(97 + i)})</span> {opt}
                              </li>
                            ))}
                          </ul>
                        )}
                        {(q.correct_answer || q.answer) && (
                          <div className="mt-2 text-sm text-green-700 bg-green-50 p-2 rounded">
                            <strong>Answer:</strong> {q.correct_answer || q.answer}
                          </div>
                        )}
                        {q.explanation && (
                          <div className="mt-1 text-sm text-gray-500 italic">
                            💡 {q.explanation}
                          </div>
                        )}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <div className="text-gray-500 text-sm">No questions found in the paper data.</div>
                )}
              </div>
            );
          })()}

          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Paper Details</h3>
            <div className="space-y-2 text-gray-700">
              <p><strong>Paper ID:</strong> {paper.paper_id}</p>
              <p><strong>Topic:</strong> {paper.topic}</p>
              <p><strong>User ID:</strong> {paper.user_id}</p>
              <p><strong>Created:</strong> {new Date(paper.created_at).toLocaleString()}</p>
            </div>
          </div>
        </>
      ) : status === 'queued' ? (
        <div className="p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
          <p className="font-semibold">Processing</p>
          <p>Your paper is being generated. This may take a few moments...</p>
          <p className="mt-2 text-sm">Paper ID: {paperId}</p>
        </div>
      ) : (
        <div className="p-4 bg-gray-100 border border-gray-300 text-gray-700 rounded">
          <p className="font-semibold">Status: {status}</p>
        </div>
      )}
    </div>
  );
};

export default PaperResults;
