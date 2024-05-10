from pydantic import BaseModel
from typing import Optional, List
from dataclasses import dataclass, field
from webauthn.helpers.structs import AuthenticatorTransport, CredentialDeviceType

@dataclass
class Credential:
    id: bytes
    public_key: bytes
    sign_count: int
    transports: Optional[List[AuthenticatorTransport]] = None

@dataclass
class User(BaseModel):
    id: str
    public_key: str
    username: str
    sign_count: int
    is_discoverable_credential: Optional[bool]
    device_type: CredentialDeviceType
    backed_up: bool
    transports: Optional[List[AuthenticatorTransport]]
    aaguid: str = ""
    