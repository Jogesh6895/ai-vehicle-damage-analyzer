"""
File Handler Module

This module handles all file I/O operations for the Vehicle Damage Analyzer.
It manages reading input files, writing output files, and directory operations.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union
from datetime import datetime


class FileHandler:
    """
    Handles file operations for input and output data.

    This class provides methods to read images from input directories,
    write reports to output directories, and manage file operations.

    Attributes:
        config: Configuration instance containing directory paths
    """

    def __init__(self, config):
        """
        Initialize FileHandler with configuration.

        Args:
            config: Configuration instance with directory settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_input_files(self, directory: Optional[str] = None) -> List[Path]:
        """
        Get all supported image files from input directory.

        Args:
            directory: Directory to scan (uses config.input_dir if None)

        Returns:
            List[Path]: List of image file paths

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        input_dir = directory or self.config.input_dir

        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        files = []
        for ext in self.config.supported_formats:
            files.extend(Path(input_dir).glob(f"*{ext}"))
            files.extend(Path(input_dir).glob(f"*{ext.upper()}"))

        self.logger.info(f"Found {len(files)} image files in {input_dir}")
        return sorted(files)

    def read_image(self, file_path: Union[str, Path]) -> bytes:
        """
        Read image file as bytes.

        Args:
            file_path: Path to image file

        Returns:
            bytes: Image data

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.logger.debug(f"Read image: {file_path} ({len(data)} bytes)")
            return data
        except Exception as e:
            self.logger.error(f"Failed to read image {file_path}: {e}")
            raise IOError(f"Failed to read image: {e}")

    def write_report(
        self, data: dict, filename: Optional[str] = None, subdir: Optional[str] = None
    ) -> Path:
        """
        Write analysis report to CSV file.

        Args:
            data: Dictionary containing report data
            filename: Output filename (auto-generated if None)
            subdir: Subdirectory within output_dir

        Returns:
            Path: Path to written file

        Raises:
            IOError: If file cannot be written
        """
        import pandas as pd

        output_dir = Path(self.config.output_dir)
        if subdir:
            output_dir = output_dir / subdir
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"damage_report_{timestamp}.csv"

        if not filename.endswith(".csv"):
            filename += ".csv"

        output_path = output_dir / filename

        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            self.logger.info(f"Report written to: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to write report: {e}")
            raise IOError(f"Failed to write report: {e}")

    def write_text_report(
        self, content: str, filename: Optional[str] = None, subdir: Optional[str] = None
    ) -> Path:
        """
        Write text report to file.

        Args:
            content: Text content to write
            filename: Output filename (auto-generated if None)
            subdir: Subdirectory within output_dir

        Returns:
            Path: Path to written file

        Raises:
            IOError: If file cannot be written
        """
        output_dir = Path(self.config.output_dir)
        if subdir:
            output_dir = output_dir / subdir
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"damage_report_{timestamp}.txt"

        output_path = output_dir / filename

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"Text report written to: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to write text report: {e}")
            raise IOError(f"Failed to write text report: {e}")

    def copy_to_input(self, source_file: Union[str, Path]) -> Path:
        """
        Copy a file to the input directory.

        Args:
            source_file: Path to source file

        Returns:
            Path: Path to copied file

        Raises:
            FileNotFoundError: If source file doesn't exist
            IOError: If file cannot be copied
        """
        source_file = Path(source_file)

        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")

        dest_path = Path(self.config.input_dir) / source_file.name

        try:
            shutil.copy2(source_file, dest_path)
            self.logger.info(f"Copied {source_file} to {dest_path}")
            return dest_path
        except Exception as e:
            self.logger.error(f"Failed to copy file: {e}")
            raise IOError(f"Failed to copy file: {e}")

    def clean_output_dir(self, older_than_days: int = 0) -> int:
        """
        Clean old report files from output directory.

        Args:
            older_than_days: Delete files older than this many days (0 for all)

        Returns:
            int: Number of files deleted
        """
        output_dir = Path(self.config.output_dir)

        if not output_dir.exists():
            return 0

        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (older_than_days * 86400)

        for file_path in output_dir.glob("damage_report_*"):
            try:
                if older_than_days == 0 or file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    self.logger.debug(f"Deleted old report: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete {file_path}: {e}")

        self.logger.info(f"Deleted {deleted_count} old report files")
        return deleted_count

    def get_output_files(self, pattern: str = "*") -> List[Path]:
        """
        Get list of output files matching pattern.

        Args:
            pattern: File pattern to match (e.g., "*.csv")

        Returns:
            List[Path]: List of matching file paths
        """
        output_dir = Path(self.config.output_dir)

        if not output_dir.exists():
            return []

        files = list(output_dir.glob(pattern))
        return sorted(files)

    def validate_image_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate if file has a supported image format.

        Args:
            file_path: Path to image file

        Returns:
            bool: True if format is supported, False otherwise
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        return ext in self.config.supported_formats

    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about a file.

        Args:
            file_path: Path to file

        Returns:
            dict: File information including size, modification time, etc.

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()

        return {
            "name": file_path.name,
            "path": str(file_path.absolute()),
            "size": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix,
        }
