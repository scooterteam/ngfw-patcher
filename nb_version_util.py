import re

class NbVersionUtil:
    """
    Utility class for handling version number formatting.
    Converts integer-encoded version numbers into string representations and vice versa.
    """

    VERSION_SEPERATOR = "."

    @staticmethod
    def version_to_string(encoded_version: int, parts: int = None, sep: str = None) -> str:
        """
        Decodes the given integer into a version string.
        If parts is not specified, uses the high nibble to determine 3 or 4 parts.
        """
        if sep is None:
            sep = NbVersionUtil.VERSION_SEPERATOR
        if parts is None:
            high_nibble = (encoded_version >> 12) & 0xF
            parts = 4 if high_nibble != 0 else 3

        segments = []
        for i in range(parts - 1, -1, -1):
            part_value = (encoded_version >> (i * 4)) & 0xF if encoded_version != 0 else 0
            segments.append(str(part_value))

        return sep.join(segments).strip()

    @staticmethod
    def string_to_version(version: str, sep: str = None) -> int:
        """
        Encodes a version string back into its integer representation.
        Supports both 3-part (major.minor.patch) and 4-part (major.minor.patch.build).
        """
        if sep is None:
            sep = NbVersionUtil.VERSION_SEPERATOR

        if not version or not version.strip():
            raise ValueError("version string is null or empty")

        parts = re.split(re.escape(sep), version.strip())

        if not (3 <= len(parts) <= 4):
            raise ValueError(f"invalid version format: {version}")

        encoded = 0
        for i, part in enumerate(parts):
            try:
                part_value = int(part)
            except ValueError:
                raise ValueError(f"invalid version component: {part}")

            if not (0 <= part_value <= 0xF):
                raise ValueError(f"version part out of range (0-15): {part_value}")

            shift = (len(parts) - 1 - i) * 4
            encoded |= (part_value & 0xF) << shift

        return encoded
