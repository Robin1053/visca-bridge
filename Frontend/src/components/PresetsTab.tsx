import React from "react";
import { Button, Box, Typography } from "@mui/material";
import Grid from "@mui/material/GridLegacy";

const PresetsTab: React.FC = () => {
    const handlePresetClick = (cmd: string) => {
        fetch(`/preset/virtual/${cmd}`, { method: "POST" }).catch(console.error);
    };

    return (
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
    );
};

export default PresetsTab;
