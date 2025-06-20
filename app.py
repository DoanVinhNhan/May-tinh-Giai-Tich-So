from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import traceback

# --- Import các phương thức của Máy tính ma trận ---
from numerical_methods.linear_algebra.direct_methods.gauss_elimination import solve_gauss_elimination
from numerical_methods.linear_algebra.direct_methods.gauss_jordan import solve_gauss_jordan
from numerical_methods.linear_algebra.direct_methods.lu_decomposition import solve_lu
from numerical_methods.linear_algebra.direct_methods.cholesky import solve_cholesky
from numerical_methods.linear_algebra.eigen.svd import calculate_svd
from numerical_methods.linear_algebra.eigen.danilevsky import danilevsky_algorithm

# --- START: IMPORT MỚI CHO TÍNH NGHỊCH ĐẢO ---
from numerical_methods.linear_algebra.inverse.gauss_jordan_inverse import solve_inverse_gauss_jordan
from numerical_methods.linear_algebra.inverse.lu_inverse import solve_inverse_lu
from numerical_methods.linear_algebra.inverse.cholesky_inverse import solve_inverse_cholesky
from numerical_methods.linear_algebra.inverse.bordering import solve_inverse_bordering
from numerical_methods.linear_algebra.inverse.jacobi_inverse import solve_inverse_jacobi
from numerical_methods.linear_algebra.inverse.newton_inverse import solve_inverse_newton
from numerical_methods.linear_algebra.inverse.gauss_seidel_inverse import solve_inverse_gauss_seidel

# --- END: IMPORT MỚI ---

# --- Import các phương thức của Giải phương trình f(x)=0 ---
from utils.expression_parser import parse_expression, parse_phi_expression
from numerical_methods.root_finding.bisection import solve_bisection
from numerical_methods.root_finding.secant import solve_secant
from numerical_methods.root_finding.newton import solve_newton
from numerical_methods.root_finding.simple_iteration import solve_simple_iteration
from utils.expression_parser import get_derivative

from numerical_methods.nonlinear_systems.newton import solve_newton_system
from numerical_methods.nonlinear_systems.newton_modified import solve_newton_modified_system
from numerical_methods.nonlinear_systems.simple_iteration import solve_simple_iteration_system

from numerical_methods.linear_algebra.iterative_methods.jacobi import solve_jacobi
from numerical_methods.linear_algebra.iterative_methods.gauss_seidel import solve_gauss_seidel

from numerical_methods.root_finding.polynomial_root_finding import solve_polynomial

from numerical_methods.linear_algebra.eigen.power_method import power_iteration_deflation, power_method_single
from numerical_methods.linear_algebra.iterative_methods.simple_iteration import solve_simple_iteration as solve_simple_iteration_hpt



app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

def hpt_solver(solver_function):
    data = request.get_json()
    if not data or 'matrix_a' not in data or 'matrix_b' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A hoặc B."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        matrix_b = np.array(data['matrix_b'], dtype=float)
        result = solver_function(matrix_a, matrix_b)
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý request HPT:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

def iterative_hpt_solver(solver_function):
    data = request.get_json()
    if not data or 'matrix_a' not in data or 'matrix_b' not in data or 'x0' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A, B hoặc vector X₀."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        matrix_b = np.array(data['matrix_b'], dtype=float)
        x0 = np.array(data['x0'], dtype=float)
        
        eps = float(data.get('tolerance', 1e-5))
        max_iter = int(data.get('max_iter', 100))
            
        result = solver_function(matrix_a, matrix_b, x0, eps=eps, max_iter=max_iter)
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý request HPT lặp:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500
    
