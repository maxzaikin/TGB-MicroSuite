// file: src/shared/hooks/useDebounce.ts

import { useState, useEffect } from 'react';

/**
 * A custom hook to debounce a value. It delays updating the hook's output
 * until a certain amount of time has passed without the input value changing.
 * This is extremely useful for performance optimization, especially for features
 * like auto-saving or live search fields that trigger API calls.
 *
 * @template T The type of the value to be debounced.
 * @param {T} value The value from your component's state that you want to debounce (e.g., a search term).
 * @param {number} delay The debounce delay in milliseconds (e.g., 500).
 * @returns {T} The debounced value, which updates only after the delay.
 */
export function useDebounce<T>(value: T, delay: number): T {
  // State to store the debounced value. This is what the hook will return.
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(
    () => {
      // Set up a timer. This function will run after the 'delay' time has passed.
      const handler = setTimeout(() => {
        // Once the timer completes, update the debounced value with the latest input value.
        setDebouncedValue(value);
      }, delay);

      // This is the crucial cleanup function.
      // It runs every time the `value` or `delay` changes, OR when the component unmounts.
      // Its job is to cancel the previously set timer before a new one is set.
      return () => {
        clearTimeout(handler);
      };
    },
    // The effect will re-run whenever the input `value` or `delay` changes.
    [value, delay]
  );

  // Return the debounced value to the component that uses this hook.
  return debouncedValue;
}