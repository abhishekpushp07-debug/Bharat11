/**
 * Phone Input Screen - Enter phone number
 */
import React, { useState, useRef, useEffect } from 'react';

const PhoneScreen = ({ onNext, onBack, initialPhone = '' }) => {
  const [phone, setPhone] = useState(initialPhone);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 10);
    setPhone(value);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (phone.length !== 10) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }
    
    onNext(phone);
  };

  const formatPhone = (num) => {
    if (num.length <= 5) return num;
    return `${num.slice(0, 5)} ${num.slice(5)}`;
  };

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col" data-testid="phone-screen">
      {/* Header */}
      <header className="flex items-center p-4 safe-top">
        <button 
          onClick={onBack}
          className="w-10 h-10 rounded-full bg-bg-card flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors"
          data-testid="back-btn"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 px-6 pt-8">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-text-primary mb-2">
            Enter your phone number
          </h1>
          <p className="text-text-secondary font-hindi">
            अपना मोबाइल नंबर दर्ज करें
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Phone Input */}
          <div className="mb-6">
            <div className={`flex items-center gap-3 p-4 bg-bg-secondary rounded-xl border-2 transition-colors ${
              error ? 'border-primary' : 'border-transparent focus-within:border-primary'
            }`}>
              {/* Country Code */}
              <div className="flex items-center gap-2 text-text-secondary">
                <span className="text-xl">🇮🇳</span>
                <span className="font-numbers text-lg">+91</span>
              </div>
              
              {/* Divider */}
              <div className="w-px h-8 bg-bg-elevated" />
              
              {/* Input */}
              <input
                ref={inputRef}
                type="tel"
                value={formatPhone(phone)}
                onChange={handlePhoneChange}
                placeholder="98765 43210"
                className="flex-1 bg-transparent text-text-primary font-numbers text-xl font-semibold outline-none placeholder:text-text-tertiary"
                maxLength={11}
                data-testid="phone-input"
              />
            </div>
            
            {error && (
              <p className="mt-2 text-primary text-sm" data-testid="phone-error">
                {error}
              </p>
            )}
          </div>

          {/* Info */}
          <div className="flex items-start gap-3 p-4 bg-bg-card rounded-xl mb-8">
            <svg className="w-5 h-5 text-info flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <p className="text-text-secondary text-sm font-hindi">
              आपका नंबर आपकी पहचान और लॉगिन के लिए उपयोग होगा। OTP की जरूरत नहीं है।
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={phone.length !== 10}
            className="btn btn-primary w-full py-4 text-lg"
            data-testid="continue-btn"
          >
            Continue
          </button>
        </form>
      </div>

      {/* Keypad hint */}
      <div className="py-6 text-center text-text-tertiary text-xs">
        <p>A secure 4-digit PIN will be your password</p>
      </div>
    </div>
  );
};

export default PhoneScreen;
