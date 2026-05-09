interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Spinner = ({ size = 'md', className = '' }: SpinnerProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4',
  };

  return (
    <svg
      className={`${sizeClasses[size]} ${className} animate-spin text-blue-600 dark:text-blue-400`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// Full page loading overlay
Spinner.FullPage = ({ message = 'Loading...' }: { message?: string }) => (
  <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-4">
    <Spinner size="xl" />
    <p className="text-white text-lg font-medium">{message}</p>
  </div>
);

// Button loading state
Spinner.Button = ({ size = 'sm' }: { size?: 'sm' | 'md' | 'lg' | 'xl' }) => (
  <Spinner size={size} className="mr-2" />
);

export default Spinner;
