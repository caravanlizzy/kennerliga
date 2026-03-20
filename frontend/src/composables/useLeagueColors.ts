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
    if (league === 2) return 'blue-grey-2';
    if (league === 3) return 'brown-1';
    if (league === 4) return 'red-2';
    if (league <= 6) return 'deep-purple-1';
    if (league <= 10) return 'indigo-1';
    return 'grey-2';
  };

  const getHexLeagueColor = (league: number): string => {
    if (league <= 1) return '#ffb300'; // amber-8
    if (league === 2) return '#607d8b'; // blue-grey-5
    if (league === 3) return '#6d4c41'; // brown-6
    if (league === 4) return '#e53935'; // red-6
    if (league <= 6) return '#5e35b1'; // deep-purple-6
    if (league <= 10) return '#3949ab'; // indigo-6
    return '#616161'; // grey-7
  };

  return {
    getLeagueColor,
    getLeagueBgColor,
    getHexLeagueColor
  };
}
