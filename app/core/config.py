import os
import yaml


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}  # Добавляем заголовок с токеном Bearer


def load_config_from_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "settings.yaml")
config = load_config_from_yaml(config_path)
galileo_ad_name = config.get("galileo_ad_name")
galileo_ad_password = config.get("galileo_ad_password")
engine = config.get("db").get("uri")
domain = config.get("domain")
proxies = f"http://{galileo_ad_name}:{galileo_ad_password}@10.1.8.100:9090"
