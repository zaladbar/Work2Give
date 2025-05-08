import { useSettings } from "./lib/state";

function App() {
  const { settings, setSettings } = useSettings();
  const { idleMinutes, cloudMode, devShare } = settings;
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div>
        <label className="flex items-center justify-between">
          <span>Idle Minutes:</span>
          <input 
            type="number" 
            value={idleMinutes} 
            onChange={e => setSettings({ ...settings, idleMinutes: +e.target.value })} 
            className="border p-1 w-20 text-right" 
          />
        </label>
      </div>

      <div>
        <label className="flex items-center justify-between">
          <span>Cloud Mode:</span>
          <input 
            type="checkbox" 
            checked={cloudMode} 
            onChange={e => setSettings({ ...settings, cloudMode: e.target.checked })} 
            className="h-4 w-4" 
          />
        </label>
      </div>

      <div>
        <label className="flex flex-col">
          <span>Dev Share: {Math.round(devShare * 100)}%</span>
          <input 
            type="range" 
            min="0" max="1" step="0.01" 
            value={devShare} 
            onChange={e => setSettings({ ...settings, devShare: parseFloat(e.target.value) })} 
            className="mt-1"
          />
        </label>
      </div>
    </div>
  );
}

export default App;
