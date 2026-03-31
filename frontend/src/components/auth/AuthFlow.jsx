/**
 * Auth Flow Container
 * Manages the authentication flow: Welcome -> Phone -> PIN
 */
import React, { useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/api/client';
import WelcomeScreen from './WelcomeScreen';
import PhoneScreen from './PhoneScreen';
import PinScreen from './PinScreen';
import { COLORS } from '@/constants/design';
import { Lock, ArrowLeft, Loader2 } from 'lucide-react';

// ====== Forgot PIN Screen ======
function ForgotPinScreen({ phone, onBack, onSuccess }) {
  const [step, setStep] = useState(1); // 1=new, 2=confirm
  const [newPin, setNewPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNewPin = (pin) => {
    setNewPin(pin);
    setStep(2);
    setError('');
  };

  const handleConfirmPin = async (pin) => {
    setConfirmPin(pin);
    if (pin !== newPin) {
      setError('PIN match nahi kar raha. Dobara try karo.');
      setStep(1);
      setNewPin('');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await api.auth.forgotPin({ phone, new_pin: pin });
      if (res.data?.token?.access_token) {
        localStorage.setItem('crickpredict_token', res.data.token.access_token);
        localStorage.setItem('crickpredict_refresh_token', res.data.token.refresh_token);
      }
      onSuccess(res.data);
    } catch (e) {
      setError(e?.response?.data?.detail || 'PIN reset failed');
      setStep(1);
      setNewPin('');
    } finally { setLoading(false); }
  };

  return (
    <div data-testid="forgot-pin-screen" className="min-h-screen flex flex-col p-6" style={{ background: COLORS.background.primary }}>
      <button data-testid="forgot-pin-back" onClick={onBack} className="flex items-center gap-2 mb-6" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={18} /> Back
      </button>
      <div className="flex-1 flex flex-col items-center justify-center pb-20">
        <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4" style={{ background: `${COLORS.warning.main}20` }}>
          <Lock size={28} color={COLORS.warning.main} />
        </div>
        <h2 className="text-xl font-bold text-white mb-1">Reset PIN</h2>
        <p className="text-sm mb-6" style={{ color: COLORS.text.secondary }}>
          {step === 1 ? 'Naya 4-digit PIN enter karo' : 'PIN dobara confirm karo'}
        </p>
        <p className="text-xs mb-4" style={{ color: COLORS.text.tertiary }}>Phone: {phone}</p>

        {/* Step indicator */}
        <div className="flex gap-2 mb-6">
          {[1, 2].map(s => (
            <div key={s} className="h-1 rounded-full transition-all" style={{
              width: step >= s ? '28px' : '14px',
              background: step >= s ? COLORS.warning.main : COLORS.background.tertiary,
            }} />
          ))}
        </div>

        {/* PIN Dots */}
        <div className="flex gap-3 mb-4">
          {[0, 1, 2, 3].map(i => {
            const val = step === 1 ? newPin : confirmPin;
            return (
              <div key={i} className="w-12 h-14 rounded-xl flex items-center justify-center text-lg font-bold"
                style={{
                  background: COLORS.background.tertiary,
                  border: `2px solid ${val.length === i ? COLORS.warning.main : val.length > i ? COLORS.success.main : COLORS.border.light}`,
                  color: '#fff',
                }}>
                {val[i] ? '\u2022' : ''}
              </div>
            );
          })}
        </div>

        {/* Hidden input for mobile keyboard */}
        <input
          type="tel"
          inputMode="numeric"
          autoFocus
          value={step === 1 ? newPin : confirmPin}
          onChange={e => {
            const v = e.target.value.replace(/\D/g, '').slice(0, 4);
            if (step === 1) { setNewPin(v); if (v.length === 4) setTimeout(() => handleNewPin(v), 200); }
            else { setConfirmPin(v); if (v.length === 4) setTimeout(() => handleConfirmPin(v), 200); }
            setError('');
          }}
          className="opacity-0 absolute"
        />

        {error && <p className="text-xs text-center mt-2" style={{ color: COLORS.error.main }}>{error}</p>}
        {loading && <Loader2 size={24} className="animate-spin mt-4" color={COLORS.warning.main} />}
      </div>
    </div>
  );
}

const AuthFlow = () => {
  const [step, setStep] = useState('welcome'); // welcome, phone, pin-create, pin-confirm, pin-login, forgot-pin
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
    
    // Check if user exists
    try {
      const res = await api.auth.checkPhone(phoneNumber);
      if (res.data?.exists) {
        setIsExistingUser(true);
        setStep('pin-login');
      } else {
        setIsExistingUser(false);
        setStep('pin-create');
      }
    } catch (_) {
      // Fallback: assume new user
      setIsExistingUser(false);
      setStep('pin-create');
    }
  };

  const handlePinCreate = (pin) => {
    setCreatedPin(pin);
    setStep('pin-confirm');
    setError('');
  };

  const handlePinConfirm = async (pin) => {
    if (pin !== createdPin) {
      setError('PINs do not match. Please try again.');
      setCreatedPin('');
      setStep('pin-create');
      return;
    }

    setError('');
    
    // Register the user
    const result = await register(phone, pin);
    
    if (!result.success) {
      if (result.error?.toLowerCase().includes('already exists')) {
        // User exists, switch to login flow
        setIsExistingUser(true);
        setStep('pin-login');
        setError('Account exists. Please login with your PIN.');
        setCreatedPin('');
      } else {
        setError(result.error || 'Registration failed. Please try again.');
        setCreatedPin('');
        setStep('pin-create');
      }
    }
    // On success, authStore.isAuthenticated will be true and App will show HomeScreen
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
      case 'forgot-pin':
        setStep('pin-login');
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

  // Handle forgot PIN
  const handleForgotPin = () => {
    setStep('forgot-pin');
    setError('');
  };

  // Handle forgot PIN success
  const handleForgotPinSuccess = async (data) => {
    if (data?.token?.access_token) {
      // Auto login after PIN reset
      await login(phone, ''); // This won't work directly, use token
      // Set tokens manually and refresh
      window.location.reload();
    }
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
            onForgotPin={handleForgotPin}
          />
          {/* Option to register instead */}
          <div className="fixed bottom-3 left-0 right-0 text-center">
            <button 
              onClick={switchToRegister}
              className="text-text-secondary text-sm"
            >
              New user? <span className="text-primary font-medium">Create Account</span>
            </button>
          </div>
        </div>
      )}

      {step === 'forgot-pin' && (
        <ForgotPinScreen
          phone={phone}
          onBack={handleBack}
          onSuccess={handleForgotPinSuccess}
        />
      )}
    </div>
  );
};

export default AuthFlow;
