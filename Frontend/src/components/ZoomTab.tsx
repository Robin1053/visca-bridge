import React from "react";
import { Button } from "@mui/material";
import Grid from "@mui/material/GridLegacy";
import { ZoomIn, ZoomOut, Stop } from "@mui/icons-material";

const ZoomTab: React.FC = () => {
    const handlePresetClick = (cmd: string) => {
        fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
    };

    return (
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
    );
};

export default ZoomTab;
