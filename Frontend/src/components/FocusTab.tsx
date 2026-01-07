import React from "react";
import { Button } from "@mui/material";
import Grid from "@mui/material/GridLegacy";
import { Stop } from "@mui/icons-material";

const FocusTab: React.FC = () => {
    const handlePresetClick = (cmd: string) => {
        fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
    };

    return (
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
    );
};

export default FocusTab;
