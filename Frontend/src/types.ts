export interface Stats {
  run: boolean;
  ser: boolean;
  cli: number;
  tot: number;
  i2r: number;
  r2i: number;
  act: number;
  start: number;
  port: string;
  baud: number;
  vport: number;
  log: Array<{ t: number; l: string; m: string }>;
}

export interface CommandResponse {
  ok: boolean;
  resp?: string;
  err?: string;
}

export interface PresetCommands {
  [key: string]: string;
}