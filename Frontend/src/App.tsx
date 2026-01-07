import React, { useState } from "react";
import { Box, Tabs, Tab, Card, CardContent } from "@mui/material";
import ManualTab from "./components/ManualTab";
import PowerTab from "./components/PowerTab";
import ZoomTab from "./components/ZoomTab";
import FocusTab from "./components/FocusTab";
import PanTiltTab from "./components/PanTiltTab";
import PresetsTab from "./components/PresetsTab";
import PictureTab from "./components/PictureTab";
import EventLog from "./components/EventLog";
import SnackbarFeedback from "./components/SnackbarFeedback";

const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<number>(0);

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
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
          {currentTab === 0 && <ManualTab />}
          {currentTab === 1 && <PowerTab />}
          {currentTab === 2 && <ZoomTab />}
          {currentTab === 3 && <FocusTab />}
          {currentTab === 4 && <PanTiltTab />}
          {currentTab === 5 && <PresetsTab />}
          {currentTab === 6 && <PictureTab />}
        </CardContent>
      </Card>

      <EventLog />
      <SnackbarFeedback />
    </Box>
  );
};

export default App;
