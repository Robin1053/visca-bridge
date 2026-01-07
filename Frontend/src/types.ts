export interface LogEntry {
  t: number;
  l: string;
  m: string;
}

export interface Stats {
  log: LogEntry[];
}

export interface VirtualPreset {
  name?: string;
  camera_preset: number;
  pan_speed?: number;
  tilt_speed?: number;
  zoom_speed?: number;
  focus?: "auto" | "manual";
}
