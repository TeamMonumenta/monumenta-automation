from typing import List, Dict, Any
import requests

class ZFSSnapshotManager:
    """
    A class to interact with a ZFS snapshot management API for performing operations like
    fetching available space, listing snapshots, creating and deleting snapshots.

    Attributes:
        hostname (str): The hostname of the server.
        port (int): The port number of the server.
    """

    def __init__(self, hostname: str, port: int) -> None:
        """
        Initializes the ZFSSnapshotManager with the given hostname and port.

        Args:
            hostname (str): The hostname of the API server.
            port (int): The port number of the API server.
        """
        self._base_url = f"http://{hostname}:{port}"

    def _request(self, path: str) -> Dict[str, Any]:
        """
        Sends a GET request to the given endpoint and handles errors.

        Args:
            endpoint (str): The API endpoint to send the GET request to.

        Returns:
            dict: The parsed JSON response from the API.

        Raises:
            RuntimeError: If the response status code indicates an error.
        """
        try:
            response = requests.get(f"{self._base_url}/{path}")
            response.raise_for_status()  # Will raise an HTTPError if the status is 4xx/5xx
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")

    def free(self, dataset: str) -> int:
        """
        Fetches the free space available for the given dataset.

        Args:
            dataset (str): The dataset name (e.g., "ipool/home").

        Returns:
            int: The available free space in gigabytes.

        Raises:
            RuntimeError: If the API request fails or returns an error.
        """
        data = self._request(f"free?dataset={dataset}")
        return int(data["free"])

    def list(self, dataset: str) -> List[Dict[str, str]]:
        """
        Lists all snapshots for the given dataset.

        Args:
            dataset (str): The dataset name (e.g., "ipool/home").

        Returns:
            list: A list of snapshots, where each snapshot is a dictionary containing
                  'name', 'refer', and 'used' keys.

        Raises:
            RuntimeError: If the API request fails or returns an error.
        """
        data = self._request(f"list?dataset={dataset}")
        return data.get("snapshots", [])

    def create(self, dataset: str, snapshot: str) -> None:
        """
        Creates a snapshot for the given dataset.

        Args:
            dataset (str): The dataset name (e.g., "ipool/home").
            snapshot (str): The snapshot name to create.

        Raises:
            RuntimeError: If the API request fails or returns an error.
        """
        data = self._request(f"create?dataset={dataset}&snapshot={snapshot}")
        if data.get("status") != "success":
            raise RuntimeError(f"Failed to create snapshot: {data}")

    def delete(self, dataset: str, snapshot: str) -> None:
        """
        Deletes a snapshot for the given dataset.

        Args:
            dataset (str): The dataset name (e.g., "ipool/home").
            snapshot (str): The snapshot name to delete.

        Raises:
            RuntimeError: If the API request fails or returns an error.
        """
        data = self._request(f"delete?dataset={dataset}&snapshot={snapshot}")
        if data.get("status") != "success":
            raise RuntimeError(f"Failed to delete snapshot: {data}")