# --- START: HELPER MỚI CHO TÍNH NGHỊCH ĐẢO ---
def inverse_solver(solver_function):
    data = request.get_json()
    if not data or 'matrix_a' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        
        # Lấy các tham số bổ sung (cho phương pháp lặp)
        params = {}
        if 'tolerance' in data:
            params['eps'] = float(data['tolerance'])
        if 'max_iter' in data:
            params['max_iter'] = int(data['max_iter'])
        if 'x0_method' in data:
            params['x0_method'] = data['x0_method']
            
        result = solver_function(matrix_a, **params)
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý request nghịch đảo:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500
# --- END: HELPER MỚI ---
def iterative_hpt_solver_simple_iteration(solver_function):
    data = request.get_json()
    if not data or 'matrix_b' not in data or 'matrix_d' not in data or 'x0' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận B, d hoặc vector X₀."}), 400
    try:
        matrix_B = np.array(data['matrix_b'], dtype=float)
        matrix_d = np.array(data['matrix_d'], dtype=float)
        x0 = np.array(data['x0'], dtype=float)
        
        eps = float(data.get('tolerance', 1e-5))
        max_iter = int(data.get('max_iter', 100))
        # START: LẤY LỰA CHỌN CHUẨN TỪ REQUEST
        norm_choice = data.get('norm_choice', 'inf') 
        # END: LẤY LỰA CHỌN
            
        # START: TRUYỀN LỰA CHỌN VÀO HÀM SOLVER
        result = solver_function(matrix_B, matrix_d, x0, eps=eps, max_iter=max_iter, norm_choice=norm_choice)
        # END: TRUYỀN LỰA CHỌN
        
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý request HPT lặp đơn:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500


@app.route('/matrix/iterative/jacobi', methods=['POST'])
def handle_iterative_jacobi():
    return iterative_hpt_solver(solve_jacobi)

@app.route('/matrix/iterative/gauss-seidel', methods=['POST'])
def handle_iterative_gauss_seidel():
    return iterative_hpt_solver(solve_gauss_seidel)

@app.route('/matrix/svd', methods=['POST'])
def handle_svd_calculation():
    data = request.get_json()
    if not data or 'matrix_a' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A."}), 400
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        init_matrix = None
        if 'init_matrix' in data and data['init_matrix']:
            init_matrix = np.array(data['init_matrix'], dtype=float)
        method = data.get('method', 'default')
        num_singular = data.get('num_singular', None)
        num_iter = data.get('num_iter', 20)
        tol = data.get('tol', 1e-8)
        if num_singular is not None:
            try:
                num_singular = int(num_singular)
            except Exception:
                num_singular = None
        if method == 'power':
            result = calculate_svd(matrix_a, method='power', num_singular=num_singular, num_iter=num_iter, tol=tol)
        else:
            result = calculate_svd(matrix_a, init_matrix=init_matrix) if init_matrix is not None else calculate_svd(matrix_a)
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý SVD:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

@app.route('/matrix/gauss-jordan', methods=['POST'])
def handle_gauss_jordan_calculation():
    return hpt_solver(solve_gauss_jordan)

@app.route('/matrix/gauss-elimination', methods=['POST'])
def handle_gauss_elimination_calculation():
    return hpt_solver(solve_gauss_elimination)

@app.route('/matrix/lu-decomposition', methods=['POST'])
def handle_lu_decomposition_calculation():
    return hpt_solver(solve_lu)

@app.route('/matrix/cholesky', methods=['POST'])
def handle_cholesky_calculation():
    return hpt_solver(solve_cholesky)

