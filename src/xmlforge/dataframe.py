"""
DataFrame library detection and abstraction layer.

This module provides automatic detection and abstraction for different
DataFrame libraries (pandas, polars, dask, pyspark).
"""

import importlib
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable


class DataFrameLibrary(Enum):
    """Enum for supported DataFrame libraries."""
    PANDAS = "pandas"
    POLARS = "polars"
    DASK = "dask"
    PYSPARK = "pyspark"


@runtime_checkable
class DataFrameLike(Protocol):
    """Protocol for DataFrame-like objects."""
    def __len__(self) -> int: ...
    def __getitem__(self, key: Any) -> Any: ...


class DataFrameLibraryDetector:
    """
    Detects and manages available DataFrame libraries.

    This class automatically detects which DataFrame libraries are installed
    and provides a unified interface for creating DataFrames with any of them.
    """

    def __init__(self):
        """Initialize the detector and scan for available libraries."""
        self._available_libraries = {}
        self._constructors = {}
        self._detect_libraries()

    def _detect_libraries(self) -> None:
        """Detect which DataFrame libraries are available."""
        # Test pandas
        try:
            pd = importlib.import_module("pandas")
            self._available_libraries[DataFrameLibrary.PANDAS] = pd
            self._constructors[DataFrameLibrary.PANDAS] = pd.DataFrame
        except ImportError:
            pass

        # Test polars
        try:
            pl = importlib.import_module("polars")
            self._available_libraries[DataFrameLibrary.POLARS] = pl
            self._constructors[DataFrameLibrary.POLARS] = pl.DataFrame
        except ImportError:
            pass

        # Test dask
        try:
            dask_df = importlib.import_module("dask.dataframe")
            pd = importlib.import_module("pandas")  # Dask needs pandas
            self._available_libraries[DataFrameLibrary.DASK] = dask_df
            # Dask constructor is more complex
            self._constructors[DataFrameLibrary.DASK] = self._create_dask_constructor(dask_df, pd)
        except ImportError:
            pass

        # Test pyspark
        try:
            spark_sql = importlib.import_module("pyspark.sql")
            self._available_libraries[DataFrameLibrary.PYSPARK] = spark_sql
            # PySpark constructor needs active SparkSession
            self._constructors[DataFrameLibrary.PYSPARK] = self._create_pyspark_constructor()
        except ImportError:
            pass

    def _create_dask_constructor(self, dask_df, pd):
        """Create Dask DataFrame constructor."""
        def create_dask_df(data: List[Dict[str, Any]], npartitions: int = 1):
            pandas_df = pd.DataFrame(data)
            return dask_df.from_pandas(pandas_df, npartitions=npartitions)

        return create_dask_df

    def _create_pyspark_constructor(self):
        """Create PySpark DataFrame constructor."""
        def create_spark_df(data: List[Dict[str, Any]]):
            try:
                from pyspark.sql import SparkSession  # type: ignore
                spark = SparkSession.getActiveSession()

                if spark is None:
                    # Create a default session if none exists
                    spark = SparkSession.builder.appName("XMLForge").getOrCreate()

                return spark.createDataFrame(data)
            except Exception as e:
                raise RuntimeError(f"Could not create PySpark DataFrame: {e}")

        return create_spark_df

    def is_available(self, library: DataFrameLibrary) -> bool:
        """
        Check if a DataFrame library is available.

        Args:
            library: The DataFrame library to check.

        Returns:
            True if the library is available, False otherwise.
        """
        return library in self._available_libraries

    def get_available_libraries(self) -> List[DataFrameLibrary]:
        """
        Get list of available DataFrame libraries.

        Returns:
            List of available DataFrame libraries.
        """
        return list(self._available_libraries.keys())

    def get_preferred_library(self) -> Optional[DataFrameLibrary]:
        """
        Get the preferred library based on performance and features.

        Priority order: Polars > Pandas > Dask > PySpark

        Returns:
            The preferred DataFrame library, or None if none are available.
        """
        preference_order = [
            DataFrameLibrary.POLARS,    # Fastest for most operations
            DataFrameLibrary.PANDAS,    # Most common, good performance
            DataFrameLibrary.DASK,      # Good for out-of-core operations
            DataFrameLibrary.PYSPARK    # Good for very large distributed data
        ]

        for lib in preference_order:
            if self.is_available(lib):
                return lib

        return None

    def get_constructor(self, library: DataFrameLibrary):
        """
        Get the DataFrame constructor for the specified library.

        Args:
            library: The DataFrame library.

        Returns:
            The constructor function for the library.

        Raises:
            ImportError: If the library is not available.
        """
        if not self.is_available(library):
            raise ImportError(f"{library.value} is not available")

        return self._constructors[library]

    def create_dataframe(
        self, data: List[Dict[str, Any]],
        library: Optional[DataFrameLibrary] = None,
        **kwargs
    ) -> DataFrameLike:
        """
        Create a DataFrame using the specified or preferred library.

        Args:
            data: List of dictionaries to convert to DataFrame.
            library: Specific library to use, or None for auto-detection.
            **kwargs: Additional arguments for the DataFrame constructor.

        Returns:
            DataFrame instance from the specified library.

        Raises:
            ImportError: If no supported DataFrame library is found.
        """
        if library is None:
            library = self.get_preferred_library()

            if library is None:
                raise ImportError("No supported DataFrame library found")

        constructor = self.get_constructor(library)

        # Handle library-specific kwargs
        if library == DataFrameLibrary.DASK:
            npartitions = kwargs.pop('npartitions', 1)
            return constructor(data, npartitions=npartitions)
        else:
            return constructor(data)

    def get_library_info(self) -> Dict[str, Any]:
        """
        Get information about available DataFrame libraries.

        Returns:
            Dictionary with library availability and version information.
        """
        info = {
            "available_libraries": [lib.value for lib in self.get_available_libraries()],
            "preferred_library": None,
            "versions": {}
        }

        preferred = self.get_preferred_library()
        if preferred:
            info["preferred_library"] = preferred.value

        # Get version information
        for lib in self.get_available_libraries():
            try:
                if lib == DataFrameLibrary.PANDAS:
                    import pandas as pd  # type: ignore
                    info["versions"]["pandas"] = pd.__version__
                elif lib == DataFrameLibrary.POLARS:
                    import polars as pl  # type: ignore
                    info["versions"]["polars"] = pl.__version__
                elif lib == DataFrameLibrary.DASK:
                    import dask  # type: ignore
                    info["versions"]["dask"] = dask.__version__
                elif lib == DataFrameLibrary.PYSPARK:
                    import pyspark  # type: ignore
                    info["versions"]["pyspark"] = pyspark.__version__
            except Exception:
                info["versions"][lib.value] = "unknown"

        return info

    def convert_dataframe(self, df: DataFrameLike,
                         target_library: DataFrameLibrary) -> DataFrameLike:
        """
        Convert DataFrame between different libraries.

        Args:
            df: Source DataFrame.
            target_library: Target library to convert to.

        Returns:
            Converted DataFrame.

        Raises:
            ValueError: If conversion is not possible.
        """
        # Detect source library
        source_library = self._detect_dataframe_type(df)

        if source_library == target_library:
            return df  # No conversion needed

        # Convert via pandas as intermediate format
        if source_library != DataFrameLibrary.PANDAS:
            df = self._to_pandas(df)

        # Convert from pandas to target
        return self._from_pandas(df, target_library)

    def _detect_dataframe_type(self, df: DataFrameLike) -> DataFrameLibrary:
        """Detect the type of a DataFrame object."""
        df_type = type(df).__module__

        if "pandas" in df_type:
            return DataFrameLibrary.PANDAS
        elif "polars" in df_type:
            return DataFrameLibrary.POLARS
        elif "dask" in df_type:
            return DataFrameLibrary.DASK
        elif "pyspark" in df_type:
            return DataFrameLibrary.PYSPARK
        else:
            raise ValueError(f"Unknown DataFrame type: {type(df)}")

    def _to_pandas(self, df: DataFrameLike):
        """Convert any DataFrame to pandas."""
        df_type = self._detect_dataframe_type(df)

        if df_type == DataFrameLibrary.PANDAS:
            return df
        elif df_type == DataFrameLibrary.POLARS:
            return df.to_pandas()  # type: ignore
        elif df_type == DataFrameLibrary.DASK:
            return df.compute()  # type: ignore
        elif df_type == DataFrameLibrary.PYSPARK:
            return df.toPandas()  # type: ignore
        else:
            raise ValueError(f"Cannot convert {df_type} to pandas")

    def _from_pandas(self, df, target_library: DataFrameLibrary):
        """Convert pandas DataFrame to target library."""
        if target_library == DataFrameLibrary.PANDAS:
            return df
        elif target_library == DataFrameLibrary.POLARS:
            import polars as pl  # type: ignore
            return pl.from_pandas(df)
        elif target_library == DataFrameLibrary.DASK:
            import dask.dataframe as dd  # type: ignore
            return dd.from_pandas(df, npartitions=1)
        elif target_library == DataFrameLibrary.PYSPARK:
            from pyspark.sql import SparkSession  # type: ignore
            spark = SparkSession.getActiveSession()
            if spark is None:
                spark = SparkSession.builder.appName("XMLForge").getOrCreate()
            return spark.createDataFrame(df)
        else:
            raise ValueError(f"Cannot convert to {target_library}")


# Global detector instance
_detector = DataFrameLibraryDetector()


def get_detector() -> DataFrameLibraryDetector:
    """
    Get the global DataFrameLibraryDetector instance.

    Returns:
        The global detector instance.
    """
    return _detector


def create_dataframe(data: List[Dict[str, Any]],
                    library: Optional[Union[str, DataFrameLibrary]] = None,
                    **kwargs) -> DataFrameLike:
    """
    Convenience function to create a DataFrame using the global detector.

    Args:
        data: List of dictionaries to convert to DataFrame.
        library: Library name ('pandas', 'polars', 'dask', 'pyspark') or None for auto.
        **kwargs: Additional arguments for the DataFrame constructor.

    Returns:
        DataFrame instance from the specified library.
    """
    lib_enum = None

    if library:
        lib_enum = DataFrameLibrary(library)

    return _detector.create_dataframe(data, lib_enum, **kwargs)
