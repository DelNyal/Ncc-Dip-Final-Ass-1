def pack_values(value1, value2):
    # Ensure values are within the valid range (0-65535 for 16 bits)
    value1 = max(0, min(65535, value1))
    value2 = max(0, min(65535, value2))

    # Pack values into a 32-bit integer
    packed_int = (value1 << 16) | value2
    return packed_int


def unpack_values(packed_int):
    # Extract values from the packed integer
    value2 = packed_int & 0xFFFF  # Get the lower 16 bits
    value1 = (packed_int >> 16) & 0xFFFF  # Get the upper 16 bits

    return value1, value2


# Example usage:
value1 = 1  # Example value (16 bits)
value2 = 5  # Example value (16 bits)
print(f"{len(str(value1).encode('utf-8')) + len(str(value2).encode('utf-8'))}")
# Pack values into a single 32-bit integer
packed_data = pack_values(value1, value2)
print(f"Packed Integer: {packed_data}")  # Display the packed integer in binary

# Unpack values from the packed integer
unpacked_value1, unpacked_value2 = unpack_values(packed_data)
print(f"Unpacked Values: {unpacked_value1}, {unpacked_value2}")
