import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'medium' }) => {
  const spinnerSize = {
    small: '16px',
    medium: '24px',
    large: '32px'
  }[size];

  return (
    <div 
      className="spinner" 
      style={{ 
        width: spinnerSize,
        height: spinnerSize,
        borderWidth: size === 'small' ? '2px' : '3px'
      }}
    />
  );
};

export default LoadingSpinner;
