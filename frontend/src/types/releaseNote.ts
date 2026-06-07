export type TReleaseNoteDto = {
  id: number;
  title: string;
  text: string;
  created_at: string;
  updated_at: string;
};

export type ReleaseNoteCreate = {
  title: string;
  text: string;
};
