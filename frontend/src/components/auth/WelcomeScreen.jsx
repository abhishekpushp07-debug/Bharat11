/**
 * Welcome Screen - First screen users see
 */
import React from 'react';

const WelcomeScreen = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-bg-primary flex flex-col" data-testid="welcome-screen">
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-10">
        <div className="absolute top-20 -left-20 w-64 h-64 rounded-full bg-primary blur-3xl" />
        <div className="absolute bottom-40 -right-20 w-80 h-80 rounded-full bg-primary blur-3xl" />
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 relative z-10">
        {/* Logo */}
        <div className="mb-8 animate-fade-in">
          <div className="w-24 h-24 rounded-full bg-gradient-primary flex items-center justify-center shadow-glow-red">
            <span className="font-display text-3xl font-bold text-white">B11</span>
          </div>
        </div>

        {/* Title */}
        <h1 
          className="font-display text-4xl font-bold text-primary tracking-wider mb-2 text-center animate-fade-in"
          style={{ animationDelay: '100ms' }}
        >
          BHARAT 11
        </h1>
        
        <p 
          className="text-text-secondary text-center mb-8 animate-fade-in"
          style={{ animationDelay: '200ms' }}
        >
          Fantasy Cricket Prediction
        </p>

        {/* Features */}
        <div 
          className="w-full max-w-xs space-y-4 mb-12 animate-fade-in"
          style={{ animationDelay: '300ms' }}
        >
          <div className="flex items-center gap-3 text-text-secondary">
            <div className="w-10 h-10 rounded-full bg-bg-card flex items-center justify-center text-primary">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="font-hindi">11 सवालों के जवाब दो</span>
          </div>
          
          <div className="flex items-center gap-3 text-text-secondary">
            <div className="w-10 h-10 rounded-full bg-bg-card flex items-center justify-center text-primary">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="font-hindi">Leaderboard पर चढ़ो</span>
          </div>
          
          <div className="flex items-center gap-3 text-text-secondary">
            <div className="w-10 h-10 rounded-full bg-bg-card flex items-center justify-center text-gold">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
            <span className="font-hindi">Virtual Coins जीतो</span>
          </div>
        </div>

        {/* Get Started Button */}
        <button
          onClick={onGetStarted}
          className="btn btn-primary w-full max-w-xs text-lg py-4 animate-fade-in"
          style={{ animationDelay: '400ms' }}
          data-testid="get-started-btn"
        >
          Get Started
        </button>
      </div>

      {/* Footer */}
      <div className="py-6 text-center text-text-tertiary text-xs">
        <p>By continuing, you agree to our Terms & Privacy Policy</p>
      </div>
    </div>
  );
};

export default WelcomeScreen;
