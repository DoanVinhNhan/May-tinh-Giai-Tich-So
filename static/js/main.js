document.addEventListener('DOMContentLoaded', function () {
    // Khi vừa load trang, tự động render trang mặc định là matrix-solve
    renderPage('matrix-solve');
    // Gắn lại event cho sidebar menu (đảm bảo khi chuyển sang SVD sẽ gắn event đúng)
    document.querySelectorAll('[data-page]').forEach(btn => {
        btn.addEventListener('click', e => {
            renderPage(btn.getAttribute('data-page'));
        });
    });
});

// === DOM ELEMENTS ===
// KHÔNG lấy các biến DOM toàn cục ở đây nữa!

// === GLOBAL STATE ===
let displayPrecision = 4; // Số chữ số sau dấu phẩy mặc định

// === HELPER FUNCTIONS ===
    // --- Hàm chuyển đổi LaTeX sang Python ---
function latexToPython(latex) {
    if (!latex) return "";
    let pyExpr = latex;

    // Xử lý các trường hợp đặc biệt trước
    // Căn bậc n: \sqrt[n]{x} -> x**(1/n)
    pyExpr = pyExpr.replace(/\\sqrt\[(.*?)\]\{(.*?)\}/g, '($2)**(1/($1))');
    // Căn bậc 2: \sqrt{x} -> sqrt(x)
    pyExpr = pyExpr.replace(/\\sqrt\{(.*?)\}/g, 'sqrt($1)');
    // Phân số: \frac{a}{b} -> (a)/(b)
    pyExpr = pyExpr.replace(/\\frac\{(.*?)\}\{(.*?)\}/g, '($1)/($2)');
    // Log cơ số a: \log_{a}{b} -> log(b, a) (Sửa lỗi logic)
    pyExpr = pyExpr.replace(/\\log_\{(.*?)\}\{(.*?)\}/g, 'log($2, $1)');
    // Biến có chỉ số: x_1, x_{23} -> x1, x23
    pyExpr = pyExpr.replace(/x_\{?(\d+)\}?/g, 'x$1');

    // Xử lý các hàm chuẩn
    pyExpr = pyExpr.replace(/\\(sin|cos|tan|asin|acos|atan|ln|exp|abs|pi)/g, '$1');

    // Xử lý các toán tử
    pyExpr = pyExpr.replace(/\^/g, '**');      // Lũy thừa
    pyExpr = pyExpr.replace(/\\cdot/g, '*');   // Nhân
    
    // Xóa các dấu ngoặc nhọn còn lại của LaTeX
    pyExpr = pyExpr.replace(/\{/g, '(');
    pyExpr = pyExpr.replace(/\}/g, ')');
    
    // Xóa các khoảng trắng thừa
    pyExpr = pyExpr.replace(/\s+/g, ' ');

    return pyExpr;
}
function formatLatexMatrix(data) {
    if (!Array.isArray(data) || !Array.isArray(data[0])) return '';
    let tableHtml = '<table class="matrix-table">';
    data.forEach(row => {
        tableHtml += '<tr>';
        row.forEach(cell => {
            // Cell chứa chuỗi LaTeX thuần túy
            const escapedCell = cell.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            tableHtml += `<td>${escapedCell}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</table>';
    return `<div class="matrix-container">${tableHtml}</div>`;
}
function parseMatrix(matrixString) {
    try {
        const rows = matrixString.trim().split('\n').filter(r => r.trim() !== '');
        if (rows.length === 0) return [];
        const matrix = rows.map(row =>
            row.trim().split(/\s+/).map(numStr => {
                const number = parseFloat(numStr);
                if (isNaN(number)) throw new Error(`Giá trị không hợp lệ: "${numStr}"`);
                return number;
            })
        );
        const firstRowLength = matrix[0].length;
        if (!matrix.every(row => row.length === firstRowLength)) {
            throw new Error('Các hàng phải có cùng số lượng phần tử.');
        }
        return matrix;
    } catch (error) {
        return { error: error.message };
    }
}

function formatNumber(num, precision = displayPrecision) {
    if (num === null || num === undefined) return 'N/A';
    // Số nhỏ hơn 1e-15 coi là 0
    if (typeof num === 'object' && num !== null && num.hasOwnProperty('re') && num.hasOwnProperty('im')) {
        let realPart = num.re;
        let imagPart = num.im;
        if (Math.abs(realPart) < 1e-15) realPart = 0;
        if (Math.abs(imagPart) < 1e-15) imagPart = 0;
        if (imagPart === 0) return realPart.toFixed(precision);
        
        const sign = imagPart < 0 ? ' - ' : ' + ';
        return `${realPart.toFixed(precision)}${sign}${Math.abs(imagPart).toFixed(precision)}i`;
    }
    if (typeof num === 'number') {
        if (Math.abs(num) < 1e-15) return (0).toFixed(precision);
        return num.toFixed(precision);
    }
    return num;
}


function formatMatrix(data, precision = displayPrecision) {
    if (!Array.isArray(data) || data.length === 0) return '';
    let tableHtml = '<table class="matrix-table">';
    data.forEach(row => {
        tableHtml += '<tr>';
        row.forEach(cell => {
            tableHtml += `<td>${formatNumber(cell, precision)}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</table>';
    return tableHtml;
}


function displayError(message) {
    const errorMessageDiv = document.getElementById('error-message');
    const resultsAreaDiv = document.getElementById('results-area');
    if (resultsAreaDiv) resultsAreaDiv.innerHTML = '';
    if (errorMessageDiv) {
        errorMessageDiv.classList.remove('hidden');
        errorMessageDiv.textContent = `Lỗi: ${message}`;
    }
}

function resetDisplay() {
    const loadingSpinnerDiv = document.getElementById('loading-spinner');
    const errorMessageDiv = document.getElementById('error-message');
    const resultsAreaDiv = document.getElementById('results-area');

    if (loadingSpinnerDiv) loadingSpinnerDiv.classList.add('hidden');
    if (errorMessageDiv) errorMessageDiv.classList.add('hidden');
    if (resultsAreaDiv) resultsAreaDiv.innerHTML = '';
}

async function handleCalculation(endpoint, body) {
    resetDisplay();
    const loadingSpinnerDiv = document.getElementById('loading-spinner');
    if(loadingSpinnerDiv) loadingSpinnerDiv.classList.remove('hidden');

    try {
        const response = await fetch("http://127.0.0.1:5001" + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            let errorText = `Lỗi Server: ${response.status} ${response.statusText}`;
            try {
                const errorResult = await response.json();
                errorText = errorResult.error || errorText;
            } catch (e) {
                // Do nothing if response is not JSON
            }
            displayError(errorText);
            return;
        }

        let result;
        try {
            result = await response.json();
        } catch (jsonErr) {
            displayError('Lỗi: Server trả về dữ liệu không phải JSON.');
            console.error('Lỗi parse JSON:', jsonErr);
            return;
        }

        resetDisplay();

        if (!result.success) {
            displayError(result.error || 'Lỗi không xác định từ server.');
            console.error('Lỗi backend:', result.error);
            return;
        }
        
        const displayMap = {
            'svd': wrapDisplay(displaySvdResults),
            'gauss-jordan': wrapDisplay(displayGaussJordanResults),
            'gauss-elimination': wrapDisplay(displayGaussEliminationResults),
            'lu-decomposition': wrapDisplay(displayLuResults),
            'cholesky': wrapDisplay(displayCholeskyResults),
            'danilevsky': wrapDisplay(displayDanilevskyResults),
            'solve': wrapDisplay(displayNonlinearEquationResults), 
            'lu': wrapDisplay(displayInverseResults), 
            'bordering': wrapDisplay(displayInverseResults),
            'jacobi': wrapDisplay(displayInverseResults),
            'newton': wrapDisplay(displayInverseResults),
            'nonlinear-system/solve': wrapDisplay(displayNonlinearSystemResults)
        };
        
        let key = endpoint.split('/').pop();
        
        if (endpoint === '/nonlinear-system/solve') {
            key = 'nonlinear-system/solve';
        } else if (endpoint.includes('/matrix/inverse/')) {
            displayMap[key](result, key);
            return; 
        }
        
        if (displayMap[key]) {
            displayMap[key](result);
        } else {
             document.getElementById('results-area').innerHTML = '<div class="text-red-600">Không có hàm hiển thị kết quả phù hợp cho endpoint này.</div>';
             console.warn('Không có hàm hiển thị cho endpoint:', endpoint);
        }

    } catch (err) {
        resetDisplay();
        displayError('Không thể kết nối đến máy chủ. Hãy chắc chắn backend Flask đang chạy.\n' + err);
        console.error('Lỗi kết nối hoặc JS:', err);
    }
}

function wrapDisplay(fn) {
    return function(result, method) {
        window.lastResult = result;
        window.lastDisplayFn = fn;
        fn(result, method);
    };
}

// --- PAGE RENDERING LOGIC FOR SIDEBAR MENU ---
function renderPage(page) {
    const mainContent = document.getElementById('main-content');
    const pageTitle = document.getElementById('page-title');
    if (!mainContent) return;

    let pageHtml = '';
    let setupFunction = null;
    let title = 'Máy tính Giải tích số';

    if (page === 'matrix-solve') {
        pageHtml = document.getElementById('matrix-solve-page').innerHTML;
        setupFunction = setupMatrixSolveEvents;
        title = 'Giải Hệ Phương Trình Tuyến Tính';
    } else if (page === 'matrix-inverse-direct') {
        pageHtml = document.getElementById('matrix-inverse-direct-page').innerHTML;
        setupFunction = setupMatrixInverseDirectEvents;
        title = 'Tính Ma Trận Nghịch Đảo (Trực tiếp)';
    } else if (page === 'matrix-inverse-iterative') {
        pageHtml = document.getElementById('matrix-inverse-iterative-page').innerHTML;
        setupFunction = setupMatrixInverseIterativeEvents;
        title = 'Tính Ma Trận Nghịch Đảo (Lặp)';
    } else if (page === 'matrix-svd') {
        pageHtml = document.getElementById('matrix-svd-page').innerHTML;
        setupFunction = setupMatrixSvdEvents;
        title = 'Phân Rã Giá Trị Suy Biến (SVD)';
    } else if (page === 'matrix-danilevsky') {
        pageHtml = document.getElementById('matrix-danilevsky-page').innerHTML;
        setupFunction = setupMatrixDanilevskyEvents;
        title = 'Tìm Trị Riêng & Vector Riêng (Danilevsky)';
    } else if (page === 'nonlinear-solve') {
        pageHtml = document.getElementById('nonlinear-solve-page').innerHTML;
        setupFunction = setupNonlinearSolveEvents;
        title = 'Giải phương trình phi tuyến f(x) = 0';
    } else if (page === 'nonlinear-system-solve') {
        pageHtml = document.getElementById('nonlinear-system-solve-page').innerHTML;
        setupFunction = setupNonlinearSystemSolveEvents;
        title = 'Giải Hệ Phương Trình Phi Tuyến';
    } else {
        pageHtml = '<div class="text-center text-gray-500">Chọn một chức năng ở menu bên trái.</div>';
    }
    
    mainContent.innerHTML = pageHtml;
    pageTitle.textContent = title;

    if(setupFunction) {
        setupFunction();
    }

    window.lastResult = null;
    window.lastDisplayFn = null;
}

// Gắn sự kiện cho sidebar menu
document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
        // BƯỚC 1: Xóa màu active khỏi TẤT CẢ các nút
        // Dòng code này sẽ tìm mọi phần tử có thuộc tính [data-page] và xóa hết các lớp màu của chúng.
        document.querySelectorAll('[data-page]').forEach(b => {
            b.classList.remove('bg-blue-100', 'text-blue-700');
            b.classList.remove('bg-green-100', 'text-green-700');
            b.classList.remove('bg-yellow-100', 'text-yellow-700');
        });
        
        // BƯỚC 2: Thêm màu active cho nút vừa được click
        const button = e.currentTarget;
        const page = button.getAttribute('data-page');

        if (page.startsWith('matrix')) {
            button.classList.add('bg-blue-100', 'text-blue-700');
        } else if (page === 'nonlinear-solve') {
            button.classList.add('bg-green-100', 'text-green-700');
        } else if (page === 'nonlinear-system-solve') {
            button.classList.add('bg-yellow-100', 'text-yellow-700');
        }

        // BƯỚC 3: Hiển thị nội dung trang tương ứng
        renderPage(page);
    });
});
// Hàm setup lại event cho trang giải hệ phương trình
function setupHptCalculation(endpoint) {
    const matrixA_Input = document.getElementById('matrix-a-input-hpt');
    const matrixB_Input = document.getElementById('matrix-b-input-hpt');

    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) {
        displayError(matrixA.error || 'Ma trận A không được để trống.');
        return;
    }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) {
        displayError(matrixB.error || 'Ma trận B không được để trống.');
        return;
    }
    if (matrixA.length !== matrixB.length) {
         displayError(`Số hàng của ma trận A (${matrixA.length}) và B (${matrixB.length}) phải bằng nhau.`);
         return;
    }

    const body = { matrix_a: matrixA, matrix_b: matrixB };
    handleCalculation(endpoint, body);
}

