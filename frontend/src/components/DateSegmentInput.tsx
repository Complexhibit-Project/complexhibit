"use client";

interface DateSegmentInputProps {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

export default function DateSegmentInput({
  placeholder,
  value,
  onChange
}: DateSegmentInputProps) {
  const parts = value.split('-');
  const year = parts[0] || '';
  const month = parts[1] || '';
  const day = parts[2] || '';

  const handleYearChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newYear = e.target.value;
    const combined = newYear + (month ? `-${month}` : '') + (day ? `-${day}` : '');
    onChange(combined);
  };

  const handleMonthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newMonth = e.target.value;
    if (newMonth && !year) return; // Don't allow month without year
    const combined = year + (newMonth ? `-${newMonth}` : '') + (day && newMonth ? `-${day}` : '');
    onChange(combined);
  };

  const handleDayChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDay = e.target.value;
    if (newDay && (!year || !month)) return; // Don't allow day without year and month
    const combined = year + (month ? `-${month}` : '') + (newDay ? `-${newDay}` : '');
    onChange(combined);
  };

  const baseClasses = "w-14 px-2 py-2 border border-gray-200 rounded text-sm text-center focus:ring-1 focus:ring-indigo-500 outline-none";

  return (
    <div className="flex items-center gap-2">
      <input
        type="number"
        min="1800"
        max="2100"
        placeholder="YYYY"
        value={year}
        onChange={handleYearChange}
        className={`${baseClasses} w-20`}
      />
      <span className="text-gray-400">/</span>
      <input
        type="number"
        min="1"
        max="12"
        placeholder="MM"
        value={month}
        onChange={handleMonthChange}
        disabled={!year}
        className={`${baseClasses} ${!year ? 'bg-gray-100 cursor-not-allowed' : ''}`}
      />
      <span className="text-gray-400">/</span>
      <input
        type="number"
        min="1"
        max="31"
        placeholder="DD"
        value={day}
        onChange={handleDayChange}
        disabled={!year || !month}
        className={`${baseClasses} ${(!year || !month) ? 'bg-gray-100 cursor-not-allowed' : ''}`}
      />
    </div>
  );
}
