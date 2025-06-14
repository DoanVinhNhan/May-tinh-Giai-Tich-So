import unittest
import numpy as np
import sympy as sp

# =================================================================================
# ===                  IMPORT CÁC HÀM THUẬT TOÁN CỐT LÕI                       ===
# ===    (Bỏ qua các hàm wrapper `solve_...`, kiểm thử trực tiếp logic)         ===
# =================================================================================

from numerical_methods.root_finding.bisection import bisection
from numerical_methods.root_finding.newton import newton
from numerical_methods.root_finding.simple_iteration import simple_iteration
from numerical_methods.linear_algebra.direct_methods.gauss_elimination import gauss_elimination
from numerical_methods.linear_algebra.direct_methods.gauss_jordan import gauss_jordan
from numerical_methods.linear_algebra.inverse.gauss_jordan_inverse import gauss_jordan_inverse
from numerical_methods.nonlinear_systems.newton import newton_system
from numerical_methods.nonlinear_systems.simple_iteration import simple_iteration_system

class ComprehensiveTestNumericalMethods(unittest.TestCase):
    """
    Bộ kiểm thử toàn diện, kiểm tra trực tiếp các hàm logic thuật toán cốt lõi.
    """

    def assertMatricesAlmostEqual(self, A, B, places=6, msg=None):
        self.assertIsNotNone(A, msg=f"Hàm trả về None. {msg or ''}")
        self.assertEqual(np.shape(A), np.shape(B), msg=f"Kích thước không khớp: {np.shape(A)} vs {np.shape(B)}. {msg or ''}")
        np.testing.assert_almost_equal(A, B, decimal=places, err_msg=msg)

    # ===============================================
    # ===      1. TEST: PHƯƠNG PHÁP CHIA ĐÔI       ===
    # ===============================================
    def test_bisection_case_1(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 5"""
        f = lambda x: np.e**x - np.cos(2*x)
        root, _ = bisection(f, -2, 0, tol=1e-8)
        self.assertAlmostEqual(f(root), 0, places=7)

    def test_bisection_case_2(self):
        """Nguồn: BaitapGTS tuần 1_3.pdf, Câu 6"""
        f = lambda x: x**5 - 3*x**3 + 2*x**2 - x + 5
        root, _ = bisection(f, -3, -1.5, tol=1e-8)
        self.assertAlmostEqual(f(root), 0, places=7)

    def test_bisection_case_3(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 13a"""
        f = lambda x: x**3 + 3*x**2 - 1
        root, _ = bisection(f, 0.5, 0.6, tol=1e-8)
        self.assertAlmostEqual(f(root), 0, places=7)

    def test_bisection_case_4(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 13b"""
        f = lambda x: x**2 + 4*np.sin(x) - 1
        root, _ = bisection(f, 0.2, 0.3, tol=1e-8)
        self.assertAlmostEqual(f(root), 0, places=7)
        
    def test_bisection_case_5(self):
        """Nguồn: BaitapGTS tuần 1_3.pdf, Câu 11c"""
        f = lambda x: np.e**(-x) - x
        root, _ = bisection(f, 0.5, 0.6, tol=1e-8)
        self.assertAlmostEqual(f(root), 0, places=7)

    # ===============================================
    # ===       2. TEST: PHƯƠNG PHÁP NEWTON         ===
    # ===============================================
    def test_newton_case_1(self):
        """Nguồn: đề thi collection_Giữa kỳ - GTS.pdf, 20182, ĐỀ I, Câu 1"""
        x_sym = sp.symbols('x')
        f_sym = sp.log(x_sym) - 1
        root, _ = newton(f_sym, 2.5, tol=1e-9)
        self.assertAlmostEqual(root, np.e, places=8)

    def test_newton_case_2(self):
        """Nguồn: đề thi collection_Giữa kỳ - GTS.pdf, 20232, Câu 1 (k=10)"""
        x_sym = sp.symbols('x')
        f_sym = x_sym**6 - 42 
        root, _ = newton(f_sym, 1.8, tol=1e-9)
        self.assertAlmostEqual(root**6, 42, places=8)

    def test_newton_case_3(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 54"""
        x_sym = sp.symbols('x')
        f_sym = sp.exp(x_sym) - sp.cos(2*x_sym)
        root, _ = newton(f_sym, -0.5, tol=1e-9)
        self.assertAlmostEqual(np.e**root, np.cos(2*root), places=8)
        
    def test_newton_case_4(self):
        """Nguồn: BaitapGTS tuần 1_3.pdf, Câu 11b"""
        x_sym = sp.symbols('x')
        f_sym = 2**x_sym - 5*x_sym + sp.sin(x_sym)
        root, _ = newton(f_sym, 0.2, tol=1e-9)
        self.assertAlmostEqual(2**root + np.sin(root), 5*root, places=8)
        
    def test_newton_case_5(self):
        """Nguồn: BaitapGTS tuần 1_3.pdf, Câu 11a"""
        x_sym = sp.symbols('x')
        f_sym = x_sym**5 - 3*x_sym**3 + 2*x_sym**2 - x_sym + 5
        root, _ = newton(f_sym, -2.0, tol=1e-9)
        self.assertAlmostEqual(float(f_sym.subs(x_sym, root)), 0, places=7)

    # ===============================================
    # ===      3. TEST: PHƯƠNG PHÁP LẶP ĐƠN         ===
    # ===============================================
    def test_simple_iteration_case_1(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 13a"""
        phi = lambda x: 1 / np.sqrt(x + 3)
        root, _ = simple_iteration(phi, 0.5, tol=1e-9)
        self.assertAlmostEqual(root, phi(root), places=8)

    def test_simple_iteration_case_2(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 56c"""
        phi = lambda x: np.exp(-x)
        root, _ = simple_iteration(phi, 0.5, tol=1e-9)
        self.assertAlmostEqual(root, phi(root), places=8)

    def test_simple_iteration_case_3(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 13b"""
        phi = lambda x: np.arcsin((1 - x**2) / 4)
        root, _ = simple_iteration(phi, 0.2, tol=1e-9)
        self.assertAlmostEqual(root, phi(root), places=8)
        
    def test_simple_iteration_case_4(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 13c"""
        phi = lambda x: 1.4**x
        root, _ = simple_iteration(phi, 1.2, tol=1e-9)
        self.assertAlmostEqual(root, phi(root), places=8)
        
    def test_simple_iteration_case_5(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 13d"""
        phi = lambda x: (np.e**x + 7) / 10
        root, _ = simple_iteration(phi, 1.0, tol=1e-9)
        self.assertAlmostEqual(root, phi(root), places=8)

    # ===============================================
    # ===      4. TEST: GIẢI HỆ TUYẾN TÍNH         ===
    # ===============================================
    def run_linear_system_solvers(self, A, b, places=5):
        x_ref = np.linalg.solve(A, b)
        
        x_gauss, _ = gauss_elimination(A.copy(), b.copy())
        self.assertMatricesAlmostEqual(x_gauss, x_ref, places=places, msg="Gauss Elimination")
        
        x_gj, _ = gauss_jordan(A.copy(), b.copy())
        self.assertMatricesAlmostEqual(x_gj, x_ref, places=places, msg="Gauss Jordan")

    def test_linear_system_case_1(self):
        """Nguồn: đề thi collection_Giữa kỳ - GTS.pdf, 20182, ĐỀ I, Câu 2"""
        A = np.array([
            [20.5, 1.7, -3.2, 2.1, 9.23, -3.52], [2.5, 37.1, 5.2, 2.8, 7.23, -5.52],
            [11.3, 2.7, -38.2, 4.1, -7.58, 4.25], [8.4, -4.6, -6.5, 52.1, 1.43, 15.26],
            [42.7, -36.9, -42.7, 61.1, 2.43, -35.26], [19.2, -1, 35, -2, 14.73, 5.64]
        ])
        b = np.array([21.41, 27.11, 14.17, 52.49, 56.72, 18.57])
        self.run_linear_system_solvers(A, b)

    def test_linear_system_case_2(self):
        """Nguồn: đề thi collection_Cuối kỳ - GTS.pdf, 2023.2, ĐỀ SỐ 1, Câu 1b"""
        A = np.array([
            [10.5, 1, 0.4, 0.7, -0.5, 0.9, -0.9], [-0.5, 10.7, 0.8, -0.5, 0.2, -0.4, 0.1],
            [0.4, 0.2, 13, 0.7, -0.1, 0.5, 0.6], [0.3, -0.6, 0.1, 12.5, -0.3, 0.5, 0.9],
            [-0.7, 0.5, -0.8, 0.9, 14.7, -0.3, -0.8], [-0.8, -0.5, -0.7, -0.3, 0.2, 15.1, 0.1],
            [0, 0, -0.5, -0.6, 0.1, -0.9, 15.9]
        ])
        b = np.array([-10, -1, -1, 0, -1, -1, -1])
        self.run_linear_system_solvers(A, b)
        
    def test_linear_system_case_3(self):
        """Nguồn: đề thi collection_Giữa kỳ - GTS.pdf, 20212, ĐỀ I, Câu 2 (a=10)"""
        a = 10.
        A = np.array([
            [27.5+a, 1.7, -3.2, 2.1, 9.23, -3.52], [2.5, 47.1+a, 5.2, 2.8, 7.23, -5.52],
            [11.3, 2.7, -38.2-a, 4.1, -7.58, 4.25], [8.4, -4.6, -6.5, 52.1+a, 1.43, 15.26],
            [42.7, -36.9, -42.7, 61.1, 243+a, -35.26], [9.2, -1, 35, -2, 14.73, 75.64+a]
        ])
        b = np.array([21.41, 27.11, 14.17, 52.49, 56.72, 18.57])
        self.run_linear_system_solvers(A, b)

    def test_linear_system_case_4(self):
        """Nguồn: đề thi collection_Cuối kỳ - GTS.pdf, 20192, Câu 1"""
        A = np.array([
            [0.8412, -0.0064, -0.0025, -0.0304, -0.0014, -0.0083, -0.1594],
            [-0.0057, 0.7355, -0.0436, -0.0099, -0.0083, -0.0201, -0.3413],
            [-0.0264, -0.1506, 0.6443, -0.0139, -0.0142, -0.0070, -0.0236],
            [-0.3299, -0.0565, -0.0495, 0.6364, -0.0204, -0.0483, -0.0649],
            [-0.0089, -0.0081, -0.0333, -0.0295, 0.6588, -0.0237, -0.0020],
            [-0.1190, -0.0901, -0.0996, -0.1260, -0.1722, 0.7632, -0.3369],
            [-0.0063, -0.0126, -0.0196, -0.0098, -0.0064, -0.0132, 0.9988]
        ])
        b = np.array([74000, 56000, 10500, 25000, 17500, 196000, 5000])
        self.run_linear_system_solvers(A, b, places=0)

    def test_linear_system_case_5(self):
        """Nguồn: CK 20191.pdf, ĐỀ I, Câu 4"""
        A = np.array([[8, 6, 10, 10], [9, 1, 10, 5], [1, 3, 1, 8], [10, 6, 10, 1]])
        b = np.array([1, 2, 3, 4])
        self.run_linear_system_solvers(A, b)

    # ===============================================
    # ===      5. TEST: TÌM MA TRẬN NGHỊCH ĐẢO      ===
    # ===============================================
    def run_inverse_solvers(self, A):
        A_inv_ref = np.linalg.inv(A)
        A_inv_gj, _ = gauss_jordan_inverse(A.copy())
        self.assertMatricesAlmostEqual(A_inv_gj, A_inv_ref, places=5)

    def test_inverse_case_1(self):
        """Nguồn: CK 20191.pdf, ĐỀ I, Câu 4"""
        A = np.array([[8, 6, 10, 10], [9, 1, 10, 5], [1, 3, 1, 8], [10, 6, 10, 1]], dtype=float)
        self.run_inverse_solvers(A)

    def test_inverse_case_2(self):
        """Nguồn: CK 20191.pdf, ĐỀ II, Câu 4"""
        A = np.array([[7, 7, 10, 8], [8, 1, 3, 2], [3, 1, 6, 5], [7, 5, 2, 7]], dtype=float)
        self.run_inverse_solvers(A)

    def test_inverse_case_3(self):
        """Nguồn: đề thi collection_Cuối kỳ - GTS.pdf, 2023.2, ĐỀ SỐ 1, Câu 2"""
        A = np.array([
            [4.0327, 2.6090, 2.3283, 4.8132, 2.8724], [2.6090, 3.6586, 4.6534, 3.5740, 3.9131],
            [2.3283, 4.6534, 6.7322, 3.4631, 5.0275], [4.8132, 3.5740, 3.4631, 6.8665, 3.1182],
            [2.8724, 3.9131, 5.0275, 3.1182, 4.8099]
        ])
        self.run_inverse_solvers(A)
        
    def test_inverse_case_4(self):
        """Nguồn: đề thi collection_Cuối kỳ - GTS.pdf, 2023.2, ĐỀ SỐ 2, Câu 2"""
        A = np.array([
            [6.7562, 4.4584, 5.1176, 3.5945, 3.4311], [4.4584, 4.3051, 4.3327, 1.9363, 1.5788],
            [5.1176, 4.3327, 5.1287, 3.5097, 3.3354], [3.5945, 1.9363, 3.5097, 4.8411, 4.8972],
            [3.4311, 1.5788, 3.3354, 4.8972, 5.0688]
        ])
        self.run_inverse_solvers(A)

    def test_inverse_case_5(self):
        """Nguồn: đề thi collection_Cuối kỳ - GTS.pdf, 20182, Câu 2 (a=20, 4x4)"""
        a = 20.
        A = np.array([
            [11+a, 22, -13, 24], [22, 233+a, 24, 35],
            [33, -24, 35+a, -26], [14, 45, 26, 47+a]
        ], dtype=float)
        self.run_inverse_solvers(A)
        
    # ===============================================
    # ===      6. TEST: HỆ PHI TUYẾN     ===
    # ===============================================
    def test_newton_system_case_1(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 22a"""
        x1, x2, x3 = sp.symbols('x1 x2 x3')
        f_system = [3*x1 - sp.cos(x2*x3) - 0.5, 4*x1**2 - 625*x2**2 + 2*x2 - 1, sp.exp(-x1*x2) + 20*x3 + (10*sp.pi-3)/3]
        X0 = np.array([0.1, 0.1, -0.5])
        sol, _ = newton_system(f_system, X0, tol=1e-7, max_iter=15)
        f_lambdas = [sp.lambdify((x1, x2, x3), f, 'numpy') for f in f_system]
        for f in f_lambdas:
            self.assertAlmostEqual(f(sol[0], sol[1], sol[2]), 0, places=6)
    
    def test_newton_system_case_2(self):
        """Nguồn: Baitap GTS full 15 tuần.pdf, Câu 21a"""
        x1, x2 = sp.symbols('x1 x2')
        f_system = [4*x1**2 - 20*x1 + 0.25*x2**2 + 8, 0.5*x1*x2**2 + 2*x1 - 5*x2 + 8]
        X0 = np.array([0.5, 2.0])
        sol, _ = newton_system(f_system, X0, tol=1e-7, max_iter=15)
        f_lambdas = [sp.lambdify((x1, x2), f, 'numpy') for f in f_system]
        for f in f_lambdas:
            self.assertAlmostEqual(f(sol[0], sol[1]), 0, places=6)

    def test_simple_iteration_system_case_1(self):
        """Nguồn: đề thi collection_Giữa kỳ - GTS.pdf, 20232, Câu 2"""
        g_system = [
            lambda x: (13 - x[1]**2 + 1.5*x[2]**2) / 15,
            lambda x: (11 + x[2] - x[0]**2) / 10,
            lambda x: (20 + x[1]**3) / 30
        ]
        X0 = np.array([0.5, 0.5, 0.5])
        sol, _ = simple_iteration_system(g_system, X0, tol=1e-8, max_iter=50)
        self.assertAlmostEqual(sol[0], g_system[0](sol), places=7)

    def test_simple_iteration_system_case_2(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 20b"""
        g_system = [
            lambda x: (13 - x[1]**2 + 4*x[2]) / 15,
            lambda x: (11 + x[2] - x[0]**2) / 10,
            lambda x: (22 + x[1]**3) / 25
        ]
        X0 = np.array([0.5, 0.5, 0.5])
        sol, _ = simple_iteration_system(g_system, X0, tol=1e-8, max_iter=50)
        self.assertAlmostEqual(sol[1], g_system[1](sol), places=7)

    def test_simple_iteration_system_case_3(self):
        """Nguồn: BaitapGTS tuần 4-6.pdf, Câu 20a"""
        g_system = [
            lambda x: (np.cos(x[1]*x[2]) + 0.5) / 3.0,
            lambda x: (1/25.0) * np.sqrt(x[0]**2 + 0.3125) - 0.03,
            lambda x: -1/20.0 * np.exp(-x[0]*x[1]) - (10*np.pi - 3)/60.0
        ]
        X0 = np.array([0.1, 0.1, -0.5])
        sol, _ = simple_iteration_system(g_system, X0, tol=1e-8, max_iter=50)
        self.assertAlmostEqual(sol[2], g_system[2](sol), places=7)

if __name__ == '__main__':
    print("Bắt đầu chạy bộ kiểm thử phức tạp cho Máy tính Giải tích số...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ComprehensiveTestNumericalMethods)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("-" * 70)
    if result.wasSuccessful():
        print("\n=> ✔️ Tất cả các bài test đã qua!")
    else:
        print("\n=> ❌ Có lỗi xảy ra trong quá trình kiểm thử.")