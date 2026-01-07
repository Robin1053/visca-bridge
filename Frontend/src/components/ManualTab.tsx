import React, { useState } from "react";
import { Box, TextField, Button } from "@mui/material";
import { Send } from "@mui/icons-material";

const ManualTab: React.FC = () => {
  const [hexCommand, setHexCommand] = useState("");
  const [loading, setLoading] = useState(false);

  const sendCommand = async () => {
    if (!hexCommand.trim()) return;
    setLoading(true);
    try {
      await fetch("/preset/advanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          camera_preset: 1,
          pan_speed: 6,
          tilt_speed: 6,
          zoom_speed: 0,
          focus: "auto"
        })
      });
      setHexCommand("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <TextField
        fullWidth
        label="VISCA Hex Command"
        placeholder="z.B. 81 01 04 07 02 FF"
        value={hexCommand}
        onChange={(e) => setHexCommand(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && sendCommand()}
        sx={{ mb: 2 }}
        inputProps={{ style: { fontFamily: "monospace" } }}
      />
      <Button
        variant="contained"
        startIcon={<Send />}
        onClick={sendCommand}
        disabled={!hexCommand.trim() || loading}
      >
        {loading ? "Sending..." : "Send Command"}
      </Button>
    </Box>
  );
};

export default ManualTab;