function setupMatrixSolveEvents() {
    document.getElementById('calculate-gauss-btn').onclick = () => setupHptCalculation('/matrix/gauss-elimination');
    document.getElementById('calculate-gj-btn').onclick = () => setupHptCalculation('/matrix/gauss-jordan');
    document.getElementById('calculate-lu-btn').onclick = () => setupHptCalculation('/matrix/lu-decomposition');
    document.getElementById('calculate-cholesky-btn').onclick = () => setupHptCalculation('/matrix/cholesky');
}

// --- START: CÁC HÀM SETUP EVENT MỚI ---
function setupInverseCalculation(endpoint, inputId) {
    const matrixA_Input = document.getElementById(inputId);
    const matrixA = parseMatrix(matrixA_Input.value);

    if (matrixA.error || matrixA.length === 0) {
        displayError(matrixA.error || 'Ma trận A không được để trống.');
        return;
    }

    if (matrixA.length !== matrixA[0].length) {
        displayError('Ma trận nghịch đảo yêu cầu ma trận vuông.');
        return;
    }

    const body = { matrix_a: matrixA };
    
    // Thêm các tham số cho phương pháp lặp
    if (inputId === 'matrix-a-input-inv-iter') {
        const tolerance = document.getElementById('inv-iter-tolerance').value;
        const maxIter = document.getElementById('inv-iter-max-iter').value;
        const x0Method = document.getElementById('inv-iter-x0-select').value;
        if (!tolerance || !maxIter) {
            displayError("Vui lòng nhập đủ Sai số và Số lần lặp tối đa.");
            return;
        }
        body.tolerance = parseFloat(tolerance);
        body.max_iter = parseInt(maxIter);
        body.x0_method = x0Method;
    }

    handleCalculation(endpoint, body);
}

