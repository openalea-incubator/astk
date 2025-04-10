from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openalea.astk")
except PackageNotFoundError:
    # package is not installed
    pass