import React from "react";
import { Button, Box, Typography } from "@mui/material";
import Grid from "@mui/material/GridLegacy";

const ZoomTab: React.FC = () => {
    const handlePresetClick = (cmd: string) => {
        fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
    };

    return (
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
    );
};

export default ZoomTab;
