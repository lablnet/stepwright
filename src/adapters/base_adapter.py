# adapters/base_adapter.py
# Abstract Base Class for StepWright Enterprise Storage Adapters
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseStorageAdapter(ABC):
    """
    Abstract Base Class for StepWright Storage Adapters.

    Any storage adapter (SQL, NoSQL, Cloud S3/GCS, Message Queue, or File) must
    implement this contract to be pluggable into StepWright data export workflows.

    @since 2.0.0
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection or prepare storage resource."""
        pass

    @abstractmethod
    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Write scraped data record(s) to the target storage sink.

        :param data: Single dictionary record or list of record dictionaries
        :param options: Additional writing options (table name, bucket, topic, file path, etc.)
        :return: True if write succeeded, False otherwise
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection or release storage resource."""
        pass
