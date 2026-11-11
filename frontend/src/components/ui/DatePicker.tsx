"use client";

import React from 'react';
import ReactDatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { Calendar as CalendarIcon } from "lucide-react";

interface DatePickerProps {
  selected?: Date | null;
  onChange: (date: Date | null) => void;
  placeholder?: string;
  className?: string;
}

export default function DatePicker({ selected, onChange, placeholder, className }: DatePickerProps) {
  return (
    <div className="relative">
      <ReactDatePicker
        selected={selected}
        onChange={onChange}
        dateFormat="yyyy-MM-dd"
        placeholderText={placeholder || "Select date"}
        className={`w-full px-4 py-2 pl-10 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow ${className || ""}`}
        isClearable
        showYearDropdown
        scrollableYearDropdown
        yearDropdownItemNumber={100}
      />
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <CalendarIcon className="h-4 w-4 text-gray-400" />
      </div>
      <style jsx global>{`
        .react-datepicker-wrapper {
          display: block;
          width: 100%;
        }
        .react-datepicker__input-container {
          display: block;
        }
        .react-datepicker-popper {
          z-index: 50 !important;
        }
      `}</style>
    </div>
  );
}
