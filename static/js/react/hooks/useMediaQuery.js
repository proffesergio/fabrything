/**
 * useMediaQuery Hook
 * 
 * Simple hook for responsive component rendering.
 * Returns true if media query matches.
 * 
 * Usage:
 *   const isMobile = useMediaQuery('(max-width: 768px)');
 */

import { useEffect, useState } from 'react';

const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handler = (e) => setMatches(e.matches);
    mediaQuery.addListener(handler);

    return () => mediaQuery.removeListener(handler);
  }, [query]);

  return matches;
};

export default useMediaQuery;