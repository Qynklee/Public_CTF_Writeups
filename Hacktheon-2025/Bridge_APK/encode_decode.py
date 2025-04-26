def calculate_adjustments(key):
    # Tính tổng các byte trong key, giới hạn 23 byte như trong mã
    total_sum = sum(key[:23])
    mod = total_sum % 25
    v33 = mod + 1  # Cho ký tự thông thường (mã hóa)
    v34 = mod + 34  # Cho ký tự đặc biệt (mã hóa)
    v21 = -(mod + 1)  # Phủ định của v33 (giải mã)
    v26 = mod + 34  # Giống v34 (giải mã)
    return v33, v34, v21, v26

def encode(input_bytes):
    # Chuỗi cố định byte_5E9A
    key = b"bridge_default_key_2025"
    v33, v34, _, _ = calculate_adjustments(key)
    
    output = []
    for c in input_bytes:
        c_prime = c
        if c >= 0x21 and c != 0x7F:  # Ký tự thông thường
            c_prime = c + v33
            if c_prime > 0x7E:
                c_prime -= 94
        else:  # Ký tự đặc biệt
            tmp = c - 94 if c >= 0x5E else c
            c_prime = tmp + v34
            if c_prime >= 0x7F:
                c_prime -= 94
        
        if c_prime >= 0:
            output.append(c_prime & 0xFF)
        else:
            # Mã hóa thành 2 byte
            encoded = (c_prime >> 6) + ((c_prime & 0x3F) << 8) - 32576
            output.append(encoded & 0xFF)
            output.append((encoded >> 8) & 0xFF)
    
    # Đặt trạng thái thành công (tương tự a1[0] = 2)
    return bytes([2] + output)

def decode(input_bytes):
    # Bỏ qua byte trạng thái (input_bytes[0] = 2)
    if not input_bytes or input_bytes[0] != 2:
        return b""
    
    key = b"bridge_default_key_2025"
    _, _, v21, v26 = calculate_adjustments(key)
    
    output = []
    i = 1  # Bỏ qua byte trạng thái
    while i < len(input_bytes):
        c = input_bytes[i]
        if c < 0x21 or c == 0x7F:
            return b""  # Không hỗ trợ ký tự đặc biệt
        
        c_prime = c
        if c < v26:
            c_prime = c + 94
        
        c_prime += v21
        if c_prime < 0:
            if i + 1 >= len(input_bytes):
                return b""
            # Xử lý 2-byte
            encoded = (input_bytes[i] | (input_bytes[i + 1] << 8)) + 32576
            c_prime = ((encoded & 0x3F) << 6) | (encoded >> 8)
            i += 2
        else:
            i += 1
        
        output.append(c_prime & 0xFF)
    
    return bytes(output)

# Ví dụ sử dụng
if __name__ == "__main__":
    # Dữ liệu thử nghiệm
    input_data = b"Hello, World!"
    print("Input:", input_data)
    
    encoded = encode(input_data)
    print("Encoded:", encoded[1:])  # Bỏ byte trạng thái
    
    decoded = decode(encoded)
    print("Decoded:", decoded)