import React, { useState } from "react";
import { Box, TextField, Slider, FormControl, InputLabel, Select, MenuItem, Button } from "@mui/material";

const AdvancedPresetControl: React.FC = () => {
  const [presetId, setPresetId] = useState(1);
  const [panSpeed, setPanSpeed] = useState(6);
  const [tiltSpeed, setTiltSpeed] = useState(6);
  const [zoomSpeed, setZoomSpeed] = useState(0);
  const [focus, setFocus] = useState<"auto" | "manual">("auto");

  const sendAdvancedPreset = async () => {
    try {
      await fetch("/preset/advanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ camera_preset: presetId, pan_speed: panSpeed, tilt_speed: tiltSpeed, zoom_speed: zoomSpeed, focus })
      });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <TextField
        label="Preset ID" type="number" fullWidth inputProps={{ min: 1, max: 16 }}
        value={presetId} onChange={(e) => setPresetId(+e.target.value)} sx={{ mb: 2 }}
      />
      <Slider value={panSpeed} min={1} max={24} onChange={(_, v) => setPanSpeed(v as number)} valueLabelDisplay="auto" />
      <Slider value={tiltSpeed} min={1} max={24} onChange={(_, v) => setTiltSpeed(v as number)} valueLabelDisplay="auto" />
      <TextField label="Zoom Speed" type="number" fullWidth inputProps={{ min: 0, max: 7 }} value={zoomSpeed} onChange={e => setZoomSpeed(+e.target.value)} sx={{ mt: 2 }} />
      <FormControl fullWidth sx={{ mt: 2 }}>
        <InputLabel>Focus</InputLabel>
        <Select value={focus} onChange={e => setFocus(e.target.value as "auto" | "manual")}>
          <MenuItem value="auto">Auto</MenuItem>
          <MenuItem value="manual">Manual</MenuItem>
        </Select>
      </FormControl>
      <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={sendAdvancedPreset}>Send Advanced Preset</Button>
    </Box>
  );
};

export default AdvancedPresetControl;