function setupMatrixInverseDirectEvents() {
    const inputId = 'matrix-a-input-inv-direct';
    document.getElementById('calculate-inv-gj-btn').onclick = () => setupInverseCalculation('/matrix/inverse/gauss-jordan', inputId);
    document.getElementById('calculate-inv-lu-btn').onclick = () => setupInverseCalculation('/matrix/inverse/lu', inputId);
    document.getElementById('calculate-inv-cholesky-btn').onclick = () => setupInverseCalculation('/matrix/inverse/cholesky', inputId);
    document.getElementById('calculate-inv-bordering-btn').onclick = () => setupInverseCalculation('/matrix/inverse/bordering', inputId);
}

function setupMatrixInverseIterativeEvents() {
    const inputId = 'matrix-a-input-inv-iter';
    document.getElementById('calculate-inv-jacobi-btn').onclick = () => setupInverseCalculation('/matrix/inverse/jacobi', inputId);
    document.getElementById('calculate-inv-newton-btn').onclick = () => setupInverseCalculation('/matrix/inverse/newton', inputId);
}

// --- END: CÁC HÀM SETUP EVENT MỚI ---

// Hàm setup lại event cho trang SVD
function setupMatrixSvdEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input-svd');
    const methodSelect = document.getElementById('svd-method-select');
    const numSingularInput = document.getElementById('svd-num-singular');
    const yInitInput = document.getElementById('svd-init-matrix-input');
    const powerOptionsDiv = document.getElementById('svd-power-options');

    function updateSvdOptions() {
        if (methodSelect.value === 'power') {
            powerOptionsDiv.style.display = 'block';
        } else {
            powerOptionsDiv.style.display = 'none';
        }
    }
    if (methodSelect) {
        methodSelect.onchange = updateSvdOptions;
        updateSvdOptions();
    }

    document.getElementById('calculate-svd-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) {
            displayError(matrixA.error || 'Ma trận A không được để trống.');
            return;
        }
        const method = methodSelect ? methodSelect.value : 'default';
        const body = { matrix_a: matrixA, method };
        if (method === 'power') {
            if (numSingularInput && numSingularInput.value) {
                body.num_singular = parseInt(numSingularInput.value);
            }
            if (yInitInput && yInitInput.value.trim()) {
                let yInitArr = [];
                const lines = yInitInput.value.trim().split('\n');
                if (lines.length === 1) {
                    yInitArr = lines[0].trim().split(/\s+/).map(Number);
                } else {
                    yInitArr = lines.map(x => parseFloat(x.trim()));
                }
                if (yInitArr.some(isNaN)) {
                    displayError('Vector khởi đầu không hợp lệ.');
                    return;
                }
                body.init_matrix = yInitArr;
            }
        }
        handleCalculation('/matrix/svd', body);
    };
}
// Hàm setup lại event cho trang Danilevsky
function setupMatrixDanilevskyEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input-danilevsky');
    document.getElementById('calculate-danilevsky-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) {
            displayError(matrixA.error || 'Ma trận A không được để trống.');
            return;
        }
        handleCalculation('/matrix/danilevsky', { matrix_a: matrixA });
    };
}

