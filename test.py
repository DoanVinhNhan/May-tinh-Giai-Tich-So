import numpy as np

#-------------------------------------------------------------------------------
# Mã nguồn thuật toán Danilevsky (Phiên bản sửa lỗi triệt để)
#-------------------------------------------------------------------------------

def danilevsky_algorithm(A):
    """
    Thực hiện thuật toán Danilevsky.
    Được cấu trúc lại thành 2 pha để đảm bảo tính chính xác.
    1. Pha biến đổi: Đưa ma trận về dạng chéo khối Frobenius.
    2. Pha trích xuất: Phân tích ma trận kết quả để tìm tất cả các giá trị riêng.
    """
    if A.shape[0] != A.shape[1]:
        raise ValueError("Ma trận đầu vào phải là ma trận vuông")

    n = A.shape[0]
    S = A.copy().astype(np.complex128)

    # --- PHA 1: BIẾN ĐỔI MA TRẬN ---
    m = n
    while m > 1:
        k = m - 1
        
        # Nếu phần tử mốc khác 0, thực hiện biến đổi
        if not np.isclose(S[k, k - 1], 0):
            M = np.eye(n, dtype=np.complex128)
            M[k - 1, :] = S[k, :]
            try:
                M_inv = np.linalg.inv(M)
                S = M_inv @ S @ M
            except np.linalg.LinAlgError:
                # Nếu không biến đổi được, coi như suy biến và bỏ qua
                # để pha trích xuất xử lý sau
                m = k 
                continue
            m = m - 1
            continue
        else:
            # Nếu phần tử mốc bằng 0, tìm cột để hoán vị
            s = -1
            for j in range(k - 1):
                if not np.isclose(S[k, j], 0):
                    s = j
                    break
            
            # Nếu tìm thấy cột để hoán vị, thực hiện và lặp lại
            if s != -1:
                C = np.eye(n, dtype=np.complex128)
                C[:, [s, k - 1]] = C[:, [k - 1, s]]
                S = C @ S @ C
                continue
            else:
                # Nếu không hoán vị được, đây là trường hợp suy biến
                # Giảm kích thước bài toán và để pha trích xuất xử lý
                m = k
                continue

    # --- PHA 2: TRÍCH XUẤT GIÁ TRỊ RIÊNG TỪ MA TRẬN KẾT QUẢ ---
    all_eigenvalues = []
    end_idx = n
    i = n - 1
    while i >= 0:
        # Một khối bắt đầu tại hàng `i`. Tìm xem nó kéo dài đến đâu.
        # Bên trong một khối Frobenius, các phần tử S[j, j-1] phải bằng 1.
        start_idx = i
        while start_idx > 0 and np.isclose(S[start_idx, start_idx - 1], 1.0):
            start_idx -= 1

        # Đã tìm thấy một khối từ [start_idx, end_idx)
        block = S[start_idx:end_idx, start_idx:end_idx]
        
        # Lấy đa thức đặc trưng từ hàng đầu của khối
        poly_coeffs = np.concatenate(([1.0], -block[0, :]))
        eigenvalues_block = np.roots(poly_coeffs)
        all_eigenvalues.extend(eigenvalues_block)
        
        # Di chuyển đến khối tiếp theo
        end_idx = start_idx
        i = start_idx - 1

    return sorted(all_eigenvalues, key=lambda x: (x.real, x.imag))


#-------------------------------------------------------------------------------
# Các ma trận để kiểm thử (giữ nguyên)
#-------------------------------------------------------------------------------

A1 = np.array([[0, 7, 6], [1, 0, 0], [0, 1, 0]])
A2 = np.array([[6, -2, -2], [-2, 5,  0], [-2,  0,  7]])
A3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
A4 = np.array([[3, 0, 0], [0, 1, 2], [0, -2, 1]])

test_cases = {
    "Case 1 (Lý tưởng - Ma trận Frobenius)": A1,
    "Case 2 (Tốt - Ma trận đối xứng)": A2,
    "Case 3 (Xấu - Ma trận suy biến của bạn)": A3,
    "Case 4 (Tổng quát - GTR phức)": A4,
}

#-------------------------------------------------------------------------------
# Chạy kiểm thử và in kết quả (giữ nguyên)
#-------------------------------------------------------------------------------

print("="*60)
print("BẮT ĐẦU KIỂM THỬ THUẬT TOÁN DANILEVSKY (PHIÊN BẢN CUỐI CÙNG)")
print("="*60)

for name, A in test_cases.items():
    print(f"\n--- {name} ---")
    print("Ma trận đầu vào A:")
    print(A)

    numpy_eigvals = sorted(np.linalg.eigvals(A), key=lambda x: (x.real, x.imag))
    danilevsky_eigvals = danilevsky_algorithm(A)

    print("\nKết quả so sánh giá trị riêng:")
    print(f"{'NumPy (Chuẩn)':<25} | {'Danilevsky (Của bạn)':<25}")
    print("-"*60)
    
    if len(danilevsky_eigvals) != len(numpy_eigvals):
         print(f"Lỗi: Danilevsky trả về {len(danilevsky_eigvals)} giá trị thay vì {len(numpy_eigvals)}")
    else:
        for i in range(len(numpy_eigvals)):
            np_val = numpy_eigvals[i]
            dn_val = danilevsky_eigvals[i]
            np_str = f"{np_val.real:.4f}{np_val.imag:+.4f}j" if abs(np_val.imag) > 1e-9 else f"{np_val.real:.4f}"
            dn_str = f"{dn_val.real:.4f}{dn_val.imag:+.4f}j" if abs(dn_val.imag) > 1e-9 else f"{dn_val.real:.4f}"
            print(f"{np_str:<25} | {dn_str:<25}")

    print("-"*60)