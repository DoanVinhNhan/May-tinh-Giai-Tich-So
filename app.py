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
# --- END: CÁC ENDPOINT MỚI ---

@app.route('/nonlinear-equation/solve', methods=['POST'])
def solve_nonlinear_equation():
    data = request.get_json()
    method = data.get('method')
    expression_str = data.get('expression')
    
    try:
        a = float(data['interval_a'])
        b = float(data['interval_b'])
        stop_value = data.get('value')
        mode = data.get('mode', 'absolute_error')
        stop_condition = data.get('stop_condition')

        if method == 'simple_iteration':
            parsed_result = parse_phi_expression(expression_str)
        else:
            parsed_result = parse_expression(expression_str)

        if not parsed_result.get('success'):
            return jsonify({'success': False, 'error': parsed_result.get('error', 'Lỗi phân tích biểu thức.')})

        f = parsed_result.get('f')
        if method == 'simple_iteration':
            phi = parsed_result.get('phi')

        if method in ['bisection', 'newton', 'secant']:
            try:
                fa = f(a)
                fb = f(b)
                if fa * fb >= 0 and method == 'bisection':
                    return jsonify({'success': False, 'error': f'Khoảng [{a}, {b}] không phải là khoảng cách ly nghiệm vì f(a)={fa:.4f} và f(b)={fb:.4f} không trái dấu.'})
            except (ValueError, TypeError) as e:
                 return jsonify({'success': False, 'error': f'Không thể tính giá trị hàm tại điểm a={a} hoặc b={b}. Lỗi: {e}'})
        
        try:
            if mode == 'iterations':
                N = int(float(stop_value))
                tol = 1e-6 
            else:
                tol = float(stop_value)
                N = 200
        except (ValueError, TypeError):
             return jsonify({'success': False, 'error': 'Giá trị điều kiện dừng phải là một con số.'})

        if method == 'bisection':
            result = solve_bisection(f, a, b, mode, stop_value)
        elif method == 'newton':
            result = solve_newton(expression_str, a, b, tol, N, mode, stop_condition)
        elif method == 'secant':
            result = solve_secant(parsed_result, a, b, mode, tol, stop_condition)
        elif method == 'simple_iteration':
            x0_str = data.get('x0')
            if x0_str is None or x0_str == '':
                return jsonify({'success': False, 'error': 'Vui lòng nhập điểm bắt đầu x₀.'})
            x0 = float(x0_str)
            result = solve_simple_iteration(expression_str, a, b, x0, tol, N, mode)
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
        result = solve_polynomial(coeffs)
        return jsonify(result)
    except Exception as e:
        print("Lỗi khi xử lý request giải đa thức:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)