// ===============================================
// === START: CODE MỚI CHO PHƯƠNG TRÌNH PHI TUYẾN
// ===============================================

function setupNonlinearSolveEvents() {
    // --- Lấy các element trên DOM ---
    const methodSelect = document.getElementById('nonlinear-method-select');
    const calculateBtn = document.getElementById('calculate-nonlinear-btn');
    
    // Groups
    const fGroup = document.getElementById('f-expression-group');
    const phiGroup = document.getElementById('phi-expression-group');
    const x0Group = document.getElementById('x0-group');
    const advancedStopGroup = document.getElementById('advanced-stop-condition-group');

    // Inputs
    const fInput = document.getElementById('f-expression-input');
    const phiInput = document.getElementById('phi-expression-input');

    // Previews
    const fPreview = document.getElementById('f-latex-preview');
    const phiPreview = document.getElementById('phi-latex-preview');

    // --- Hàm render LaTeX (live preview) ---
    function renderLatex(inputElement, previewElement) {
        const latexString = inputElement.value;
        if (latexString.trim() === "") {
            previewElement.innerHTML = "";
            previewElement.classList.remove('text-red-500');
            return;
        }
        try {
            // Render trực tiếp chuỗi LaTeX người dùng nhập
            katex.render(latexString, previewElement, {
                throwOnError: true,
                displayMode: true
            });
            previewElement.classList.remove('text-red-500');
        } catch (error) {
            previewElement.textContent = "Lỗi cú pháp LaTeX";
            previewElement.classList.add('text-red-500');
        }
    }

    // --- Gắn sự kiện ---
    fInput.addEventListener('input', () => renderLatex(fInput, fPreview));
    phiInput.addEventListener('input', () => renderLatex(phiInput, phiPreview));
    
    // Cập nhật UI dựa trên phương pháp được chọn
    function updateUIVisibility() {
        const method = methodSelect.value;
        fGroup.style.display = (method !== 'simple_iteration') ? 'block' : 'none';
        phiGroup.style.display = (method === 'simple_iteration') ? 'block' : 'none';
        x0Group.style.display = (method === 'simple_iteration') ? 'block' : 'none';
        advancedStopGroup.style.display = (method === 'newton' || method === 'secant') ? 'block' : 'none';
        // Trigger render lại preview khi chuyển phương pháp
        renderLatex(fInput, fPreview);
        renderLatex(phiInput, phiPreview);
    }

    methodSelect.addEventListener('change', updateUIVisibility);

    calculateBtn.addEventListener('click', () => {
        const method = methodSelect.value;
        const latexExpression = (method === 'simple_iteration') ? phiInput.value : fInput.value;
        
        // Chuyển đổi LaTeX sang Python trước khi gửi
        const pythonExpression = latexToPython(latexExpression);
        
        const body = {
            method: method,
            expression: pythonExpression, // Gửi biểu thức đã chuyển đổi
            interval_a: document.getElementById('interval-a-input').value,
            interval_b: document.getElementById('interval-b-input').value,
            mode: document.getElementById('stop-mode-select').value,
            value: document.getElementById('stop-value-input').value,
            stop_condition: (method === 'newton' || method === 'secant') ? document.getElementById('advanced-stop-select').value : null,
        };

        if (method === 'simple_iteration') {
            body.x0 = document.getElementById('x0-input').value;
        }
        
        // Validate inputs
        if (!latexExpression) {
            displayError('Vui lòng nhập biểu thức hàm số.');
            return;
        }
        if (!body.interval_a || !body.interval_b) {
            displayError('Vui lòng nhập đủ khoảng [a, b].');
            return;
        }
        if (!body.value) {
            displayError('Vui lòng nhập giá trị cho điều kiện dừng.');
            return;
        }

        handleCalculation('/nonlinear-equation/solve', body);
    });

    // Khởi tạo UI và preview ban đầu
    updateUIVisibility();
}


