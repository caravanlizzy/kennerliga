export enum AnnouncementType {
  INFO = 'INFO',
  WINNER = 'WINNER',
  REGISTER = 'REGISTER',
  WARNING = 'WARNING',
  NEUTRAL = 'NEUTRAL',
}

export interface Announcement {
  id: number;
  type: AnnouncementType;
  title: string;
  content: string | null;
  visible_until: string;
  visible_from: string;
}

export interface AnnouncementCreate {
  type: AnnouncementType;
  title: string;
  content?: string | null;
  visible_until: string;
  visible_from: string;
}
