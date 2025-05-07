"""
Secure Credentials Manager for InsightForge

This module provides secure storage and retrieval of sensitive credentials
for various integrations like API keys, tokens and passwords.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Check if keyring is available
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning("Keyring module not available. Secure storage of credentials will be limited.")

# Check if cryptography is available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logger.warning("Cryptography module not available. Fallback to simple obfuscation will be used.")


class CredentialsManager:
    """Manager for securely storing and retrieving credentials."""
    
    def __init__(self, app_name: str = "insightforge"):
        """
        Initialize the credentials manager.
        
        Args:
            app_name: Application name for keyring storage
        """
        self.app_name = app_name
        self._cache = {}
        self._fallback_file = os.path.expanduser("~/.insightforge/credentials.json")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self._fallback_file), exist_ok=True)
        
        # Load credentials from fallback file if needed
        if not KEYRING_AVAILABLE and os.path.exists(self._fallback_file):
            self._load_fallback()
    
    def set_credential(self, integration: str, key: str, value: str) -> None:
        """
        Store a credential securely.
        
        Args:
            integration: Integration name (e.g., 'jira', 'github')
            key: Credential key (e.g., 'api_token', 'password')
            value: The value to store
        """
        credential_key = f"{integration}_{key}"
        
        if KEYRING_AVAILABLE:
            # Store in system keyring
            keyring.set_password(self.app_name, credential_key, value)
            logger.debug(f"Credential '{credential_key}' stored in system keyring")
        else:
            # Store in local cache and save to file
            self._cache[credential_key] = self._obfuscate(value)
            self._save_fallback()
            logger.debug(f"Credential '{credential_key}' stored in fallback file")
    
    def get_credential(self, integration: str, key: str) -> Optional[str]:
        """
        Retrieve a stored credential.
        
        Args:
            integration: Integration name (e.g., 'jira', 'github')
            key: Credential key (e.g., 'api_token', 'password')
            
        Returns:
            The stored value or None if not found
        """
        credential_key = f"{integration}_{key}"
        
        if KEYRING_AVAILABLE:
            # Retrieve from system keyring
            value = keyring.get_password(self.app_name, credential_key)
            if value:
                logger.debug(f"Credential '{credential_key}' retrieved from system keyring")
                return value
        
        # Try fallback
        if credential_key in self._cache:
            value = self._deobfuscate(self._cache[credential_key])
            logger.debug(f"Credential '{credential_key}' retrieved from fallback storage")
            return value
        
        logger.debug(f"Credential '{credential_key}' not found")
        return None
    
    def delete_credential(self, integration: str, key: str) -> bool:
        """
        Delete a stored credential.
        
        Args:
            integration: Integration name (e.g., 'jira', 'github')
            key: Credential key (e.g., 'api_token', 'password')
            
        Returns:
            True if the credential was deleted, False otherwise
        """
        credential_key = f"{integration}_{key}"
        
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.app_name, credential_key)
                logger.debug(f"Credential '{credential_key}' deleted from system keyring")
                return True
            except Exception as e:
                logger.debug(f"Error deleting credential from keyring: {str(e)}")
        
        # Also remove from fallback
        if credential_key in self._cache:
            del self._cache[credential_key]
            self._save_fallback()
            logger.debug(f"Credential '{credential_key}' deleted from fallback storage")
            return True
        
        return False
    
    def _obfuscate(self, value: str) -> str:
        """
        Obfuscate a value for storage.
        
        Args:
            value: Value to obfuscate
            
        Returns:
            Obfuscated value
        """
        if ENCRYPTION_AVAILABLE:
            try:
                # Generate a key from the machine-specific information
                # Note: This is not fully secure as the key is derived from predictable values
                # but it's better than plain text
                machine_id = self._get_machine_id()
                salt = b'insightforge'  # Using a static salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
                
                # Encrypt the value
                f = Fernet(key)
                token = f.encrypt(value.encode())
                return token.decode()
            except Exception as e:
                logger.warning(f"Encryption failed, falling back to simple obfuscation: {str(e)}")
        
        # Simple base64 encoding as fallback
        # This is not secure, just prevents casual viewing
        return base64.b64encode(value.encode()).decode()
    
    def _deobfuscate(self, value: str) -> str:
        """
        Deobfuscate a stored value.
        
        Args:
            value: Obfuscated value
            
        Returns:
            Original value
        """
        if ENCRYPTION_AVAILABLE:
            try:
                # Generate the key again
                machine_id = self._get_machine_id()
                salt = b'insightforge'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
                
                # Decrypt the value
                f = Fernet(key)
                return f.decrypt(value.encode()).decode()
            except Exception as e:
                logger.warning(f"Decryption failed, trying simple decoding: {str(e)}")
        
        # Simple base64 decoding as fallback
        try:
            return base64.b64decode(value.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to decode value: {str(e)}")
            return ""
    
    def _get_machine_id(self) -> str:
        """
        Get a unique machine identifier for encryption key derivation.
        
        Returns:
            A string that should be unique to this machine
        """
        # Try to get machine ID from different sources
        machine_id = ""
        
        # Try dbus machine ID on Linux
        if os.path.exists("/var/lib/dbus/machine-id"):
            try:
                with open("/var/lib/dbus/machine-id", "r") as f:
                    machine_id = f.read().strip()
            except Exception:
                pass
        
        # Try Windows registry
        if not machine_id and os.name == "nt":
            try:
                import winreg
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                         r"SOFTWARE\Microsoft\Cryptography")
                machine_id, _ = winreg.QueryValueEx(reg_key, "MachineGuid")
                winreg.CloseKey(reg_key)
            except Exception:
                pass
        
        # Try macOS system UUID
        if not machine_id and os.path.exists("/usr/sbin/system_profiler"):
            try:
                import subprocess
                output = subprocess.check_output(["/usr/sbin/system_profiler", "SPHardwareDataType"])
                for line in output.decode().split("\n"):
                    if "UUID" in line:
                        machine_id = line.strip().split(":")[1].strip()
                        break
            except Exception:
                pass
        
        # Fallback to hostname if all else fails
        if not machine_id:
            import socket
            machine_id = socket.gethostname()
        
        return machine_id
    
    def _save_fallback(self) -> None:
        """Save credentials to fallback file."""
        try:
            with open(self._fallback_file, "w") as f:
                json.dump(self._cache, f)
            
            # Set restrictive permissions on the file
            os.chmod(self._fallback_file, 0o600)
        except Exception as e:
            logger.error(f"Failed to save credentials to fallback file: {str(e)}")
    
    def _load_fallback(self) -> None:
        """Load credentials from fallback file."""
        try:
            with open(self._fallback_file, "r") as f:
                self._cache = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials from fallback file: {str(e)}")
            self._cache = {}


# Singleton instance
_instance = None

def get_credentials_manager() -> CredentialsManager:
    """
    Get the singleton instance of CredentialsManager.
    
    Returns:
        CredentialsManager instance
    """
    global _instance
    if _instance is None:
        _instance = CredentialsManager()
    return _instance