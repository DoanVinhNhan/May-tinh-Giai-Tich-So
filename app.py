from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
from numerical_methods.linear_algebra.direct_methods.gauss_elimination import solve_gauss_elimination
from numerical_methods.linear_algebra.direct_methods.gauss_jordan import solve_gauss_jordan
from numerical_methods.linear_algebra.direct_methods.lu_decomposition import solve_lu
from numerical_methods.linear_algebra.direct_methods.cholesky import solve_cholesky
from numerical_methods.linear_algebra.eigen.svd import calculate_svd
from numerical_methods.linear_algebra.eigen.danilevsky import danilevsky_algorithm

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
        # Đảm bảo luôn trả về JSON serializable
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        import traceback
        print("Lỗi khi xử lý request:", traceback.format_exc())
        return jsonify({"success": False, "error": f"Lỗi: {str(e)}"}), 500

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
        # Lấy method và các tham số power method nếu có
        method = data.get('method', 'default')
        num_singular = data.get('num_singular', None)
        num_iter = data.get('num_iter', 20)
        tol = data.get('tol', 1e-8)
        # Chuyển num_singular sang int nếu có
        if num_singular is not None:
            try:
                num_singular = int(num_singular)
            except Exception:
                num_singular = None
        # Gọi calculate_svd với method phù hợp
        if method == 'power':
            result = calculate_svd(matrix_a, method='power', num_singular=num_singular, num_iter=num_iter, tol=tol)
        else:
            result = calculate_svd(matrix_a, init_matrix=init_matrix) if init_matrix is not None else calculate_svd(matrix_a)
        result['success'] = True if 'error' not in result else False
        return jsonify(result)
    except Exception as e:
        import traceback
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
        result = danilevsky_algorithm(matrix_a)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)