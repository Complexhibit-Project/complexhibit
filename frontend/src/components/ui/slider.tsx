'use client';

import React, { useRef, useEffect, useCallback } from 'react';

interface DateRangeSliderProps {
  min: number;
  max: number;
  onChange: (range: [number, number]) => void;
  className?: string;
}

export default function DateRangeSlider({ min, max, value, onChange, className = '' }: DateRangeSliderProps & { value: [number, number] }) {
  const [minVal, maxVal] = value;
  const range = useRef<HTMLDivElement>(null);

  // Convert to percentage
  const getPercent = useCallback(
    (val: number) => Math.round(((val - min) / (max - min)) * 100),
    [min, max]
  );

  // Update width and position
  useEffect(() => {
    const minPercent = getPercent(minVal);
    const maxPercent = getPercent(maxVal);

    if (range.current) {
      range.current.style.left = `${minPercent}%`;
      range.current.style.width = `${maxPercent - minPercent}%`;
    }
  }, [minVal, maxVal, getPercent]);

  return (
    <div className={`relative w-full h-12 flex items-center justify-center ${className}`}>
      <input
        type="range"
        min={min}
        max={max}
        value={minVal}
        onChange={(event) => {
          const newVal = Math.min(Number(event.target.value), maxVal - 1);
          onChange([newVal, maxVal]);
        }}
        className="thumb thumb--left z-30 w-full absolute pointer-events-none h-0 outline-none"
        style={{ zIndex: minVal > max - 100 ? 5 : undefined }}
      />
      <input
        type="range"
        min={min}
        max={max}
        value={maxVal}
        onChange={(event) => {
          const newVal = Math.max(Number(event.target.value), minVal + 1);
          onChange([minVal, newVal]);
        }}
        className="thumb thumb--right z-40 w-full absolute pointer-events-none h-0 outline-none"
      />

      <div className="relative w-full">
        {/* Track background */}
        <div className="absolute left-0 right-0 h-1.5 rounded-full bg-gray-200 z-10"></div>
        
        {/* Selected range */}
        <div ref={range} className="absolute h-1.5 rounded-full bg-indigo-600 z-20"></div>
        
        {/* Labels - merge when thumbs are close to prevent overlap */}
        {(() => {
          const minPercent = getPercent(minVal);
          const maxPercent = getPercent(maxVal);
          const distance = maxPercent - minPercent;
          const shouldMerge = distance < 12; // Merge labels if less than 12% apart
          
          if (shouldMerge) {
            const midPercent = (minPercent + maxPercent) / 2;
            return (
              <div 
                className="absolute top-4 text-xs text-gray-500 font-medium transform -translate-x-1/2 whitespace-nowrap"
                style={{ left: `${midPercent}%` }}
              >
                {minVal === maxVal ? minVal : `${minVal} – ${maxVal}`}
              </div>
            );
          }
          
          return (
            <>
              <div className="absolute top-4 text-xs text-gray-500 font-medium transform -translate-x-1/2" style={{ left: `${minPercent}%` }}>
                {minVal}
              </div>
              <div className="absolute top-4 text-xs text-gray-500 font-medium transform -translate-x-1/2" style={{ left: `${maxPercent}%` }}>
                {maxVal}
              </div>
            </>
          );
        })()}
      </div>

      <style jsx>{`
        input[type='range']::-webkit-slider-thumb {
          pointer-events: all;
          width: 18px;
          height: 18px;
          -webkit-appearance: none;
          background-color: white;
          border-radius: 50%;
          box-shadow: 0 0 0 1px #e5e7eb, 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          cursor: pointer;
          margin-top: -8px;
          transition: transform 0.15s cubic-bezier(0.25, 0.1, 0.25, 1), box-shadow 0.15s ease;
        }
        
        input[type='range']::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 0 0 1px #6366f1, 0 4px 6px -1px rgba(99, 102, 241, 0.3);
        }
        
        input[type='range']::-webkit-slider-thumb:active {
            transform: scale(0.95);
            background-color: #f9fafb;
        }

        input[type='range']::-moz-range-thumb {
          pointer-events: all;
          width: 18px;
          height: 18px;
          border: none;
          background-color: white;
          border-radius: 50%;
          box-shadow: 0 0 0 1px #e5e7eb, 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          cursor: pointer;
          transition: transform 0.15s cubic-bezier(0.25, 0.1, 0.25, 1);
        }
        
        input[type='range']::-moz-range-thumb:hover {
             transform: scale(1.1);
        }
      `}</style>
    </div>
  );
}
