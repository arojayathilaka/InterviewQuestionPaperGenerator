import React, { useState } from 'react';
import { paperAPI } from '../services/api';

const PaperGenerationForm = ({ onPaperGenerated, userId }) => {
  const [formData, setFormData] = useState({
    technology_topic: '',
    num_questions: 10,
    difficulty_level: 'mixed',
    question_types: ['multiple_choice'],
    duration_minutes: 60,
    preferences: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCheckboxChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      question_types: checked
        ? [...prev.question_types, value]
        : prev.question_types.filter(type => type !== value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validate inputs
      if (!formData.technology_topic.trim()) {
        throw new Error('Please enter a technology topic');
      }
      if (formData.num_questions < 1 || formData.num_questions > 100) {
        throw new Error('Number of questions must be between 1 and 100');
      }
      if (formData.question_types.length === 0) {
        throw new Error('Please select at least one question type');
      }

      const request = {
        user_id: userId,
        ...formData,
      };

      const response = await paperAPI.generatePaper(request);
      
      setSuccess(`Paper generation started! Paper ID: ${response.paper_id}`);
      setFormData({
        technology_topic: '',
        num_questions: 10,
        difficulty_level: 'mixed',
        question_types: ['multiple_choice'],
        duration_minutes: 60,
        preferences: '',
      });

      if (onPaperGenerated) {
        onPaperGenerated(response.paper_id);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail?.message || err.message || 'Failed to generate paper';
      setError(errorMessage);
      console.error('Paper generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Generate Question Paper</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Technology Topic *
        </label>
        <input
          type="text"
          name="technology_topic"
          value={formData.technology_topic}
          onChange={handleInputChange}
          placeholder="e.g., Python Async Programming, React Hooks"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-gray-700 font-semibold mb-2">
            Number of Questions
          </label>
          <input
            type="number"
            name="num_questions"
            value={formData.num_questions}
            onChange={handleInputChange}
            min="1"
            max="100"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold mb-2">
            Difficulty Level
          </label>
          <select
            name="difficulty_level"
            value={formData.difficulty_level}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
            <option value="mixed">Mixed</option>
          </select>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Question Types
        </label>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              value="multiple_choice"
              checked={formData.question_types.includes('multiple_choice')}
              onChange={handleCheckboxChange}
              className="mr-2"
            />
            <span>Multiple Choice</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              value="short_answer"
              checked={formData.question_types.includes('short_answer')}
              onChange={handleCheckboxChange}
              className="mr-2"
            />
            <span>Short Answer</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              value="essay"
              checked={formData.question_types.includes('essay')}
              onChange={handleCheckboxChange}
              className="mr-2"
            />
            <span>Essay</span>
          </label>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Exam Duration (minutes)
        </label>
        <input
          type="number"
          name="duration_minutes"
          value={formData.duration_minutes}
          onChange={handleInputChange}
          min="15"
          max="180"
          step="15"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
        />
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 font-semibold mb-2">
          Additional Preferences
        </label>
        <textarea
          name="preferences"
          value={formData.preferences}
          onChange={handleInputChange}
          placeholder="e.g., Focus on best practices, include real-world scenarios"
          rows="4"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
      >
        {loading ? 'Generating...' : 'Generate Paper'}
      </button>
    </form>
  );
};

export default PaperGenerationForm;