@app.route('/matrix/danilevsky', methods=['POST'])
def handle_danilevsky():
    data = request.get_json()
    matrix_a = np.array(data.get('matrix_a'))
    try:
        eigen_results = danilevsky_algorithm(matrix_a)
        # Sửa lỗi: Đảm bảo kết quả luôn là một dictionary và có success flag
        if isinstance(eigen_results, dict):
            eigen_results['success'] = True
            return jsonify(eigen_results)
        else: # Trường hợp hàm cũ trả về list hoặc tuple
            return jsonify({'success': True, 'data': eigen_results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# --- START: CÁC ENDPOINT MỚI CHO TÍNH NGHỊCH ĐẢO ---
@app.route('/matrix/inverse/gauss-jordan', methods=['POST'])
def handle_inverse_gauss_jordan():
    return inverse_solver(solve_inverse_gauss_jordan)

@app.route('/matrix/iterative/simple-iteration', methods=['POST'])
def handle_iterative_simple_iteration():
    return iterative_hpt_solver_simple_iteration(solve_simple_iteration_hpt)

@app.route('/matrix/inverse/lu', methods=['POST'])
def handle_inverse_lu():
    return inverse_solver(solve_inverse_lu)

@app.route('/matrix/inverse/cholesky', methods=['POST'])
def handle_inverse_cholesky():
    return inverse_solver(solve_inverse_cholesky)

@app.route('/matrix/inverse/bordering', methods=['POST'])
def handle_inverse_bordering():
    return inverse_solver(solve_inverse_bordering)

@app.route('/matrix/inverse/jacobi', methods=['POST'])
def handle_inverse_jacobi():
    return inverse_solver(solve_inverse_jacobi)

@app.route('/matrix/inverse/newton', methods=['POST'])
def handle_inverse_newton():
    return inverse_solver(solve_inverse_newton)

@app.route('/matrix/inverse/gauss-seidel', methods=['POST'])
def handle_inverse_gauss_seidel():
    return inverse_solver(solve_inverse_gauss_seidel)
# --- END: CÁC ENDPOINT MỚI ---

@app.route('/nonlinear-equation/solve', methods=['POST'])
def solve_nonlinear_equation():
    data = request.get_json()
    method = data.get('method')
    expression_str = data.get('expression')
    
    try:
        a = float(data['interval_a'])
        b = float(data['interval_b'])
        stop_value_str = data.get('value')
        mode = data.get('mode', 'absolute_error')
        stop_condition = data.get('stop_condition') # Dùng cho Newton, Secant

        if not stop_value_str:
            return jsonify({'success': False, 'error': 'Vui lòng nhập giá trị cho điều kiện dừng.'})
        
        stop_value = float(stop_value_str)

        if method == 'simple_iteration':
            # Phương pháp lặp đơn không dùng stop_condition
            x0_str = data.get('x0')
            if x0_str is None or x0_str == '':
                return jsonify({'success': False, 'error': 'Vui lòng nhập điểm bắt đầu x₀.'})
            x0 = float(x0_str)
            # Truyền mode và value trực tiếp
            result = solve_simple_iteration(expression_str, a, b, x0, mode, stop_value)
        else:
            # Các phương pháp khác
            if method == 'bisection':
                parsed_result = parse_expression(expression_str)
                if not parsed_result.get('success'): return jsonify(parsed_result)
                f = parsed_result.get('f')
                result = solve_bisection(f, a, b, mode, stop_value)
            elif method == 'newton':
                parsed_result = parse_expression(expression_str)
                if not parsed_result.get('success'): return jsonify(parsed_result)
                result = solve_newton(expression_str, a, b, mode, stop_value, stop_condition)
            elif method == 'secant':
                parsed_result = parse_expression(expression_str)
                if not parsed_result.get('success'): return jsonify(parsed_result)
                result = solve_secant(parsed_result, a, b, mode, stop_value, stop_condition)
            else:
                return jsonify({'success': False, 'error': 'Phương pháp không hợp lệ.'})
        
        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': f'Dữ liệu đầu vào không hợp lệ: {e}. Vui lòng kiểm tra lại các con số.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Đã xảy ra lỗi không xác định: {e}'})

@app.route('/nonlinear-system/solve', methods=['POST'])
def solve_nonlinear_system():
    data = request.get_json()
    try:
        method = data.get('method')
        n = int(data.get('n'))
        expressions = data.get('expressions') # list of strings
        x0 = [float(x) for x in data.get('x0')] # list of numbers
        stop_option = data.get('stop_option') # 'absolute_error', 'relative_error', 'iterations'
        stop_value = float(data.get('stop_value'))

        if stop_option == 'iterations':
            stop_value = int(stop_value)

        result = {}
        if method == 'newton':
            result = solve_newton_system(n, expressions, x0, stop_option, stop_value)
        elif method == 'newton_modified':
            result = solve_newton_modified_system(n, expressions, x0, stop_option, stop_value)
        elif method == 'simple_iteration':
            a0 = [float(a) for a in data.get('a0')]
            b0 = [float(b) for b in data.get('b0')]
            result = solve_simple_iteration_system(n, expressions, x0, a0, b0, stop_option, stop_value)
        else:
            return jsonify({"success": False, "error": "Phương pháp không hợp lệ."}), 400

        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': f'Dữ liệu đầu vào không hợp lệ: {e}. Vui lòng kiểm tra lại các con số.'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Đã xảy ra lỗi không xác định: {e}'}), 500

