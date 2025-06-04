from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import re

app = FastAPI()
CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DSSKey(BaseModel):
    index: int
    key_type: int
    value: str
    label: str
    icon: str = "Green"

class SIPAccount(BaseModel):
    phone_number: str
    display_name: Optional[str] = ""
    register_addr: str
    register_port: str
    register_user: str
    register_password: str
    register_ttl: str
    enable_reg: str

class ConfigFile(BaseModel):
    dss_keys: List[DSSKey]
    raw_config: str
    sip_account: SIPAccount

@app.get("/api/configs")
def list_configs():
    return [f for f in os.listdir(CONFIG_DIR) if f.endswith(".cfg")]

@app.get("/api/config/{filename}")
def get_config(filename: str):
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Config not found")
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    dss = extract_dss_keys(raw)
    sip = extract_sip_account(raw)
    return {"dss_keys": dss, "sip_account": sip, "raw_config": raw}

@app.post("/api/config/{filename}")
def save_config(filename: str, data: ConfigFile):
    new_dss = format_dss_block(data.dss_keys)
    new_sip = format_sip_block(data.sip_account)

    config = data.raw_config
    if "<DSSKEY CONFIG MODULE>" in config:
        config = re.sub(
            r"<DSSKEY CONFIG MODULE>\n--Dsskey Config1--.*?\n\n",
            new_dss + "\n",
            config,
            flags=re.DOTALL,
        )
    else:
        config = new_dss + "\n" + config

    if "<SIP CONFIG MODULE>" in config:
        config = re.sub(
            r"<SIP CONFIG MODULE>.*?<<END OF FILE>>",
            new_sip,
            config,
            flags=re.DOTALL,
        )
    else:
        config = config.strip() + "\n" + new_sip

    with open(os.path.join(CONFIG_DIR, filename), "w", encoding="utf-8") as f:
        f.write(config)
    return {"message": "Config updated"}

def extract_dss_keys(config: str) -> List[DSSKey]:
    match = re.search(r"<DSSKEY CONFIG MODULE>\n--Dsskey Config1--(.*?)\n\n", config, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    keys = []
    for i in range(1, 33):
        t = re.search(rf"Fkey{i} Type\s*:(\d+)", block)
        v = re.search(rf"Fkey{i} Value\s*:(.+)", block)
        l = re.search(rf"Fkey{i} Title\s*:(.+)", block)
        ic = re.search(rf"Fkey{i} ICON\s*:(.+)", block)
        if t and v and l:
            keys.append(DSSKey(
                index=i,
                key_type=int(t.group(1)),
                value=v.group(1).strip(),
                label=l.group(1).strip(),
                icon=ic.group(1).strip() if ic else "Green"
            ))
    return keys

def extract_sip_account(config: str) -> SIPAccount:
    block = re.search(r"<SIP CONFIG MODULE>(.*?)<<END OF FILE>>", config, re.DOTALL)
    text = block.group(1) if block else ""
    def g(k): return re.search(rf"SIP1 {k}\s*:(.*)", text)
    return SIPAccount(
        phone_number=g("Phone Number").group(1).strip() if g("Phone Number") else "",
        display_name=g("Display Name").group(1).strip() if g("Display Name") else "",
        register_addr=g("Register Addr").group(1).strip() if g("Register Addr") else "",
        register_port=g("Register Port").group(1).strip() if g("Register Port") else "",
        register_user=g("Register User").group(1).strip() if g("Register User") else "",
        register_password=g("Register Password").group(1).strip() if g("Register Password") else "",
        register_ttl=g("Register TTL").group(1).strip() if g("Register TTL") else "",
        enable_reg=g("Enable Reg").group(1).strip() if g("Enable Reg") else ""
    )

def format_dss_block(dss_keys: List[DSSKey]) -> str:
    lines = ["<DSSKEY CONFIG MODULE>", "--Dsskey Config1--"]
    for key in dss_keys:
        lines.append(f"Fkey{key.index} Type    :{key.key_type}")
        lines.append(f"Fkey{key.index} Value   :{key.value}")
        lines.append(f"Fkey{key.index} Title   :{key.label}")
        lines.append(f"Fkey{key.index} ICON    :{key.icon}")
    lines.append("")  # extra newline
    return "\n".join(lines)

def format_sip_block(sip: SIPAccount) -> str:
    return f"""<SIP CONFIG MODULE>
SIP1 Phone Number     :{sip.phone_number}
SIP1 Display Name     :{sip.display_name}
SIP1 Register Addr    :{sip.register_addr}
SIP1 Register Port    :{sip.register_port}
SIP1 Register User    :{sip.register_user}
SIP1 Register Password:{sip.register_password}
SIP1 Register TTL     :{sip.register_ttl}
SIP1 Enable Reg       :{sip.enable_reg}
<<END OF FILE>>"""
