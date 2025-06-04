import { useState, useEffect } from "react";

export default function FanvilConfigForm() {
  const [configs, setConfigs] = useState([]);
  const [selected, setSelected] = useState("");
  const [raw, setRaw] = useState("");
  const [dssKeys, setDssKeys] = useState([]);
  const [sip, setSip] = useState({});
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("/api/configs").then(res => res.json()).then(setConfigs);
  }, []);

  const load = async (file) => {
    const r = await fetch("/api/config/" + file);
    const d = await r.json();
    setSelected(file);
    setRaw(d.raw_config);
    setDssKeys(d.dss_keys);
    setSip(d.sip_account);
    setMsg("");
  };

  const save = async () => {
    const r = await fetch("/api/config/" + selected, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_config: raw, dss_keys: dssKeys, sip_account: sip })
    });
    const j = await r.json();
    setMsg(j.message);
  };

  const updateKey = (i, f, v) => {
    const k = [...dssKeys];
    k[i][f] = v;
    setDssKeys(k);
  };

  const updateSip = (f, v) => setSip({ ...sip, [f]: v });

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold">Выбор конфигурации</h2>
      <select onChange={(e) => load(e.target.value)} value={selected} className="border p-2 w-full">
        <option>-- выбрать --</option>
        {configs.map(f => <option key={f}>{f}</option>)}
      </select>

      {selected && (
        <>
          <h2 className="text-xl font-semibold">Настройки SIP1</h2>
          {["phone_number", "display_name", "register_addr", "register_port", "register_user", "register_pswd", "register_ttl", "enable_reg"].map(f => (
            <input key={f} value={sip[f] || ""} onChange={e => updateSip(f, e.target.value)} placeholder={f.replace("_", " ")} className="border p-2 w-full mb-2" />
          ))}

          <h2 className="text-xl font-semibold">DSS Кнопки</h2>
          {dssKeys.map((k, i) => (
            <div key={i} className="grid grid-cols-4 gap-2 mb-1">
              <input value={k.key_type} onChange={e => updateKey(i, "key_type", e.target.value)} placeholder="type" className="border p-1" />
              <input value={k.value} onChange={e => updateKey(i, "value", e.target.value)} placeholder="value" className="border p-1" />
              <input value={k.label} onChange={e => updateKey(i, "label", e.target.value)} placeholder="label" className="border p-1" />
              <input value={k.icon} onChange={e => updateKey(i, "icon", e.target.value)} placeholder="icon" className="border p-1" />
            </div>
          ))}
          <button onClick={() => setDssKeys([...dssKeys, { index: dssKeys.length + 1, key_type: 1, value: "", label: "", icon: "Green" }])} className="bg-blue-500 text-white px-4 py-1 rounded">
            Добавить кнопку
          </button>

          <div>
            <button onClick={save} className="mt-4 bg-green-600 text-white px-6 py-2 rounded">Сохранить</button>
            {msg && <p className="text-green-700 mt-2">{msg}</p>}
          </div>
        </>
      )}
    </div>
  );
}
