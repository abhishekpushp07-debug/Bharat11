/**
 * PIN Input Screen - Create or Enter PIN
 */
import React, { useState, useRef, useEffect } from 'react';

const PinScreen = ({ 
  mode = 'create', // 'create', 'confirm', 'login'
  phone,
  onSubmit, 
  onBack,
  isLoading = false,
  error = '',
  onForgotPin = null
}) => {
  const [pin, setPin] = useState(['', '', '', '']);
  const [localError, setLocalError] = useState('');
  const inputRefs = [useRef(), useRef(), useRef(), useRef()];

  useEffect(() => {
    inputRefs[0].current?.focus();
  }, []);

  useEffect(() => {
    // Clear PIN on error
    if (error) {
      setPin(['', '', '', '']);
      inputRefs[0].current?.focus();
    }
  }, [error]);

  const handleChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;
    
    const newPin = [...pin];
    newPin[index] = value;
    setPin(newPin);
    setLocalError('');

    // Auto-focus next input
    if (value && index < 3) {
      inputRefs[index + 1].current?.focus();
    }

    // Auto-submit when complete
    if (value && index === 3) {
      const fullPin = newPin.join('');
      if (fullPin.length === 4) {
        setTimeout(() => onSubmit(fullPin), 100);
      }
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !pin[index] && index > 0) {
      inputRefs[index - 1].current?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 4);
    if (pastedData.length === 4) {
      const newPin = pastedData.split('');
      setPin(newPin);
      onSubmit(pastedData);
    }
  };

  const titles = {
    create: { 
      title: 'Create your PIN', 
      subtitle: 'एक 4-digit PIN बनाएं',
      hint: 'This PIN will be your password'
    },
    confirm: { 
      title: 'Confirm your PIN', 
      subtitle: 'PIN दोबारा दर्ज करें',
      hint: 'Enter the same PIN again'
    },
    login: { 
      title: 'Enter your PIN', 
      subtitle: 'अपना PIN दर्ज करें',
      hint: `Logging in as ${phone}`
    }
  };

  const { title, subtitle, hint } = titles[mode];
  const displayError = error || localError;

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col" data-testid="pin-screen">
      {/* Header */}
      <header className="flex items-center p-4 safe-top">
        <button 
          onClick={onBack}
          className="w-10 h-10 rounded-full bg-bg-card flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors"
          disabled={isLoading}
          data-testid="back-btn"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 px-6 pt-8">
        <div className="mb-12 text-center">
          <h1 className="text-2xl font-semibold text-text-primary mb-2">
            {title}
          </h1>
          <p className="text-text-secondary font-hindi">
            {subtitle}
          </p>
        </div>

        {/* PIN Input */}
        <div className="pin-input-container mb-6" data-testid="pin-inputs">
          {pin.map((digit, index) => (
            <input
              key={index}
              ref={inputRefs[index]}
              type="tel"
              inputMode="numeric"
              pattern="\d*"
              maxLength={1}
              value={digit ? '•' : ''}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              disabled={isLoading}
              className={`pin-input ${digit ? 'filled' : ''} ${displayError ? 'border-primary' : ''}`}
              data-testid={`pin-input-${index}`}
            />
          ))}
        </div>

        {/* Error Message */}
        {displayError && (
          <div className="text-center mb-6 animate-fade-in" data-testid="pin-error">
            <p className="text-primary text-sm">{displayError}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center mb-6">
            <div className="w-8 h-8 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        )}

        {/* Hint */}
        <p className="text-center text-text-tertiary text-sm">
          {hint}
        </p>

        {/* Security Note */}
        <div className="mt-12 flex items-start gap-3 p-4 bg-bg-card rounded-xl">
          <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-text-secondary text-sm font-hindi">
              आपका PIN सुरक्षित रूप से एन्क्रिप्टेड है। हम इसे कभी नहीं देख सकते।
            </p>
          </div>
        </div>
      </div>

      {/* Forgot PIN (only for login) - positioned above the Create Account link */}
      {mode === 'login' && onForgotPin && (
        <div className="py-4 text-center pb-16">
          <button
            data-testid="forgot-pin-btn"
            onClick={() => onForgotPin()}
            className="text-primary text-sm font-medium z-10 relative"
            style={{ color: '#f59e0b' }}>
            Forgot PIN?
          </button>
        </div>
      )}
    </div>
  );
};

export default PinScreen;