@app.route('/polynomial/solve', methods=['POST'])
def handle_polynomial_solve():
    data = request.get_json()
    if not data or 'coeffs' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu các hệ số."}), 400
    try:
        coeffs = [float(c) for c in data['coeffs']]
        # Lấy tolerance và max_iter từ request, nếu không có thì dùng giá trị mặc định
        tolerance = data.get('tolerance', 1e-7)
        max_iter = data.get('max_iter', 100)

        result = solve_polynomial(coeffs, tol=tolerance, max_iter=max_iter)
        return jsonify(result)
    except Exception as e:
        import traceback
        print("Lỗi khi xử lý request giải đa thức:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

@app.route('/matrix/eigen/power-single', methods=['POST'])
def handle_power_single():
    data = request.get_json()
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        tolerance = float(data.get('tolerance', 1e-6))
        max_iter = int(data.get('max_iter', 100))
        
        # THAY ĐỔI: Gọi hàm power_method_single thay vì power_iteration_deflation
        result = power_method_single(matrix_a, tol=tolerance, max_iter=max_iter)
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý PP Lũy thừa (đơn):", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500
# END: ENDPOINT MỚI

# START: ENDPOINT MỚI CHO PP LŨY THỪA & XUỐNG THANG (NHIỀU GTR)
@app.route('/matrix/eigen/power-deflation', methods=['POST'])
def handle_power_deflation():
    data = request.get_json()
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        num_eigen = int(data.get('num_eigen', 1))
        tolerance = float(data.get('tolerance', 1e-6))
        max_iter = int(data.get('max_iter', 100))
        
        result = power_iteration_deflation(matrix_a, num_values=num_eigen, tol=tolerance, max_iter=max_iter)
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý PP Lũy thừa & Xuống thang:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

@app.route('/matrix/svd_approximation', methods=['POST'])
def handle_svd_approximation():
    data = request.get_json()
    if not data or 'matrix_a' not in data:
        return jsonify({"success": False, "error": "Dữ liệu không hợp lệ: Thiếu ma trận A."}), 400
    
    try:
        matrix_a = np.array(data['matrix_a'], dtype=float)
        approximation_method = data.get('approximation_method', 'rank-k')
        
        # Import hàm xấp xỉ SVD (sẽ tạo sau)
        from numerical_methods.linear_algebra.eigen.svd import calculate_svd_approximation
        
        # Tham số cho các phương pháp khác nhau
        if approximation_method == 'rank-k':
            k = data.get('k', 2)
            result = calculate_svd_approximation(matrix_a, method='rank-k', k=k)
        elif approximation_method == 'threshold':
            threshold = data.get('threshold', 1e-10)
            result = calculate_svd_approximation(matrix_a, method='threshold', threshold=threshold)
        elif approximation_method == 'error-bound':
            error_bound = data.get('error_bound', 0.1)
            result = calculate_svd_approximation(matrix_a, method='error-bound', error_bound=error_bound)
        else:
            return jsonify({"success": False, "error": "Phương pháp xấp xỉ không hợp lệ."}), 400
        
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    
    except Exception as e:
        print("Lỗi khi xử lý SVD approximation:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)