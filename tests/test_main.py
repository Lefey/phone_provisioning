import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import backend.main as m
from backend.main import DSSKey, SIPAccount, ConfigFile, format_dss_block, format_sip_block


def test_extract_dss_keys():
    keys = [
        DSSKey(index=1, key_type=1, value="100", label="One", icon="Red"),
        DSSKey(index=2, key_type=2, value="200", label="Two", icon="Green"),
    ]
    config = format_dss_block(keys) + "\n"
    assert m.extract_dss_keys(config) == keys


def test_extract_sip_account():
    sip = SIPAccount(
        phone_number="100",
        display_name="Test",
        register_addr="srv",
        register_port="5060",
        register_user="user",
        register_password="pass",
        register_ttl="60",
        enable_reg="1",
    )
    config = format_sip_block(sip)
    assert m.extract_sip_account(config) == sip


def test_format_dss_block():
    keys = [DSSKey(index=1, key_type=1, value="100", label="One", icon="Red")]
    expected = (
        "<DSSKEY CONFIG MODULE>\n"
        "--Dsskey Config1--\n"
        "Fkey1 Type    :1\n"
        "Fkey1 Value   :100\n"
        "Fkey1 Title   :One\n"
        "Fkey1 ICON    :Red\n"
    )
    assert format_dss_block(keys) == expected


def test_format_sip_block():
    sip = SIPAccount(
        phone_number="100",
        display_name="Test",
        register_addr="srv",
        register_port="5060",
        register_user="user",
        register_password="pass",
        register_ttl="60",
        enable_reg="1",
    )
    expected = (
        "<SIP CONFIG MODULE>\n"
        "SIP1 Phone Number     :100\n"
        "SIP1 Display Name     :Test\n"
        "SIP1 Register Addr    :srv\n"
        "SIP1 Register Port    :5060\n"
        "SIP1 Register User    :user\n"
        "SIP1 Register Password:pass\n"
        "SIP1 Register TTL     :60\n"
        "SIP1 Enable Reg       :1\n"
        "<<END OF FILE>>"
    )
    assert format_sip_block(sip) == expected


def test_save_config_updates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "CONFIG_DIR", str(tmp_path))

    old_keys = [DSSKey(index=1, key_type=0, value="old", label="Old", icon="Green")]
    old_sip = SIPAccount(
        phone_number="old",
        display_name="Old",
        register_addr="old",
        register_port="1000",
        register_user="old",
        register_password="old",
        register_ttl="30",
        enable_reg="1",
    )
    original = format_dss_block(old_keys) + "\n" + format_sip_block(old_sip)
    cfg_path = tmp_path / "phone.cfg"
    cfg_path.write_text(original, encoding="utf-8")

    new_keys = [DSSKey(index=1, key_type=1, value="100", label="New", icon="Red")]
    new_sip = SIPAccount(
        phone_number="100",
        display_name="New",
        register_addr="srv",
        register_port="5060",
        register_user="user",
        register_password="pass",
        register_ttl="60",
        enable_reg="1",
    )
    data = ConfigFile(dss_keys=new_keys, sip_account=new_sip, raw_config=original)
    m.save_config("phone.cfg", data)

    expected = format_dss_block(new_keys) + "\n" + format_sip_block(new_sip)
    assert cfg_path.read_text(encoding="utf-8") == expected
