import React, { useState, useEffect } from 'react';
import PaperGenerationForm from '../components/PaperGenerationForm';
import PaperResults from '../components/PaperResults';
import PapersList from '../components/PapersList';
import UserRegistration from '../components/UserRegistration';

const HomePage = () => {
  const [userId, setUserId] = useState(localStorage.getItem('user_id'));
  const [generatedPaperId, setGeneratedPaperId] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [showPapersList, setShowPapersList] = useState(false);

  const handleUserRegistered = (id) => {
    setUserId(id);
  };

  const handlePaperGenerated = (paperId) => {
    setGeneratedPaperId(paperId);
    setShowResults(true);
    setShowPapersList(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Interview Question Paper Generator
          </h1>
          <p className="text-gray-600 text-lg">
            Generate customized interview question papers using AI
          </p>
        </header>

        {!userId ? (
          <div className="mb-12">
            <UserRegistration onRegistered={handleUserRegistered} />
          </div>
        ) : (
          <>
            <div className="mb-8 text-center">
              <p className="text-gray-700 font-semibold">
                Welcome, {localStorage.getItem('user_name')}!
              </p>
              <div className="mt-2 flex justify-center gap-4">
                <button
                  onClick={() => {
                    setShowPapersList(true);
                    setShowResults(false);
                  }}
                  className="text-sm bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-1 px-4 rounded-lg transition duration-200"
                >
                  📄 My Papers
                </button>
                <button
                  onClick={() => {
                    localStorage.clear();
                    setUserId(null);
                    setShowResults(false);
                    setShowPapersList(false);
                  }}
                  className="text-sm text-red-600 hover:text-red-800 font-semibold"
                >
                  Sign Out
                </button>
              </div>
            </div>

            {showPapersList ? (
              <PapersList
                userId={userId}
                onViewPaper={(paperId) => {
                  setGeneratedPaperId(paperId);
                  setShowResults(true);
                  setShowPapersList(false);
                }}
                onClose={() => setShowPapersList(false)}
              />
            ) : showResults ? (
              <PaperResults
                paperId={generatedPaperId}
                onClose={() => {
                  setShowResults(false);
                  setShowPapersList(true);
                }}
              />
            ) : (
              <PaperGenerationForm
                userId={userId}
                onPaperGenerated={handlePaperGenerated}
              />
            )}
          </>
        )}

        <footer className="mt-12 text-center text-gray-600 text-sm">
          <p>© 2024 Interview Question Paper Generator. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default HomePage;
