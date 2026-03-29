/**
 * Auth Flow Container
 * Manages the authentication flow: Welcome -> Phone -> PIN
 */
import React, { useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import WelcomeScreen from './WelcomeScreen';
import PhoneScreen from './PhoneScreen';
import PinScreen from './PinScreen';

const AuthFlow = () => {
  const [step, setStep] = useState('welcome'); // welcome, phone, pin-create, pin-confirm, pin-login
  const [phone, setPhone] = useState('');
  const [createdPin, setCreatedPin] = useState('');
  const [isExistingUser, setIsExistingUser] = useState(false);
  const [error, setError] = useState('');
  
  const { register, login, isLoading } = useAuthStore();

  const handleGetStarted = () => {
    setStep('phone');
  };

  const handlePhoneSubmit = async (phoneNumber) => {
    setPhone(phoneNumber);
    setError('');
    
    // For now, we'll try to determine if user exists by attempting login
    // In a real app, you might have a separate endpoint to check
    // For CrickPredict, we'll just go to PIN creation flow first
    // If they enter wrong PIN during login, they can register
    setStep('pin-create');
    setIsExistingUser(false);
  };

  const handlePinCreate = (pin) => {
    setCreatedPin(pin);
    setStep('pin-confirm');
    setError('');
  };

  const handlePinConfirm = async (pin) => {
    if (pin !== createdPin) {
      setError('PINs do not match. Please try again.');
      return;
    }

    setError('');
    
    // Register the user
    const result = await register(phone, pin);
    
    if (!result.success) {
      if (result.error?.includes('already exists')) {
        // User exists, switch to login flow
        setIsExistingUser(true);
        setStep('pin-login');
        setError('');
      } else {
        setError(result.error || 'Registration failed. Please try again.');
      }
    }
    // On success, authStore will update and App will redirect
  };

  const handlePinLogin = async (pin) => {
    setError('');
    
    const result = await login(phone, pin);
    
    if (!result.success) {
      setError(result.error || 'Invalid PIN. Please try again.');
    }
    // On success, authStore will update and App will redirect
  };

  const handleBack = () => {
    setError('');
    
    switch (step) {
      case 'phone':
        setStep('welcome');
        break;
      case 'pin-create':
        setStep('phone');
        break;
      case 'pin-confirm':
        setStep('pin-create');
        setCreatedPin('');
        break;
      case 'pin-login':
        setStep('phone');
        setIsExistingUser(false);
        break;
      default:
        setStep('welcome');
    }
  };

  // Switch to login mode
  const switchToLogin = () => {
    setIsExistingUser(true);
    setStep('pin-login');
    setError('');
  };

  // Switch to register mode
  const switchToRegister = () => {
    setIsExistingUser(false);
    setStep('pin-create');
    setError('');
  };

  return (
    <div data-testid="auth-flow">
      {step === 'welcome' && (
        <WelcomeScreen onGetStarted={handleGetStarted} />
      )}
      
      {step === 'phone' && (
        <PhoneScreen 
          onNext={handlePhoneSubmit}
          onBack={handleBack}
          initialPhone={phone}
        />
      )}
      
      {step === 'pin-create' && (
        <div>
          <PinScreen
            mode="create"
            phone={phone}
            onSubmit={handlePinCreate}
            onBack={handleBack}
            isLoading={isLoading}
            error={error}
          />
          {/* Option to login instead */}
          <div className="fixed bottom-6 left-0 right-0 text-center">
            <button 
              onClick={switchToLogin}
              className="text-text-secondary text-sm"
            >
              Already have an account? <span className="text-primary font-medium">Login</span>
            </button>
          </div>
        </div>
      )}
      
      {step === 'pin-confirm' && (
        <PinScreen
          mode="confirm"
          phone={phone}
          onSubmit={handlePinConfirm}
          onBack={handleBack}
          isLoading={isLoading}
          error={error}
        />
      )}
      
      {step === 'pin-login' && (
        <div>
          <PinScreen
            mode="login"
            phone={phone}
            onSubmit={handlePinLogin}
            onBack={handleBack}
            isLoading={isLoading}
            error={error}
          />
          {/* Option to register instead */}
          <div className="fixed bottom-6 left-0 right-0 text-center">
            <button 
              onClick={switchToRegister}
              className="text-text-secondary text-sm"
            >
              New user? <span className="text-primary font-medium">Create Account</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuthFlow;
