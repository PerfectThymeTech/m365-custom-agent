
import base64
import zlib

class DataCompressionClient:
    """Custom exception for file compression errors."""
    
    @staticmethod
    def compress_string(input_string: str) -> str:
        """
        Compress a string using zlib and encode it with base64.

        :param input_string: The string to compress.
        :type input_string: str
        :return: The compressed and base64-encoded string.
        :rtype: str
        """
        compressed = zlib.compress(input_string.encode("utf-8"), level=9)
        return base64.b64encode(compressed).decode("utf-8")

    @staticmethod
    def decompress_string(compressed_string: str) -> str:
        """
        Decompress a base64-encoded zlib-compressed string.

        :param compressed_string: The compressed string to decompress.
        :type compressed_string: str
        :return: The decompressed string.
        :rtype: str
        """
        compressed_bytes = base64.b64decode(compressed_string.encode("utf-8"))
        decompressed = zlib.decompress(compressed_bytes)
        return decompressed.decode("utf-8")
