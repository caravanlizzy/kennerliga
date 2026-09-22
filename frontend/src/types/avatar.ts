export type AvatarShape =
  | 'squircle'
  | 'circle'
  | 'heart'
  | 'star'
  | 'hexagon'
  | 'shield'
  | 'clover'
  | 'meeple'
  | 'beetle'
  | 'fish'
  | 'snake'
  | 'crown'
  | 'cat';

export interface AvatarShapeOption {
  id: AvatarShape;
  name: string;
  description: string;
  icon?: string;
}

export const AVATAR_SHAPE_OPTIONS: AvatarShapeOption[] = [
  {
    id: 'squircle',
    name: 'Squircle',
    description: 'Smooth rounded square with modern curvature',
    icon: 'crop_square',
  },
  {
    id: 'circle',
    name: 'Circle',
    description: 'Classic balanced circle',
    icon: 'lens',
  },
  {
    id: 'heart',
    name: 'Heart',
    description: 'Playful and warm heart shape',
    icon: 'favorite',
  },
  {
    id: 'star',
    name: 'Star',
    description: 'Five-pointed shining star',
    icon: 'star',
  },
  {
    id: 'hexagon',
    name: 'Hexagon',
    description: 'Board game style hex tile',
    icon: 'hexagon',
  },
  {
    id: 'shield',
    name: 'Shield',
    description: 'Tournament champion crest',
    icon: 'shield',
  },
  {
    id: 'clover',
    name: 'Clover',
    description: 'Lucky four-leaf clover',
    icon: 'nature',
  },
  {
    id: 'meeple',
    name: 'Meeple',
    description: 'Classic board game player figure',
    icon: 'accessibility_new',
  },
  {
    id: 'beetle',
    name: 'Beetle',
    description: 'Resilient scarab beetle silhouette',
    icon: 'bug_report',
  },
  {
    id: 'fish',
    name: 'Fish',
    description: 'Graceful swimming fish silhouette',
    icon: 'phishing',
  },
  {
    id: 'snake',
    name: 'Snake',
    description: 'Winding serpentine serpent coil',
    icon: 'gesture',
  },
  {
    id: 'crown',
    name: 'Crown',
    description: 'Three-pointed royal winner crown',
    icon: 'emoji_events',
  },
  {
    id: 'cat',
    name: 'Cat',
    description: 'Playful feline head with pointy ears',
    icon: 'pets',
  },
];

export interface AvatarColorOption {
  hex: string;
  name: string;
}

export const AVATAR_COLOR_OPTIONS: AvatarColorOption[] = [
  { hex: '', name: 'Auto (Hash)' },
  { hex: '#dc2626', name: 'Ruby Red' },
  { hex: '#e11d48', name: 'Rose' },
  { hex: '#f43f5e', name: 'Coral Pink' },
  { hex: '#f05924', name: 'Flame' },
  { hex: '#f97316', name: 'Amber' },
  { hex: '#f59e0b', name: 'Gold' },
  { hex: '#eab308', name: 'Sun Yellow' },
  { hex: '#84cc16', name: 'Lime' },
  { hex: '#10b981', name: 'Emerald' },
  { hex: '#059669', name: 'Forest' },
  { hex: '#14b8a6', name: 'Teal' },
  { hex: '#06b6d4', name: 'Cyan' },
  { hex: '#0ea5e9', name: 'Sky Blue' },
  { hex: '#2563eb', name: 'Royal Blue' },
  { hex: '#4f46e5', name: 'Indigo' },
  { hex: '#7c3aed', name: 'Violet' },
  { hex: '#9333ea', name: 'Purple' },
  { hex: '#c026d3', name: 'Fuchsia' },
  { hex: '#db2777', name: 'Magenta' },
  { hex: '#475569', name: 'Slate Gray' },
  { hex: '#1e293b', name: 'Midnight' },
];

export function getContrastTextColor(hexColor: string): string {
  if (!hexColor || !hexColor.startsWith('#')) return '#ffffff';
  let hex = hexColor.slice(1);
  if (hex.length === 3) {
    hex = hex
      .split('')
      .map((c) => c + c)
      .join('');
  }
  const r = parseInt(hex.substring(0, 2), 16) || 0;
  const g = parseInt(hex.substring(2, 4), 16) || 0;
  const b = parseInt(hex.substring(4, 6), 16) || 0;
  const yiq = (r * 299 + g * 587 + b * 114) / 1000;
  return yiq >= 160 ? '#1f2937' : '#ffffff';
}
