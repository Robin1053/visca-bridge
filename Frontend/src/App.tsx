import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  TextField,
  Chip,
  Box,
  Paper,
  Tabs,
  Tab,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  Stack
} from '@mui/material';
import {
  PowerSettingsNew,
  ZoomIn,
  ZoomOut,
  CameraAlt,
  Send,
  Refresh,
  FiberManualRecord,
  Circle,
  ArrowUpward,
  ArrowDownward,
  ArrowBack,
  ArrowForward,
  Home,
  Stop
} from '@mui/icons-material';
import { type Stats, type PresetCommands, type CommandResponse } from './types';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#4caf50' },
    secondary: { main: '#2196f3' },
    background: { default: '#0a0a0a', paper: '#1a1a1a' },
  },
});

export const App = () => {
  const [stats, setStats] = useState<Stats>({
    run: false, ser: false, cli: 0, tot: 0, i2r: 0, r2i: 0,
    act: 0, start: 0, port: '', baud: 0, vport: 0, log: []
  });

  const [presets, setPresets] = useState<PresetCommands>({});
  const [hexCommand, setHexCommand] = useState<string>('');
  const [response, setResponse] = useState<CommandResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentTab, setCurrentTab] = useState<number>(0);

  // API URL - Raspberry Pi IP eintragen!
  const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.1.100:8080';

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`);
      if (res.ok) setStats(await res.json());
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  const fetchPresets = async () => {
    try {
      const res = await fetch(`${API_URL}/api/presets`);
      if (res.ok) setPresets(await res.json());
    } catch (err) {
      console.error('Presets error:', err);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchPresets();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const sendCommand = async (cmd?: string) => {
    const command = cmd || hexCommand;
    if (!command.trim()) return;

    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch(`${API_URL}/api/cmd`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hex: command })
      });
      const data: CommandResponse = await res.json();
      setResponse(data);
      setTimeout(() => setResponse(null), 5000);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      setResponse({ ok: false, err: 'Network error' });
    } finally {
      setLoading(false);
    }
  };

  const handlePresetClick = (key: string) => {
    if (presets[key]) {
      setHexCommand(presets[key]);
      sendCommand(presets[key]);
    }
  };

  const formatTime = (ts: number) => new Date(ts * 1000).toLocaleTimeString('de-DE');
  const formatDateTime = (ts: number) => new Date(ts * 1000).toLocaleString('de-DE');

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
        <AppBar position="static" color="transparent" elevation={2}>
          <Toolbar>
            <CameraAlt sx={{ mr: 2 }} />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              VISCA Bridge - CV620 Control
            </Typography>
            <Chip
              icon={<FiberManualRecord />}
              label={stats.run ? 'Running' : 'Stopped'}
              color={stats.run ? 'success' : 'error'}
              sx={{ mr: 1 }}
            />
            <Chip
              icon={<Circle />}
              label={`${stats.cli} Clients`}
              color="primary"
              variant="outlined"
            />
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
          {/* Status Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2">Bridge Status</Typography>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <Circle color={stats.run ? 'success' : 'error'} />
                    <Typography variant="h6">{stats.run ? 'Running' : 'Stopped'}</Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2">Serial Port</Typography>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <Circle color={stats.ser ? 'success' : 'error'} />
                    <Typography variant="h6">{stats.port || '-'}</Typography>
                  </Stack>
                  <Typography variant="caption">{stats.baud ? `${stats.baud} baud` : ''}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2">Total Connections</Typography>
                  <Typography variant="h4" color="primary">{stats.tot}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2">VISCA Port</Typography>
                  <Typography variant="h4" color="secondary">{stats.vport || '-'}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Statistics */}
          <Card sx={{ mb: 3 }}>
            <CardHeader title="Statistics" />
            <CardContent>
              <Grid container spacing={3}>
                <Grid size={{ xs: 6, md: 3 }}>
                  <Typography variant="body2" color="text.secondary">Started</Typography>
                  <Typography variant="body1">{formatDateTime(stats.start)}</Typography>
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                  <Typography variant="body2" color="text.secondary">IP → RS232</Typography>
                  <Typography variant="h5" color="success.main">{stats.i2r}</Typography>
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                  <Typography variant="body2" color="text.secondary">RS232 → IP</Typography>
                  <Typography variant="h5" color="secondary.main">{stats.r2i}</Typography>
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                  <Typography variant="body2" color="text.secondary">Last Activity</Typography>
                  <Typography variant="body1">{stats.act ? formatDateTime(stats.act) : 'None'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Control Tabs */}
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} variant="scrollable">
                <Tab label="Manual" />
                <Tab label="Power" />
                <Tab label="Zoom" />
                <Tab label="Focus" />
                <Tab label="Pan/Tilt" />
                <Tab label="Presets" />
                <Tab label="Picture" />
              </Tabs>
            </Box>

            <CardContent>
              {/* Manual Tab */}
              {currentTab === 0 && (
                <Box>
                  <TextField
                    fullWidth
                    label="VISCA Hex Command"
                    placeholder="e.g. 81 01 04 07 02 FF"
                    value={hexCommand}
                    onChange={(e) => setHexCommand(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendCommand()}
                    sx={{ mb: 2 }}
                    slotProps={{ input: { style: { fontFamily: 'monospace' } } }}
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
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="contained" color="success" startIcon={<PowerSettingsNew />}
                      onClick={() => handlePresetClick('power_on')}>Power ON</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="contained" color="error" startIcon={<PowerSettingsNew />}
                      onClick={() => handlePresetClick('power_off')}>Power OFF</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined" startIcon={<Refresh />}
                      onClick={() => handlePresetClick('power_query')}>Query</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined"
                      onClick={() => handlePresetClick('if_clear')}>IF Clear</Button>
                  </Grid>
                </Grid>
              )}

              {/* Zoom Tab */}
              {currentTab === 2 && (
                <Grid container spacing={2}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Button fullWidth variant="contained" startIcon={<ZoomIn />}
                      onClick={() => handlePresetClick('zoom_tele')}>Tele</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Button fullWidth variant="contained" startIcon={<ZoomOut />}
                      onClick={() => handlePresetClick('zoom_wide')}>Wide</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Button fullWidth variant="contained" color="error" startIcon={<Stop />}
                      onClick={() => handlePresetClick('zoom_stop')}>Stop</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Button fullWidth variant="outlined" startIcon={<ZoomIn />}
                      onClick={() => handlePresetClick('zoom_tele_fast')}>Tele Fast</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Button fullWidth variant="outlined" startIcon={<ZoomOut />}
                      onClick={() => handlePresetClick('zoom_wide_fast')}>Wide Fast</Button>
                  </Grid>
                </Grid>
              )}

              {/* Focus Tab */}
              {currentTab === 3 && (
                <Grid container spacing={2}>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="contained" color="success"
                      onClick={() => handlePresetClick('focus_auto')}>Auto Focus</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="contained"
                      onClick={() => handlePresetClick('focus_manual')}>Manual</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined"
                      onClick={() => handlePresetClick('focus_far')}>Far</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined"
                      onClick={() => handlePresetClick('focus_near')}>Near</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined" color="error" startIcon={<Stop />}
                      onClick={() => handlePresetClick('focus_stop')}>Stop</Button>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Button fullWidth variant="outlined"
                      onClick={() => handlePresetClick('focus_onepush')}>One Push</Button>
                  </Grid>
                </Grid>
              )}

              {/* Pan/Tilt Tab */}
              {currentTab === 4 && (
                <Box>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid size={4}></Grid>
                    <Grid size={4}>
                      <Button fullWidth variant="contained" startIcon={<ArrowUpward />}
                        onClick={() => handlePresetClick('pt_up')}>Up</Button>
                    </Grid>
                    <Grid size={4}></Grid>
                    <Grid size={4}>
                      <Button fullWidth variant="contained" startIcon={<ArrowBack />}
                        onClick={() => handlePresetClick('pt_left')}>Left</Button>
                    </Grid>
                    <Grid size={4}>
                      <Button fullWidth variant="contained" color="error" startIcon={<Stop />}
                        onClick={() => handlePresetClick('pt_stop')}>Stop</Button>
                    </Grid>
                    <Grid size={4}>
                      <Button fullWidth variant="contained" startIcon={<ArrowForward />}
                        onClick={() => handlePresetClick('pt_right')}>Right</Button>
                    </Grid>
                    <Grid size={4}></Grid>
                    <Grid size={4}>
                      <Button fullWidth variant="contained" startIcon={<ArrowDownward />}
                        onClick={() => handlePresetClick('pt_down')}>Down</Button>
                    </Grid>
                    <Grid size={4}></Grid>
                  </Grid>
                  <Grid container spacing={2}>
                    <Grid size={6}>
                      <Button fullWidth variant="outlined" startIcon={<Home />}
                        onClick={() => handlePresetClick('pt_home')}>Home</Button>
                    </Grid>
                    <Grid size={6}>
                      <Button fullWidth variant="outlined" startIcon={<Refresh />}
                        onClick={() => handlePresetClick('pt_reset')}>Reset</Button>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Presets Tab */}
              {currentTab === 5 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Recall Preset</Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    {[0, 1, 2, 3].map(i => (
                      <Grid size={{ xs: 6, sm: 3 }} key={i}>
                        <Button fullWidth variant="contained"
                          onClick={() => handlePresetClick(`preset_recall_${i}`)}>
                          Preset {i}
                        </Button>
                      </Grid>
                    ))}
                  </Grid>
                  <Typography variant="h6" gutterBottom>Save Preset</Typography>
                  <Grid container spacing={2}>
                    {[0, 1, 2, 3].map(i => (
                      <Grid size={{ xs: 6, sm: 3 }} key={i}>
                        <Button fullWidth variant="outlined"
                          onClick={() => handlePresetClick(`preset_set_${i}`)}>
                          Save {i}
                        </Button>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Picture Tab */}
              {currentTab === 6 && (
                <Box>
                  <Typography variant="h6" gutterBottom>White Balance</Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('wb_auto')}>Auto</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('wb_indoor')}>Indoor</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('wb_outdoor')}>Outdoor</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('wb_manual')}>Manual</Button>
                    </Grid>
                  </Grid>
                  <Typography variant="h6" gutterBottom>Effects</Typography>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('backlight_on')}>Backlight ON</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('backlight_off')}>Backlight OFF</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('mirror_on')}>Mirror ON</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('mirror_off')}>Mirror OFF</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('flip_on')}>Flip ON</Button>
                    </Grid>
                    <Grid size={{ xs: 6, sm: 4 }}>
                      <Button fullWidth variant="outlined"
                        onClick={() => handlePresetClick('flip_off')}>Flip OFF</Button>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Response Alert */}
              {response && (
                <Alert severity={response.ok ? 'success' : 'error'} sx={{ mt: 2 }}>
                  {response.ok ? (
                    <>Success! {response.resp && `Response: ${response.resp}`}</>
                  ) : (
                    <>Error: {response.err}</>
                  )}
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Event Log */}
          <Card sx={{ mt: 3 }}>
            <CardHeader title="Event Log" />
            <CardContent>
              <Paper sx={{ maxHeight: 400, overflow: 'auto', bgcolor: 'background.default' }}>
                <List dense>
                  {stats.log.length > 0 ? (
                    stats.log.map((entry, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem>
                          <ListItemText
                            primary={entry.m}
                            secondary={
                              <Box component="span" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                {formatTime(entry.t)} -
                                <Chip
                                  label={entry.l}
                                  size="small"
                                  color={entry.l === 'E' ? 'error' : 'success'}
                                  sx={{ ml: 1, height: 16 }}
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                        {idx < stats.log.length - 1 && <Divider />}
                      </React.Fragment>
                    ))
                  ) : (
                    <ListItem>
                      <ListItemText primary="No log entries" secondary="Waiting for events..." />
                    </ListItem>
                  )}
                </List>
              </Paper>
            </CardContent>
          </Card>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;