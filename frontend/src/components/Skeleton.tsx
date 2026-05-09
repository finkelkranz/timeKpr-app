import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
}

const Skeleton = ({
  className = '',
  variant = 'rectangular',
  width,
  height
}: SkeletonProps) => {
  const baseClasses = 'bg-gray-200 dark:bg-gray-700 animate-pulse';

  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'rounded-md h-4';
      case 'circular':
        return 'rounded-full aspect-square';
      case 'rounded':
        return 'rounded-lg';
      case 'rectangular':
      default:
        return 'rounded-none';
    }
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`${baseClasses} ${getVariantClasses()} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
};

// User card skeleton
Skeleton.UserCard = () => (
  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md animate-pulse">
    <div className="p-4">
      <div className="flex items-center gap-3">
        <Skeleton variant="circular" className="w-10 h-10" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" className="w-3/4" />
          <Skeleton variant="text" className="w-1/2" />
        </div>
      </div>
    </div>
    <div className="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 space-y-2">
      <Skeleton variant="text" className="w-full h-2" />
      <Skeleton variant="text" className="w-full h-2" />
      <Skeleton variant="text" className="w-full h-2" />
    </div>
  </div>
);

// Stats card skeleton
Skeleton.StatsCard = () => (
  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 animate-pulse">
    <Skeleton variant="text" className="w-1/3 mb-2" />
    <div className="h-48 flex items-center justify-center">
      <Skeleton className="w-3/4 h-32" />
    </div>
  </div>
);

// Grid skeleton for multiple loading items
Skeleton.UserGrid = ({ count = 4 }: { count?: number }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {Array.from({ length: count }).map((_, i) => (
      <Skeleton.UserCard key={i} />
    ))}
  </div>
);

export default Skeleton;
