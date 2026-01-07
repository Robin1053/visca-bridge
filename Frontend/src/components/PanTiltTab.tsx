import React from "react";
import { Button, Box } from "@mui/material";
import Grid from "@mui/material/GridLegacy";
import { ArrowBack, ArrowDownward, ArrowForward, ArrowUpward, Home, Refresh, Stop, } from "@mui/icons-material";

const PanTiltTab: React.FC = () => {
    const handlePresetClick = (cmd: string) => {
        fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
    };

    return (
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
    );
};

export default PanTiltTab;
