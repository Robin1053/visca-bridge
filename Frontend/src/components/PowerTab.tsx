import React from "react";
import { Button } from "@mui/material";
import { PowerSettingsNew, Refresh } from "@mui/icons-material";
import Grid from "@mui/material/GridLegacy";

const PowerTab: React.FC = () => {
  const handlePresetClick = (cmd: string) => {
    fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
  };

  return (
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
  );
};

export default PowerTab;
