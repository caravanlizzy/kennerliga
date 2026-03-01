import { computed } from 'vue';

export interface LeagueStyle {
  color: string;
  bg: string;
  text: string;
}

export function useLeagueColors() {
  const getLeagueColor = (league: number): string => {
    if (league <= 1) return 'amber-8'; // best
    if (league === 2) return 'blue-grey-5';
    if (league === 3) return 'brown-6';
    if (league === 4) return 'red-6';
    if (league <= 6) return 'deep-purple-6';
    if (league <= 10) return 'indigo-6';
    return 'grey-7';
  };

  const getLeagueBgColor = (league: number): string => {
    if (league <= 1) return 'amber-1';
    if (league === 2) return 'blue-grey-1';
    if (league === 3) return 'brown-1';
    if (league === 4) return 'red-1';
    if (league <= 6) return 'deep-purple-1';
    if (league <= 10) return 'indigo-1';
    return 'grey-2';
  };

  return {
    getLeagueColor,
    getLeagueBgColor
  };
}
