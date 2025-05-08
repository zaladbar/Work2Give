import { useState, useEffect } from "react";
import { writeTextFile, readTextFile, BaseDirectory } from "@tauri-apps/api/fs";

interface Settings {
  idleMinutes: number;
  cloudMode: boolean;
  devShare: number;
}

const defaultSettings: Settings = {
  idleMinutes: 5,
  cloudMode: false,
  devShare: 0.10
};

export function useSettings() {
  const [settings, setSettings] = useState<Settings>(defaultSettings);

  // Load settings from disk on mount
  useEffect(() => {
    readTextFile("settings.json", { dir: BaseDirectory.App })
      .then(file => {
        const loaded = JSON.parse(file);
        setSettings(prev => ({ ...prev, ...loaded }));
      })
      .catch(() => {
        /* no saved settings, use defaults */
      });
  }, []);

  // Save settings to disk whenever they change
  useEffect(() => {
    writeTextFile("settings.json", JSON.stringify(settings), { dir: BaseDirectory.App })
      .catch(err => console.error("Failed to save settings:", err));
  }, [settings]);

  return { settings, setSettings };
}
