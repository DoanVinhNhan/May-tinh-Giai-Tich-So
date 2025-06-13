import numpy as np
import os
import sys

# Thêm đường dẫn của dự án vào sys.path để có thể import các module
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import hàm giải thuật Lặp đơn
try:
    from numerical_methods.nonlinear_systems.simple_iteration import solve_simple_iteration_system
except ImportError as e:
    print("!!! LỖI QUAN TRỌNG: Không thể import module solve_simple_iteration_system. !!!")
    print(f"Lỗi chi tiết: {e}")
    sys.exit(1)

# --- Định nghĩa bài toán kiểm thử HỘI TỤ ---

# Dạng lặp X = φ(X) đã được biến đổi để đảm bảo hội tụ
expressions_phi_convergent = [
    "(13 + x2) / 4",
    "(5 + x1) / 4"
]

# Các tham số
initial_guess = [0.0, 0.0]  # Bắt đầu từ [0, 0]
tolerance = 1e-7
stop_mode = "absolute_error"
max_iter = 50

# Miền D để kiểm tra điều kiện hội tụ.
# Nghiệm là (3.8, 2.2) nên ta có thể chọn miền D rộng hơn, ví dụ [0, 5] x [0, 5]
domain_a = [0.0, 0.0]
domain_b = [5.0, 5.0]


# --- Hàm hỗ trợ in kết quả ---
def print_results(method_name, result):
    print("\n" + "="*20 + f" Kết quả cho: {method_name} " + "="*20)
    if result and result.get("success"):
        solution = result.get("solution")
        iterations = result.get("iterations")
        contraction_factor = result.get("contraction_factor_K")
        solution_np = np.array(solution)
        
        print(f"Trạng thái: THÀNH CÔNG")
        print(f"Hệ số co K ≈ {contraction_factor:.4f} (K < 1 là điều kiện tốt).")
        print(f"Hội tụ sau {iterations} vòng lặp.")
        print(f"Nghiệm tìm được X ≈ {solution_np}")
    elif result and not result.get("success"):
        print(f"Trạng thái: THẤT BẠI")
        print(f"Lỗi: {result.get('error', 'Không có thông tin lỗi.')}")
    else:
        print("Trạng thái: LỖI - Thuật toán không trả về kết quả.")
    print("=" * (44 + len(method_name)))


# --- Bắt đầu kiểm thử ---
print("--- Đang kiểm thử phương pháp Lặp đơn với bài toán hội tụ ---")
try:
    simple_iter_result = solve_simple_iteration_system(
        n=2,
        expr_list=expressions_phi_convergent,
        x0_list=initial_guess,
        a0_list=domain_a,
        b0_list=domain_b,
        stop_option=stop_mode,
        stop_value=tolerance
    )
    print_results("Lặp đơn (Hội tụ)", simple_iter_result)
except Exception as e:
    import traceback
    print(f"Đã xảy ra lỗi khi chạy Lặp đơn: {e}\n{traceback.format_exc()}")