function displayNonlinearEquationResults(result) {
    const resultsArea = document.getElementById('results-area');
    
    let html = `
        <h3 class="result-heading">Kết Quả Giải Phương Trình</h3>
        <div class="text-center font-medium text-lg mb-6 p-4 bg-green-50 rounded-lg shadow-inner">
            Nghiệm x ≈ <span class="font-bold text-green-700">${formatNumber(result.solution, 8)}</span>
        </div>
        <div class="mb-4 text-center text-gray-600">
            Số lần lặp: ${result.iterations}
        </div>
    `;

    // === BƯỚC 1: SỬA LỖI HTML ===
    // Thêm các ID duy nhất là 'm1-container' và 'M1-container'
    if (result.hasOwnProperty('m1') && result.hasOwnProperty('M1')) {
        html += `
        <div class="text-center text-sm text-gray-800 mb-6 p-3 bg-gray-100 rounded-md">
            <span>Điều kiện hội tụ: </span>
            <span class="font-mono" id="m1-container">m_1 = \\min|f'(x)| \\approx ${formatNumber(result.m1, 4)}</span>; 
            <span class="font-mono" id="M1-container">M_1 = \\max|f''(x)| \\approx ${formatNumber(result.M1, 4)}</span>
        </div>
        `;
    }

    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Bảng Các Bước Lặp</h3>`;
        
        const headerMap = {
            'k': 'k', 'x_k': 'x_k', 'a': 'a_k', 'b': 'b_k', 'c': 'c_k',
            'f_c': 'f(c_k)', 'x_k+1': 'x_{k+1}', 'phi(x_k)': '\\phi(x_k)',
            'f_xk': 'f(x_k)', 'df_xk': "f'(x_k)", 'error': '\\text{error}'
        };
        
        const headers = Object.keys(result.steps[0]);
        html += `<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
        headers.forEach(header => {
            html += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider"><span id="header-${header}"></span></th>`;
        });
        html += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;

        result.steps.forEach(step => {
            html += `<tr>`;
            headers.forEach(header => {
                html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${formatNumber(step[header], 6)}</td>`;
            });
            html += `</tr>`;
        });
        html += `</tbody></table></div></div>`;
    }
    
    // Chèn toàn bộ HTML đã tạo vào trang
    resultsArea.innerHTML = html;

    // === BƯỚC 2: SỬA LỖI JAVASCRIPT ===
    // Thêm đoạn code render LaTeX cho m1 và M1

    // Render cho điều kiện hội tụ (nếu có)
    if (result.hasOwnProperty('m1') && result.hasOwnProperty('M1')) {
        const m1_container = document.getElementById('m1-container');
        const M1_container = document.getElementById('M1-container');

        if (m1_container) {
            // Lấy chuỗi text chứa mã LaTeX và render lại vào chính nó
            katex.render(m1_container.textContent, m1_container, { throwOnError: false, displayMode: false });
        }
        if (M1_container) {
            katex.render(M1_container.textContent, M1_container, { throwOnError: false, displayMode: false });
        }
    }

    // Render cho tiêu đề bảng (nếu có)
    if (result.steps && result.steps.length > 0) {
        const headersForKatex = Object.keys(result.steps[0]);
        const headerMap = { // Khai báo lại ở đây để sử dụng
            'k': 'k', 'x_k': 'x_k', 'a': 'a_k', 'b': 'b_k', 'c': 'c_k',
            'f_c': 'f(c_k)', 'x_k+1': 'x_{k+1}', 'phi(x_k)': '\\phi(x_k)',
            'f_xk': 'f(x_k)', 'df_xk': "f'(x_k)", 'error': '\\text{Sai số}'
        };
        headersForKatex.forEach(header => {
            const targetElement = document.getElementById(`header-${header}`);
            if(targetElement) {
                const latexHeader = headerMap[header] || header;
                katex.render(latexHeader, targetElement, { throwOnError: false });
            }
        });
    }
}
// ===============================================
// === END: CODE MỚI
// ===============================================

// --- START: HÀM HIỂN THỊ KẾT QUẢ MỚI ---
function displayInverseResults(result, method) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Ma Trận Nghịch Đảo A⁻¹</h3>`;
    
    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-blue-50 rounded-lg shadow-inner">${result.message}</div>`;
    }

    if (result.inverse) {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Ma trận nghịch đảo A⁻¹:</h4><div class="matrix-display">${formatMatrix(result.inverse)}</div></div>`;
    }
    
    if (result.check) {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Kiểm tra A · A⁻¹ (gần bằng ma trận đơn vị E):</h4><div class="matrix-display">${formatMatrix(result.check)}</div></div>`;
    }

    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3><div class="space-y-8">`;
        result.steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4>`;
            // Hiển thị ma trận nếu có
            if (step.matrix) {
                 html += `<div class="matrix-display">${formatMatrix(step.matrix)}</div>`;
            }
            // Hiển thị các ma trận L, U, P, v.v.
            ['L', 'U', 'P', 'M', 'inv_M', 'theta'].forEach(key => {
                if (step[key] !== undefined) {
                    html += `<div class="mt-2"><span class="font-semibold">${key}:</span>`;
                    if (Array.isArray(step[key])) { // Là ma trận
                        html += `<div class="matrix-display">${formatMatrix(step[key])}</div>`;
                    } else { // Là giá trị
                        html += ` <span class="font-mono">${formatNumber(step[key])}</span>`;
                    }
                    html += `</div>`;
                }
            });
            // Hiển thị bảng lặp cho Jacobi/Newton
            if (step.table) {
                html += `<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
                step.table.headers.forEach(header => {
                    html += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">${header}</th>`;
                });
                html += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;
                step.table.rows.forEach(row => {
                    html += `<tr>`;
                    row.forEach(cell => {
                         html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${cell}</td>`;
                    });
                    html += `</tr>`;
                });
                 html += `</tbody></table></div>`;
            }

            html += `</div>`;
        });
        html += `</div></div>`;
    }
    resultsArea.innerHTML = html;
}
// --- END: HÀM HIỂN THỊ KẾT QUẢ MỚI ---


// === CÁC HÀM HIỂN THỊ CŨ (GIỮ NGUYÊN) ===
function displaySvdResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Phân Tích SVD (A = UΣVᵀ)</h3>`;
    const uCols = result.U && result.U[0] ? result.U[0].length : 0;
    const sigmaCols = result.Sigma && result.Sigma[0] ? result.Sigma[0].length : 0;
    const vtCols = result.V_transpose && result.V_transpose[0] ? result.V_transpose[0].length : 0;
    const isWide = uCols > 4 || sigmaCols > 4 || vtCols > 4;
    if (isWide) {
        html += `<div class="mb-8">
            <div class="mb-6"><h4 class="font-medium text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.U)}</div></div>
            <div class="mb-6"><h4 class="font-medium text-gray-700">Ma trận Σ</h4><div class="matrix-display">${formatMatrix(result.Sigma)}</div></div>
            <div class="mb-6"><h4 class="font-medium text-gray-700">Ma trận Vᵀ</h4><div class="matrix-display">${formatMatrix(result.V_transpose)}</div></div>
        </div>`;
    } else {
        html += `
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 text-center">
                <div><h4 class="font-medium text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.U)}</div></div>
                <div><h4 class="font-medium text-gray-700">Ma trận Σ</h4><div class="matrix-display">${formatMatrix(result.Sigma)}</div></div>
                <div><h4 class="font-medium text-gray-700">Ma trận Vᵀ</h4><div class="matrix-display">${formatMatrix(result.V_transpose)}</div></div>
            </div>`;
    }
    if (result.intermediate_steps) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Tính Toán Trung Gian</h3><div class="space-y-6">`;
        if (result.intermediate_steps.A_transpose_A) {
            html += `<div><h4 class="font-medium text-gray-700">Ma trận AᵀA</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.A_transpose_A)}</div></div>`;
        }
        if (result.intermediate_steps.eigenvalues_of_ATA) {
            html += `<div><h4 class="font-medium text-gray-700">Giá trị riêng của AᵀA (λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.eigenvalues_of_ATA.map(v => formatNumber(v)).join(', ')} ]</div></div>`;
        }
        if (result.intermediate_steps.singular_values) {
            html += `<div><h4 class="font-medium text-gray-700">Giá trị kỳ dị (σ = √λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.singular_values.map(v => formatNumber(v)).join(', ')} ]</div></div>`;
        }
        if (result.intermediate_steps.V_matrix) {
            html += `<div><h4 class="font-medium text-gray-700">Ma trận V</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.V_matrix)}</div></div>`;
        }
        if (result.intermediate_steps.steps) {
            html += `<div class="mt-8"><h4 class="font-medium text-gray-700">Các bước lặp Power Method + Xuống thang</h4>`;
            result.intermediate_steps.steps.forEach((step, idx) => {
                html += `<div class="mb-6 p-4 bg-gray-50 rounded-lg border">
                    <h5 class="font-medium text-gray-700 mb-2">Giá trị kỳ dị thứ ${step.singular_index} (σ ≈ ${formatNumber(step.singular_value)})</h5>
                    <div class="mb-2 text-sm text-gray-600">Các bước lặp:</div>
                    <ol class="list-decimal ml-6 mb-2 text-sm">`;
                step.lambda_steps.forEach((lam, i) => {
                     html += `<li>λ<sub>${i+1}</sub> = ${formatNumber(lam)}, vector y: [${step.y_steps[i+1].map(v => formatNumber(v,3)).join(', ')}]</li>`;
                });
                html += `</ol>
                    <div class="mb-2 text-sm text-gray-600">Véctơ riêng cuối cùng (chuẩn hóa): [${step.right_vec.map(v => formatNumber(v,4)).join(', ')}]</div>
                </div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
    }
    resultsArea.innerHTML = html;
}

