type choice = {
  id: number,
  value: string,
}

export type TGameOption = {
  id: number;
  title: string;
  isBoolean: boolean;
  choices: choice[];
}
