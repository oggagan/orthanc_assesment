"""Orthanc REST API client."""

import httpx
from dicom_middleware.config import get_settings


def _orthanc_auth() -> httpx.Auth | None:
    """Basic auth for Orthanc if username/password are set."""
    s = get_settings()
    if s.orthanc_username and s.orthanc_password:
        return httpx.BasicAuth(s.orthanc_username, s.orthanc_password)
    return None


class OrthancClient:
    """Client for Orthanc REST API."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or get_settings().orthanc_url).rstrip("/")
        self.auth = _orthanc_auth()

    async def get_study_ids(self) -> list[str]:
        """List all study IDs (Orthanc internal IDs)."""
        async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
            r = await client.get(f"{self.base_url}/studies")
            r.raise_for_status()
            return r.json()

    async def get_study_instance_uid(self, orthanc_study_id: str) -> str:
        """Get DICOM Study Instance UID for an Orthanc study ID."""
        async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
            r = await client.get(f"{self.base_url}/studies/{orthanc_study_id}")
            r.raise_for_status()
            data = r.json()
            return data.get("MainDicomTags", {}).get("StudyInstanceUID", "")

    async def get_study_archive(self, orthanc_study_id: str) -> bytes:
        """Retrieve the DICOM archive (ZIP) for a study. Returns raw bytes."""
        async with httpx.AsyncClient(timeout=60.0, auth=self.auth) as client:
            r = await client.get(f"{self.base_url}/studies/{orthanc_study_id}/archive")
            r.raise_for_status()
            return r.content

    async def get_first_instance_archive(self, orthanc_study_id: str) -> bytes:
        """Get study -> first series -> first instance, return DICOM bytes. Orthanc hierarchy is Study -> Series -> Instances."""
        async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
            r = await client.get(f"{self.base_url}/studies/{orthanc_study_id}")
            r.raise_for_status()
            data = r.json()
            series_list = data.get("Series", [])
            if not series_list:
                raise ValueError(f"No series in study {orthanc_study_id}")
            first_series_id = series_list[0]
            r2 = await client.get(f"{self.base_url}/series/{first_series_id}")
            r2.raise_for_status()
            series_data = r2.json()
            instances = series_data.get("Instances", [])
            if not instances:
                raise ValueError(f"No instances in study {orthanc_study_id}")
            first_instance_id = instances[0]
            r3 = await client.get(f"{self.base_url}/instances/{first_instance_id}/file")
            r3.raise_for_status()
            return r3.content