function displayGaussJordanResults(result) {
    const resultsArea = document.getElementById('results-area');
    // Phân biệt giữa giải HPT và tìm nghịch đảo
    if (result.inverse) {
        return displayInverseResults(result, 'gauss-jordan');
    }
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Gauss-Jordan', result);
    if (result.intermediate_steps) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Biến Đổi Ma Trận</h3><div class="space-y-8">`;
        result.intermediate_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="matrix-display">${formatMatrix(step.matrix)}</div></div>`;
        });
        html += `</div></div>`;
    }
    resultsArea.innerHTML = html;
}
    
function displayGaussEliminationResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Khử Gauss', result);
    if (result.forward_steps) {
        html += `<div class="mt-10"><h3 class="result-heading">Quy Trình Thuận</h3><div class="space-y-8">`;
        result.forward_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="matrix-display">${formatMatrix(step.matrix)}</div></div>`;
        });
        html += `</div></div>`;
    }
    if (result.backward_steps && result.backward_steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Quy Trình Nghịch</h3><div class="space-y-8">`;
        result.backward_steps.forEach(step => {
            html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.message}</h4><div class="p-3 bg-gray-100 rounded-md text-sm font-mono text-center">Ma trận nghiệm X hiện tại:<br>${formatMatrix(step.solution_so_far)}</div></div>`;
        });
        html += `</div></div>`;
    }
    resultsArea.innerHTML = html;
}

function displayLuResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách LU', result);
    if ((result.decomposition && (result.decomposition.L || result.decomposition.P || result.decomposition.U))) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Ma Trận L, U${result.decomposition?.P ? ', P' : ''}</h3>`;
        html += `<div class="grid grid-cols-1 md:grid-cols-3 gap-8">`;
        if(result.decomposition.L) html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận L</h4><div class="matrix-display">${formatMatrix(result.decomposition.L)}</div></div>`;
        if(result.decomposition.U) html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.decomposition.U)}</div></div>`;
        if(result.decomposition.P) html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận P</h4><div class="matrix-display">${formatMatrix(result.decomposition.P)}</div></div>`;
        html += `</div></div>`;
    }
    if (result.status === 'unique_solution' && result.intermediate_y) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3>`;
        html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Ly = PB, ta được Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
        html += `</div>`;
    }
    resultsArea.innerHTML = html;
}


function displayCholeskyResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách Cholesky', result);
    if (result.decomposition.M && result.transformation_message.includes('không đối xứng')) {
         html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Ma trận M = AᵀA</h4><div class="matrix-display">${formatMatrix(result.decomposition.M)}</div></div>`;
    }
    if (result.decomposition.U && result.decomposition.Ut) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Phân Tách (M = UᵀU)</h3>`;
        html += `<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.decomposition.U)}</div></div>`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận Uᵀ</h4><div class="matrix-display">${formatMatrix(result.decomposition.Ut)}</div></div>`;
        html += `</div>`;
    }
    if (result.intermediate_y) {
        html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Uᵀy = d, ta được Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
    }
    html += `</div>`;
    resultsArea.innerHTML = html;
}


function displayDanilevskyResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Tìm Giá Trị Riêng (Danielevsky)</h3>`;
    
    // Kiểm tra kết quả có đúng định dạng không
    if (result.eigenvalues && result.eigenvectors) {
         html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Giá trị riêng (λ):</h4><div class="matrix-display text-center">[${result.eigenvalues.map(v => formatNumber(v)).join(',&nbsp;&nbsp; ')}]</div></div>`;
        
        // Cần chỉnh sửa cách hiển thị vector riêng cho phù hợp
        let eigenvectorsHtml = '<table class="matrix-table">';
        const num_vectors = result.eigenvectors.length > 0 ? result.eigenvectors[0].length : 0;
        if(num_vectors > 0) {
            const num_components = result.eigenvectors.length;
            for (let i = 0; i < num_components; i++) {
                eigenvectorsHtml += '<tr>';
                for(let j=0; j<num_vectors; j++){
                     eigenvectorsHtml += `<td>${formatNumber(result.eigenvectors[i][j])}</td>`;
                }
                eigenvectorsHtml += '</tr>';
            }
        }
        eigenvectorsHtml += '</table>';
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Vector riêng tương ứng (các cột):</h4><div class="matrix-display">${formatMatrix(result.eigenvectors)}</div></div>`;


        if (result.steps && result.steps.length > 0) {
            html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3><div class="space-y-8">`;
            result.steps.forEach((step, i) => {
                html += `<div><h4 class="font-medium text-gray-700 mb-2">${step.desc || `Bước ${i+1}`}</h4><div class="matrix-display">${formatMatrix(step.matrix)}</div></div>`;
            });
            html += `</div></div>`;
        }
    } else {
        html += `<div class="text-red-500">Lỗi: Định dạng kết quả trả về không hợp lệ.</div>`;
    }
    
    resultsArea.innerHTML = html;
}

// Hiển thị kết quả hệ phương trình dạng tổng quát (dùng cho Gauss, Gauss-Jordan, LU, Cholesky)
function displayGenericHptResults(title, result) {
    let html = `<h3 class="result-heading">${title}</h3>`;
     if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-blue-50 rounded-lg shadow-inner">${result.message}</div>`;
    }
    if (result.transformation_message) {
        html += `<p class="text-center text-gray-600 mb-4">${result.transformation_message}</p>`;
    }

    if (result.status === 'unique_solution') {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X:</h4><div class="matrix-display">${formatMatrix(result.solution)}</div></div>`;
    } else if (result.status === 'infinite_solutions') {
        const { particular_solution, null_space_vectors, num_free_vars } = result.general_solution;
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm tổng quát:</h4>`;
        let termHtml = '';
        for (let i = 0; i < num_free_vars; i++) {
            const v_k = null_space_vectors.map(row => [row[i]]);
            termHtml += `&nbsp; + &nbsp; t<sub>${i+1}</sub> &nbsp; <div class="matrix-display !inline-block">${formatMatrix(v_k)}</div>`;
        }
        html += `<div class="flex justify-center items-center flex-wrap"><span class="text-2xl mr-4">X = </span><div class="matrix-display !inline-block" title="Nghiệm riêng Xp">${formatMatrix(particular_solution)}</div>${termHtml}</div>`;
        html += `<p class="text-center text-sm text-gray-500 mt-2">Với t<sub>k</sub> là các tham số tự do.</p></div>`;
    } else if (result.status === 'no_solution') {
         if (result.solution_matrix || (result.forward_steps && result.forward_steps.length > 0) ) {
            const last_matrix = result.solution_matrix || result.forward_steps[result.forward_steps.length - 1].matrix;
            html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Dạng ma trận cuối cùng cho thấy sự mâu thuẫn:</h4><div class="matrix-display">${formatMatrix(last_matrix)}</div></div>`;
        }
    }
    return html;
}
function setupNonlinearSystemSolveEvents() {
    // DOM elements
    const methodSelect = document.getElementById('ns-method-select');
    const expressionsInput = document.getElementById('ns-expressions-input');
    const previewDiv = document.getElementById('ns-latex-preview');
    const x0Input = document.getElementById('ns-x0-input');
    const domainGroup = document.getElementById('ns-domain-group');
    const domainInput = document.getElementById('ns-domain-input');
    const expressionsLabel = document.getElementById('ns-expressions-label');
    const calculateBtn = document.getElementById('calculate-ns-btn');

    const placeholders = {
        newton: "x_1^2 + x_2^2 - 1\nx_1^2 - x_2",
        newton_modified: "x_1^2 + x_2^2 - 1\nx_1^2 - x_2",
        simple_iteration: "\\sqrt{1 - x_2^2}\n\\sqrt{x_1}"
    };

    // Hàm render LaTeX cho hệ phương trình (mỗi dòng một biểu thức)
    function renderSystemLatex() {
        if (!expressionsInput || !previewDiv) return;

        const latexLines = expressionsInput.value.trim().split('\n');
        previewDiv.innerHTML = '';
        previewDiv.classList.remove('text-red-500', 'items-start');
        previewDiv.classList.add('items-center');

        if (expressionsInput.value.trim() === "") {
            return;
        }
        
        let hasError = false;
        latexLines.forEach(line => {
            if (line.trim() === "") {
                const emptyDiv = document.createElement('div');
                emptyDiv.innerHTML = '&nbsp;';
                previewDiv.appendChild(emptyDiv);
                return;
            };
            const lineDiv = document.createElement('div');
            lineDiv.className = 'w-full text-center';
            try {
                katex.render(line, lineDiv, {
                    throwOnError: true,
                    displayMode: false
                });
            } catch (error) {
                lineDiv.textContent = `Lỗi cú pháp: "${line}"`;
                lineDiv.className = 'w-full text-left text-red-500 text-sm';
                hasError = true;
            }
            previewDiv.appendChild(lineDiv);
        });

        if (hasError) {
             previewDiv.classList.remove('items-center');
             previewDiv.classList.add('items-start');
        }
    }
    
    function updateUIVisibility() {
        const method = methodSelect.value;
        expressionsInput.placeholder = placeholders[method];
        if (method === 'simple_iteration') {
            expressionsLabel.innerHTML = 'Hệ hàm lặp <span class="font-mono text-sm">X = &phi;(X)</span> (dạng LaTeX)';
            domainGroup.style.display = 'block';
            domainInput.placeholder = "0 1\n0 1";
        } else {
            expressionsLabel.innerHTML = 'Hệ phương trình <span class="font-mono text-sm">F(X) = 0</span> (dạng LaTeX)';
            domainGroup.style.display = 'none';
        }
        renderSystemLatex();
    }

    // Event listeners
    methodSelect.addEventListener('change', updateUIVisibility);
    expressionsInput.addEventListener('input', renderSystemLatex);

    calculateBtn.addEventListener('click', () => {
        const method = methodSelect.value;
        
        // Lấy biểu thức LaTeX và chuyển đổi sang cú pháp Python
        const latexExpressions = expressionsInput.value.trim().split('\n').filter(line => line.trim() !== '');
        const expressions = latexExpressions.map(latexToPython);
        const n = expressions.length;
        if (n === 0) {
            displayError('Vui lòng nhập ít nhất một hàm số.');
            return;
        }

        const x0_lines = x0Input.value.trim().split('\n').filter(line => line.trim() !== '');
        if (x0_lines.length !== n) {
            displayError(`Số lượng giá trị ban đầu (${x0_lines.length}) không khớp với số phương trình (${n}).`);
            return;
        }
        const x0 = x0_lines.map(val => parseFloat(val.trim()));
        if (x0.some(isNaN)) {
            displayError('Giá trị ban đầu X₀ chứa giá trị không hợp lệ.');
            return;
        }

        const body = {
            n: n,
            method: method,
            expressions: expressions,
            x0: x0,
            stop_option: document.getElementById('ns-stop-option-select').value,
            stop_value: document.getElementById('ns-stop-value-input').value,
        };

        if (method === 'simple_iteration') {
            const domain_lines = domainInput.value.trim().split('\n').filter(line => line.trim() !== '');
            if (domain_lines.length !== n) {
                displayError(`Số lượng miền D (${domain_lines.length}) không khớp với số phương trình (${n}).`);
                return;
            }
            let a0 = [];
            let b0 = [];
            for (const line of domain_lines) {
                const parts = line.trim().split(/\s+/);
                if (parts.length !== 2 || isNaN(parseFloat(parts[0])) || isNaN(parseFloat(parts[1]))) {
                    displayError(`Miền D có dòng không hợp lệ: "${line}". Cần 2 số cách nhau bằng dấu cách.`);
                    return;
                }
                a0.push(parseFloat(parts[0]));
                b0.push(parseFloat(parts[1]));
            }
            body.a0 = a0;
            body.b0 = b0;
        }
        handleCalculation('/nonlinear-system/solve', body);
    });
    updateUIVisibility();
}
function displayNonlinearSystemResults(result) {
    const resultsArea = document.getElementById('results-area');
    let html = `<h3 class="result-heading">Kết Quả Giải Hệ Phi Tuyến</h3>`;

    if (result.message) {
        html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-green-50 rounded-lg shadow-inner">${result.message}</div>`;
    }

    // Hiển thị nghiệm
    if (result.solution) {
        const solMatrix = result.solution.map(v => [v]);
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X ≈</h4><div class="matrix-display">${formatMatrix(solMatrix, 6)}</div></div>`;
    }

    // Hiển thị các thông tin chẩn đoán
    let diagnosticHtml = '';
    if (result.jacobian_matrix_latex) {
        diagnosticHtml += `<div class="p-4 bg-gray-50 rounded-lg flex flex-col">
                        <h4 class="font-semibold text-gray-700 text-center mb-2">Ma trận Jacobi J(X)</h4>
                        <div id="jacobian-matrix-container" class="flex-grow flex items-center justify-center">${formatLatexMatrix(result.jacobian_matrix_latex)}</div>
                     </div>`;
    }
    if (result.J0_inv_matrix) {
        diagnosticHtml += `<div class="p-4 bg-gray-50 rounded-lg flex flex-col">
                    <h4 class="font-semibold text-gray-700 text-center mb-2">Ma trận J(X₀)⁻¹</h4>
                    <div class="flex-grow flex items-center justify-center">${formatMatrix(result.J0_inv_matrix, 5)}</div>
                 </div>`;
    }
    // Các thông tin khác có thể thêm vào đây
    
    if (diagnosticHtml) {
        // Thay đổi ở đây: Dùng flex, flex-wrap và justify-center
        html += `<div class="flex flex-wrap justify-center gap-6 mb-8">
                    ${diagnosticHtml}
                 </div>`;
    }

    // Hiển thị bảng lặp
    if (result.steps && result.steps.length > 0) {
        html += `<div class="mt-10"><h3 class="result-heading">Bảng Các Bước Lặp</h3>`;
        const headers = Object.keys(result.steps[0]);
        html += `<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>`;
        headers.forEach(header => {
            html += `<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider font-mono">${header}</th>`;
        });
        html += `</tr></thead><tbody class="bg-white divide-y divide-gray-200">`;

        // --- PHẦN SỬA LỖI ---
        result.steps.forEach(step => {
            html += `<tr>`;
            // Vòng lặp đúng: duyệt qua tất cả headers
            headers.forEach(header => {
                 const value = step[header];
                 html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">${formatNumber(value, 6)}</td>`;
            });
            html += `</tr>`;
        });
        // --- KẾT THÚC PHẦN SỬA LỖI ---

        html += `</tbody></table></div></div>`;
    }
    
    resultsArea.innerHTML = html;
    
    // Render KaTeX cho ma trận Jacobi
    if (result.jacobian_matrix_latex) {
        const container = document.getElementById('jacobian-matrix-container');
        if (container) {
            container.querySelectorAll('td').forEach(cell => {
                try {
                    katex.render(cell.textContent, cell, { 
                        throwOnError: false, 
                        displayMode: false 
                    });
                } catch(e) { console.error('Lỗi render KaTeX:', e); }
            });
        }
    }
}