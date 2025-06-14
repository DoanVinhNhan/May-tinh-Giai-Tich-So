# May-tinh-Giai-Tich-So/numerical_methods/root_finding/polynomial_root_finding.py
import numpy as np

# Thêm hàm này vào đầu file
# Thay thế hàm _format_poly_str cũ bằng hàm này
def _format_poly_str(coeffs):
    """Tạo một chuỗi đa thức ở định dạng LaTeX từ danh sách các hệ số."""
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        if np.isclose(c, 0):
            continue
        
        power = degree - i
        
        # Xử lý hệ số và dấu
        sign = " - " if c < 0 else " + "
        c_abs = abs(c)
        
        # Bỏ qua hệ số 1 (trừ khi là hằng số)
        if np.isclose(c_abs, 1) and power != 0:
            coeff_str = ""
        else:
            coeff_str = f"{c_abs:g}"

        # Xử lý biến và số mũ
        if power > 1:
            var_str = f"x^{{{power}}}"
        elif power == 1:
            var_str = "x"
        else: # power == 0
            var_str = ""
        
        # Ghép nối thành phần
        term = f"{coeff_str}{var_str}"

        if i == 0:
            terms.append(f"-{term}" if sign.strip() == "-" else term)
        else:
            terms.append(f"{sign}{term}")
            
    # Nối các số hạng và dọn dẹp
    poly_str = " ".join(terms).lstrip(' +')
    return poly_str if poly_str else "0"

def _find_root_bounds(coeffs):
    """
    Tìm khoảng chứa nghiệm thực dựa trên các hệ số.
    Thuật toán này dựa trên phương pháp của Lagrange.
    Đây là phiên bản Python của hàm timmiennghiem trong file giaiptdt.cpp. 
    """
    if not coeffs or coeffs[0] == 0:
        return None, None

    # Tìm cận trên cho nghiệm dương (N1)
    a = np.array(coeffs, dtype=float)
    a[0] = np.abs(a[0])
    
    first_neg_idx = -1
    for i, c in enumerate(a):
        if c < 0:
            first_neg_idx = i
            break
    
    N1 = 0
    if first_neg_idx != -1:
        max_abs_neg = np.max(np.abs(a[first_neg_idx:]))
        N1 = 1 + (max_abs_neg / a[0])**(1/first_neg_idx)
    
    # Tìm cận dưới cho nghiệm âm (-N2)
    # Bằng cách tìm cận trên cho P(-x)
    b = a.copy()
    for i in range(1, len(b)):
        if i % 2 != 0:
            b[i] = -b[i] # P(-x)
            
    first_neg_idx_b = -1
    for i, c in enumerate(b):
        if c < 0:
            first_neg_idx_b = i
            break
            
    N2 = 0
    if first_neg_idx_b != -1:
        max_abs_neg_b = np.max(np.abs(b[first_neg_idx_b:]))
        N2 = 1 + (max_abs_neg_b / b[0])**(1/first_neg_idx_b)

    return -N2, N1

def _bisection(p, a, b, tol=1e-7, max_iter=100):
    """Hàm chia đôi nội bộ để tìm nghiệm trong khoảng [a, b]."""
    fa = p(a)
    steps = []
    
    if fa * p(b) >= 0:
        return None, []

    for i in range(max_iter):
        c = (a + b) / 2.0
        fc = p(c)
        steps.append({'k': i, 'a': a, 'b': b, 'c': c, 'f(c)': fc})
        
        if abs(b - a) / 2.0 < tol or fc == 0:
            return c, steps
        
        if fa * fc < 0:
            b = c
        else:
            a = c
            fa = fc
            
    return (a + b) / 2.0, steps


def solve_polynomial(coeffs, tol=1e-7):
    """
    Giải phương trình đa thức và trả về các bước trung gian.
    """
    try:
        if len(coeffs) < 2:
            return {"success": False, "error": "Đa thức phải có bậc ít nhất là 1."}

        p = np.poly1d(coeffs)
        p_deriv = p.deriv()

        # Bước 1: Tìm khoảng chứa nghiệm tổng quát
        lower_bound, upper_bound = _find_root_bounds(coeffs)
        if lower_bound is None:
             return {"success": False, "error": "Hệ số đầu tiên không được bằng 0."}

        # Bước 2: Phân ly nghiệm bằng cách tìm các điểm cực trị
        # Nghiệm của đạo hàm là các điểm cực trị
        critical_points = p_deriv.r
        real_critical_points = sorted([cp.real for cp in critical_points if np.isclose(cp.imag, 0)])

        # Tạo các khoảng kiểm tra từ cận và các điểm cực trị
        search_points = sorted(list(set([lower_bound] + real_critical_points + [upper_bound])))
        
        intervals = []
        for i in range(len(search_points) - 1):
            intervals.append((search_points[i], search_points[i+1]))

        # Bước 3: Tìm nghiệm trong từng khoảng nhỏ
        found_roots = []
        for a, b in intervals:
            # Thêm một khoảng đệm nhỏ để tránh bỏ sót nghiệm tại điểm cực trị
            a_check = a - tol
            b_check = b + tol
            
            if p(a_check) * p(b_check) < 0:
                root, bisection_steps = _bisection(p, a_check, b_check, tol)
                if root is not None:
                    # Kiểm tra để tránh thêm nghiệm trùng lặp
                    is_duplicate = False
                    for existing_root in found_roots:
                        if np.isclose(root, existing_root['root_value']):
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        found_roots.append({
                            "root_value": root,
                            "interval": [a, b],
                            "bisection_steps": bisection_steps
                        })
        
        return {
            "success": True,
            "polynomial_str": _format_poly_str(coeffs),
            "bounds": [lower_bound, upper_bound],
            "critical_points": real_critical_points,
            "search_intervals": intervals,
            "found_roots": found_roots
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": f"Lỗi không xác định: {traceback.format_exc()}"}