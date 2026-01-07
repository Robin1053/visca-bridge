import React, { useState } from "react";
import {
  Box, Tabs, Tab, Card, CardContent, Typography, Button,
  TextField, Snackbar, Alert, List, ListItem, ListItemText, CardHeader, Paper
} from "@mui/material";

import Grid from "@mui/material/GridLegacy";
import {
  Send, PowerSettingsNew, Refresh, ZoomIn, ZoomOut, Stop, ArrowUpward,
  ArrowDownward, ArrowBack, ArrowForward, Home
} from "@mui/icons-material";

interface LogEntry {
  t: number;
  l: string;
  m: string;
}

interface Stats {
  log: LogEntry[];
}

const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<number>(0);
  const [hexCommand, setHexCommand] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<null | { ok: boolean; err?: any }>(null);
  const [stats, setStats] = useState<Stats>({ log: [] });

  // Advanced Preset State
  const [presetId, setPresetId] = useState<number>(1);
  const [panSpeed, setPanSpeed] = useState<number>(6);
  const [tiltSpeed, setTiltSpeed] = useState<number>(6);
  const [zoomSpeed, setZoomSpeed] = useState<number>(0);
  const [focus, setFocus] = useState<"auto" | "manual">("auto");

  const sendCommand = async () => {
    if (!hexCommand.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("/preset/advanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ camera_preset: presetId, pan_speed: panSpeed, tilt_speed: tiltSpeed, zoom_speed: zoomSpeed, focus })
      });
      setResponse({ ok: res.ok });
      setStats(prev => ({
        log: [...prev.log, { t: Date.now() / 1000, l: "CMD", m: hexCommand }]
      }));
      setHexCommand("");
    } catch (err) {
      setResponse({ ok: false, err });
    } finally {
      setLoading(false);
    }
  };

  const handlePresetClick = (cmd: string) => {
    setHexCommand(cmd);
    sendCommand();
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} variant="scrollable">
          <Tab label="Manual" />
          <Tab label="Power" />
          <Tab label="Zoom" />
          <Tab label="Focus" />
          <Tab label="Pan/Tilt" />
          <Tab label="Presets" />
          <Tab label="Picture" />
        </Tabs>
      </Box>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          {/* Manual Tab */}
          {currentTab === 0 && (
            <Box>
              <TextField
                fullWidth
                label="VISCA Hex Command"
                placeholder="z.B. 81 01 04 07 02 FF"
                value={hexCommand}
                onChange={(e) => setHexCommand(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendCommand()}
                sx={{ mb: 2 }}
                inputProps={{ style: { fontFamily: 'monospace' } }}
              />
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={() => sendCommand()}
                disabled={!hexCommand.trim() || loading}
              >
                {loading ? 'Sending...' : 'Send Command'}
              </Button>
            </Box>
          )}

          {/* Power Tab */}
          {currentTab === 1 && (
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Button fullWidth variant="contained" color="success" startIcon={<PowerSettingsNew />}
                  onClick={() => handlePresetClick('power_on')}>Power ON</Button>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Button fullWidth variant="contained" color="error" startIcon={<PowerSettingsNew />}
                  onClick={() => handlePresetClick('power_off')}>Power OFF</Button>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Button fullWidth variant="outlined" startIcon={<Refresh />}
                  onClick={() => handlePresetClick('power_query')}>Query</Button>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Button fullWidth variant="outlined"
                  onClick={() => handlePresetClick('if_clear')}>IF Clear</Button>
              </Grid>
            </Grid>
          )}

          {/* Zoom */}
          {currentTab === 2 && (
            <Grid container spacing={2}>
              <Grid xs={6} sm={4}>
                <Button fullWidth variant="contained" startIcon={<ZoomIn />}
                  onClick={() => handlePresetClick('zoom_tele')}>Tele</Button>
              </Grid>
              <Grid xs={6} sm={4}>
                <Button fullWidth variant="contained" startIcon={<ZoomOut />}
                  onClick={() => handlePresetClick('zoom_wide')}>Wide</Button>
              </Grid>
              <Grid xs={6} sm={4}>
                <Button fullWidth variant="contained" color="error" startIcon={<Stop />}
                  onClick={() => handlePresetClick('zoom_stop')}>Stop</Button>
              </Grid>
              <Grid xs={6} sm={4}>
                <Button fullWidth variant="outlined" startIcon={<ZoomIn />}
                  onClick={() => handlePresetClick('zoom_tele_fast')}>Tele Fast</Button>
              </Grid>
              <Grid xs={6} sm={4}>
                <Button fullWidth variant="outlined" startIcon={<ZoomOut />}
                  onClick={() => handlePresetClick('zoom_wide_fast')}>Wide Fast</Button>
              </Grid>
            </Grid>
          )}

          {/* Focus */}
          {currentTab === 3 && (
            <Grid container spacing={2}>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="contained" color="success"
                  onClick={() => handlePresetClick('focus_auto')}>Auto Focus</Button>
              </Grid>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="contained"
                  onClick={() => handlePresetClick('focus_manual')}>Manual</Button>
              </Grid>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="outlined"
                  onClick={() => handlePresetClick('focus_far')}>Far</Button>
              </Grid>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="outlined"
                  onClick={() => handlePresetClick('focus_near')}>Near</Button>
              </Grid>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="outlined" color="error" startIcon={<Stop />}
                  onClick={() => handlePresetClick('focus_stop')}>Stop</Button>
              </Grid>
              <Grid xs={6} sm={3}>
                <Button fullWidth variant="outlined"
                  onClick={() => handlePresetClick('focus_onepush')}>One Push</Button>
              </Grid>
            </Grid>
          )}

          {/* Pan/Tilt */}
          {currentTab === 4 && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid xs={4}></Grid>
                <Grid xs={4}>
                  <Button fullWidth variant="contained" startIcon={<ArrowUpward />}
                    onClick={() => handlePresetClick('pt_up')}>Up</Button>
                </Grid>
                <Grid xs={4}></Grid>
                <Grid xs={4}>
                  <Button fullWidth variant="contained" startIcon={<ArrowBack />}
                    onClick={() => handlePresetClick('pt_left')}>Left</Button>
                </Grid>
                <Grid xs={4}>
                  <Button fullWidth variant="contained" color="error" startIcon={<Stop />}
                    onClick={() => handlePresetClick('pt_stop')}>Stop</Button>
                </Grid>
                <Grid xs={4}>
                  <Button fullWidth variant="contained" startIcon={<ArrowForward />}
                    onClick={() => handlePresetClick('pt_right')}>Right</Button>
                </Grid>
                <Grid xs={4}></Grid>
                <Grid xs={4}>
                  <Button fullWidth variant="contained" startIcon={<ArrowDownward />}
                    onClick={() => handlePresetClick('pt_down')}>Down</Button>
                </Grid>
                <Grid xs={4}></Grid>
              </Grid>
              <Grid container spacing={2}>
                <Grid xs={6}>
                  <Button fullWidth variant="outlined" startIcon={<Home />}
                    onClick={() => handlePresetClick('pt_home')}>Home</Button>
                </Grid>
                <Grid xs={6}>
                  <Button fullWidth variant="outlined" startIcon={<Refresh />}
                    onClick={() => handlePresetClick('pt_reset')}>Reset</Button>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Presets */}
          {currentTab === 5 && (
            <Box>
              <Typography variant="h6" gutterBottom>Recall Preset</Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                  <Grid xs={6} sm={3} key={`rec-${i}`}>
                    <Button fullWidth variant="contained"
                      onClick={() => handlePresetClick(`preset_recall_${i}`)}>
                      Preset {i}
                    </Button>
                  </Grid>
                ))}
              </Grid>
              <Typography variant="h6" gutterBottom>Save Preset</Typography>
              <Grid container spacing={2}>
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                  <Grid xs={6} sm={3} key={`sav-${i}`}>
                    <Button fullWidth variant="outlined"
                      onClick={() => handlePresetClick(`preset_set_${i}`)}>
                      Save {i}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Picture */}
          {currentTab === 6 && (
            <Box>
              <Typography variant="h6" gutterBottom>White Balance</Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid xs={6} sm={3}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('wb_auto')}>Auto</Button>
                </Grid>
                <Grid xs={6} sm={3}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('wb_indoor')}>Indoor</Button>
                </Grid>
                <Grid xs={6} sm={3}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('wb_outdoor')}>Outdoor</Button>
                </Grid>
                <Grid xs={6} sm={3}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('wb_manual')}>Manual</Button>
                </Grid>
              </Grid>
              <Typography variant="h6" gutterBottom>Effects</Typography>
              <Grid container spacing={2}>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('backlight_on')}>Backlight ON</Button>
                </Grid>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('backlight_off')}>Backlight OFF</Button>
                </Grid>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('mirror_on')}>Mirror ON</Button>
                </Grid>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('mirror_off')}>Mirror OFF</Button>
                </Grid>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('flip_on')}>Flip ON</Button>
                </Grid>
                <Grid xs={6} sm={4}>
                  <Button fullWidth variant="outlined"
                    onClick={() => handlePresetClick('flip_off')}>Flip OFF</Button>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Event Log */}
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Event Log" />
        <CardContent>
          <Paper sx={{ maxHeight: 400, overflow: 'auto', bgcolor: 'background.default', p: 1 }}>
            <List dense>
              {stats.log.length > 0 ? (
                stats.log.map((entry, idx) => (
                  <ListItem key={idx} disableGutters>
                    <ListItemText
                      primaryTypographyProps={{ fontFamily: 'monospace', fontSize: 12 }}
                      primary={`${new Date(entry.t * 1000).toLocaleTimeString('de-DE')} [${entry.l}] ${entry.m}`}
                    />
                  </ListItem>
                ))
              ) : (
                <ListItem disableGutters>
                  <ListItemText
                    primary="No log entries yet"
                    secondary="Waiting for events..."
                  />
                </ListItem>
              )}
            </List>
          </Paper>
        </CardContent>
      </Card>

      {/* Snackbar Feedback */}
      <Snackbar open={!!response} autoHideDuration={2000} onClose={() => setResponse(null)}>
        <Alert severity={response?.ok ? 'success' : 'error'} sx={{ width: '100%' }}>
          {response?.ok ? 'Command sent!' : 'Error sending command'}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
