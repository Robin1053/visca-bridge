import React, { useState } from "react";
import { Card, CardContent, CardHeader, Paper, List, ListItem, ListItemText } from "@mui/material";
import type { LogEntry } from "../types";

const EventLog: React.FC = () => {
    const [log] = useState<LogEntry[]>([]);

    return (
        <Card sx={{ mt: 3 }}>
            <CardHeader title="Event Log" />
            <CardContent>
                <Paper sx={{ maxHeight: 300, overflow: "auto", bgcolor: "background.default", p: 1 }}>
                    <List dense>
                        {log.length === 0 && <ListItem><ListItemText primary="No log entries yet" /></ListItem>}
                        {log.map((entry, idx) => (
                            <ListItem key={idx} disableGutters>
                                <ListItemText
                                    primaryTypographyProps={{ fontFamily: "monospace", fontSize: 12 }}
                                    primary={`${new Date(entry.t * 1000).toLocaleTimeString()} [${entry.l}] ${entry.m}`}
                                />
                            </ListItem>
                        ))}
                    </List>
                </Paper>
            </CardContent>
        </Card>
    );
};

export default EventLog;
