/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState } from "react";
import { Snackbar, Alert } from "@mui/material";

const SnackbarFeedback: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("Command sent!");
  const [severity, setSeverity] = useState<"success" | "error">("success");

  // openSnackbar(message, severity) kann von anderen Tabs aufgerufen werden
  const openSnackbar = (msg: string, sev: "success" | "error") => {
    setMessage(msg);
    setSeverity(sev);
    setOpen(true);
  };

  return (
    <Snackbar open={open} autoHideDuration={2000} onClose={() => setOpen(false)}>
      <Alert severity={severity} sx={{ width: "100%" }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default SnackbarFeedback;
