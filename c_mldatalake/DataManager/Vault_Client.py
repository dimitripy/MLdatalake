import json
import hvac
import logging

class VaultClient:
    def __init__(self, vault_url, approle_credentials_path):
        self.vault_url = vault_url
        self.creds = self._load_creds(approle_credentials_path)
        self.vault_token = self._authenticate_with_vault()
    
    def _load_creds(self, approle_credentials_path):
        with open(approle_credentials_path) as f:
            return json.load(f)

    def _authenticate_with_vault(self):
        client = hvac.Client(url=self.vault_url)

        auth_response = client.auth.approle.login(
            role_id=self.creds["role_id"],
            secret_id=self.creds["secret_id"]
        )

        if 'auth' in auth_response and 'client_token' in auth_response['auth']:
            return auth_response['auth']['client_token']
        else:
            raise Exception("Authentifizierung bei Vault fehlgeschlagen.")
    
    def get_secret(self, secret_path):
        client = hvac.Client(url=self.vault_url, token=self.vault_token)

        if not client.is_authenticated():
            raise Exception("Authentifizierung bei Vault fehlgeschlagen.")

        secret_response = client.secrets.kv.v2.read_secret_version(path=secret_path)
        return secret_response['data']['data']
    

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().setLevel(logging.DEBUG)

    vault_url = "http://localhost:8200"
    approle_credentials_path = "/home/ageq/Git_Projects/MLdatalake/c_mldatalake/DataManager/approle_credentials.json"
    secret_path = "mysql/user"  
    
    vault_client = VaultClient(vault_url, approle_credentials_path)
    
