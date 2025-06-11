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

function formatNumber(num) {
    // Số nhỏ hơn 1e-15 coi là 0
    if (typeof num === 'object' && num !== null && num.hasOwnProperty('re') && num.hasOwnProperty('im')) {
        if (Math.abs(num.im) < 1e-15) return Math.abs(num.re) < 1e-15 ? '\u2007' + '0' : (num.re >= 0 ? '\u2007' : '') + num.re.toFixed(displayPrecision);
        const sign = num.im < 0 ? ' -' : ' +';
        return `${Math.abs(num.re) < 1e-15 ? '\u2007' + '0' : (num.re >= 0 ? '\u2007' : '') + num.re.toFixed(displayPrecision)}${sign} ${Math.abs(num.im).toFixed(displayPrecision)}i`;
    }
    if (typeof num === 'number') {
        if (Math.abs(num) < 1e-15) return '\u2007' + '0';
        return (num >= 0 ? '\u2007' : '') + num.toFixed(displayPrecision);
    }
    return num;
}

function formatMatrix(data, precision = displayPrecision) {
    if (!Array.isArray(data) || data.length === 0) return '';
    let tableHtml = '<table class="matrix-table">';
    data.forEach(row => {
        tableHtml += '<tr>';
        row.forEach(cell => {
            tableHtml += `<td>${formatNumber(cell)}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</table>';
    return `<div class="matrix-container">${tableHtml}</div>`;
}

function displayError(message) {
    resultsArea.innerHTML = '';
    errorMessage.classList.remove('hidden');
    errorMessage.textContent = `Lỗi: ${message}`;
}

function resetDisplay() {
    loadingSpinner.classList.add('hidden');
    errorMessage.classList.add('hidden');
    resultsArea.innerHTML = '';
}

async function handleCalculation(endpoint, body) {
    resetDisplay();
    loadingSpinner.classList.remove('hidden');
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        // Kiểm tra response status trước khi parse JSON
        if (!response.ok) {
            const text = await response.text();
            displayError(`Lỗi server (${response.status}): ${text}`);
            console.error('Lỗi server:', response.status, text);
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
            'cholesky': wrapDisplay(displayCholeskyResults)
        };
        const key = endpoint.split('/').pop();
        if (displayMap[key]) {
            displayMap[key](result);
        } else {
            // Nếu không có hàm hiển thị phù hợp, log ra console
            resultsArea.innerHTML = '<div class="text-red-600">Không có hàm hiển thị kết quả phù hợp cho endpoint này.</div>';
            console.warn('Không có hàm hiển thị cho endpoint:', endpoint);
        }
    } catch (err) {
        resetDisplay();
        displayError('Không thể kết nối đến máy chủ.\n' + err);
        console.error('Lỗi kết nối hoặc JS:', err);
    }
}

// Ghi nhớ kết quả cuối cùng để render lại khi đổi precision
function wrapDisplay(fn) {
    return function(result) {
        window.lastResult = result;
        window.lastDisplayFn = fn;
        fn(result);
    };
}

// --- PAGE RENDERING LOGIC FOR SIDEBAR MENU ---
function renderPage(page) {
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;
    // Xóa các event listener cũ bằng cách thay thế vùng main-content
    if (page === 'matrix-solve') {
        mainContent.innerHTML = document.getElementById('matrix-solve-page').innerHTML;
        setupMatrixSolveEvents();
        document.title = 'Giải hệ phương trình | Máy tính ma trận';
    } else if (page === 'matrix-svd') {
        mainContent.innerHTML = document.getElementById('matrix-svd-page').innerHTML;
        setupMatrixSvdEvents();
        document.title = 'Phân tích SVD | Máy tính ma trận';
    } else {
        mainContent.innerHTML = '<div class="text-center text-gray-500">Chọn một chức năng ở menu bên trái.</div>';
        document.title = 'Máy tính ma trận';
    }
    // Đảm bảo vùng hiển thị kết quả, spinner, error luôn đúng scope trang
    window.resultsArea = document.getElementById('results-area');
    window.loadingSpinner = document.getElementById('loading-spinner');
    window.errorMessage = document.getElementById('error-message');
    // Xóa kết quả cũ khi chuyển tab
    if (window.resultsArea) window.resultsArea.innerHTML = '';
    if (window.errorMessage) window.errorMessage.classList.add('hidden');
    if (window.loadingSpinner) window.loadingSpinner.classList.add('hidden');
    // Xóa cache kết quả toàn cục khi chuyển tab
    window.lastResult = null;
    window.lastDisplayFn = null;
}
// Gắn sự kiện cho sidebar menu
document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
        renderPage(btn.getAttribute('data-page'));
    });
});
// Hàm setup lại event cho trang giải hệ phương trình
function setupMatrixSolveEvents() {
    // Lấy lại các DOM element mới sau khi render
    const matrixA_Input = document.getElementById('matrix-a-input');
    const matrixB_Input = document.getElementById('matrix-b-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    // Gán event cho các nút giải hệ
    document.getElementById('calculate-gj-btn').onclick = () => setupHptCalculation('/matrix/gauss-jordan', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-gauss-btn').onclick = () => setupHptCalculation('/matrix/gauss-elimination', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-lu-btn').onclick = () => setupHptCalculation('/matrix/lu-decomposition', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-cholesky-btn').onclick = () => setupHptCalculation('/matrix/cholesky', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
}
// Hàm setup lại event cho trang SVD
function setupMatrixSvdEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input');
    const initMatrixInput = document.getElementById('svd-init-matrix-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    document.getElementById('calculate-svd-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
        let initMatrix = undefined;
        if (initMatrixInput && initMatrixInput.value.trim() !== '') {
            initMatrix = parseMatrix(initMatrixInput.value);
            if (initMatrix.error) { errorMessage.classList.remove('hidden'); errorMessage.textContent = initMatrix.error; resultsArea.innerHTML = ''; return; }
        }
        const body = { matrix_a: matrixA };
        if (initMatrix) body.init_matrix = initMatrix;
        handleCalculation('/matrix/svd', body);
    };
}

// Sửa lại setupHptCalculation để nhận đúng input/result area
function setupHptCalculation(endpoint, matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage) {
    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixB.error || 'Ma trận B không được để trống.'; resultsArea.innerHTML = ''; return; }
    if (matrixA.length !== matrixB.length) { errorMessage.classList.remove('hidden'); errorMessage.textContent = `Số hàng của ma trận A (${matrixA.length}) và B (${matrixB.length}) phải bằng nhau.`; resultsArea.innerHTML = ''; return; }
    handleCalculation(endpoint, { matrix_a: matrixA, matrix_b: matrixB });
}

// --- PAGE RENDERING LOGIC FOR SIDEBAR MENU ---
function renderPage(page) {
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;
    // Xóa các event listener cũ bằng cách thay thế vùng main-content
    if (page === 'matrix-solve') {
        mainContent.innerHTML = document.getElementById('matrix-solve-page').innerHTML;
        setupMatrixSolveEvents();
        document.title = 'Giải hệ phương trình | Máy tính ma trận';
    } else if (page === 'matrix-svd') {
        mainContent.innerHTML = document.getElementById('matrix-svd-page').innerHTML;
        setupMatrixSvdEvents();
        document.title = 'Phân tích SVD | Máy tính ma trận';
    } else {
        mainContent.innerHTML = '<div class="text-center text-gray-500">Chọn một chức năng ở menu bên trái.</div>';
        document.title = 'Máy tính ma trận';
    }
    // Đảm bảo vùng hiển thị kết quả, spinner, error luôn đúng scope trang
    window.resultsArea = document.getElementById('results-area');
    window.loadingSpinner = document.getElementById('loading-spinner');
    window.errorMessage = document.getElementById('error-message');
    // Xóa kết quả cũ khi chuyển tab
    if (window.resultsArea) window.resultsArea.innerHTML = '';
    if (window.errorMessage) window.errorMessage.classList.add('hidden');
    if (window.loadingSpinner) window.loadingSpinner.classList.add('hidden');
    // Xóa cache kết quả toàn cục khi chuyển tab
    window.lastResult = null;
    window.lastDisplayFn = null;
}
// Gắn sự kiện cho sidebar menu
document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
        renderPage(btn.getAttribute('data-page'));
    });
});
// Hàm setup lại event cho trang giải hệ phương trình
function setupMatrixSolveEvents() {
    // Lấy lại các DOM element mới sau khi render
    const matrixA_Input = document.getElementById('matrix-a-input');
    const matrixB_Input = document.getElementById('matrix-b-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    // Gán event cho các nút giải hệ
    document.getElementById('calculate-gj-btn').onclick = () => setupHptCalculation('/matrix/gauss-jordan', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-gauss-btn').onclick = () => setupHptCalculation('/matrix/gauss-elimination', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-lu-btn').onclick = () => setupHptCalculation('/matrix/lu-decomposition', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-cholesky-btn').onclick = () => setupHptCalculation('/matrix/cholesky', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
}
// Hàm setup lại event cho trang SVD
function setupMatrixSvdEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input');
    const initMatrixInput = document.getElementById('svd-init-matrix-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    document.getElementById('calculate-svd-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
        let initMatrix = undefined;
        if (initMatrixInput && initMatrixInput.value.trim() !== '') {
            initMatrix = parseMatrix(initMatrixInput.value);
            if (initMatrix.error) { errorMessage.classList.remove('hidden'); errorMessage.textContent = initMatrix.error; resultsArea.innerHTML = ''; return; }
        }
        const body = { matrix_a: matrixA };
        if (initMatrix) body.init_matrix = initMatrix;
        handleCalculation('/matrix/svd', body);
    };
}

// Sửa lại setupHptCalculation để nhận đúng input/result area
function setupHptCalculation(endpoint, matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage) {
    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixB.error || 'Ma trận B không được để trống.'; resultsArea.innerHTML = ''; return; }
    if (matrixA.length !== matrixB.length) { errorMessage.classList.remove('hidden'); errorMessage.textContent = `Số hàng của ma trận A (${matrixA.length}) và B (${matrixB.length}) phải bằng nhau.`; resultsArea.innerHTML = ''; return; }
    handleCalculation(endpoint, { matrix_a: matrixA, matrix_b: matrixB });
}

// --- PAGE RENDERING LOGIC FOR SIDEBAR MENU ---
function renderPage(page) {
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;
    // Xóa các event listener cũ bằng cách thay thế vùng main-content
    if (page === 'matrix-solve') {
        mainContent.innerHTML = document.getElementById('matrix-solve-page').innerHTML;
        setupMatrixSolveEvents();
        document.title = 'Giải hệ phương trình | Máy tính ma trận';
    } else if (page === 'matrix-svd') {
        mainContent.innerHTML = document.getElementById('matrix-svd-page').innerHTML;
        setupMatrixSvdEvents();
        document.title = 'Phân tích SVD | Máy tính ma trận';
    } else {
        mainContent.innerHTML = '<div class="text-center text-gray-500">Chọn một chức năng ở menu bên trái.</div>';
        document.title = 'Máy tính ma trận';
    }
    // Đảm bảo vùng hiển thị kết quả, spinner, error luôn đúng scope trang
    window.resultsArea = document.getElementById('results-area');
    window.loadingSpinner = document.getElementById('loading-spinner');
    window.errorMessage = document.getElementById('error-message');
    // Xóa kết quả cũ khi chuyển tab
    if (window.resultsArea) window.resultsArea.innerHTML = '';
    if (window.errorMessage) window.errorMessage.classList.add('hidden');
    if (window.loadingSpinner) window.loadingSpinner.classList.add('hidden');
    // Xóa cache kết quả toàn cục khi chuyển tab
    window.lastResult = null;
    window.lastDisplayFn = null;
}
// Gắn sự kiện cho sidebar menu
document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
        renderPage(btn.getAttribute('data-page'));
    });
});
// Hàm setup lại event cho trang giải hệ phương trình
function setupMatrixSolveEvents() {
    // Lấy lại các DOM element mới sau khi render
    const matrixA_Input = document.getElementById('matrix-a-input');
    const matrixB_Input = document.getElementById('matrix-b-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    // Gán event cho các nút giải hệ
    document.getElementById('calculate-gj-btn').onclick = () => setupHptCalculation('/matrix/gauss-jordan', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-gauss-btn').onclick = () => setupHptCalculation('/matrix/gauss-elimination', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-lu-btn').onclick = () => setupHptCalculation('/matrix/lu-decomposition', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
    document.getElementById('calculate-cholesky-btn').onclick = () => setupHptCalculation('/matrix/cholesky', matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage);
}
// Hàm setup lại event cho trang SVD
function setupMatrixSvdEvents() {
    const matrixA_Input = document.getElementById('matrix-a-input');
    const initMatrixInput = document.getElementById('svd-init-matrix-input');
    const resultsArea = document.getElementById('results-area');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    document.getElementById('calculate-svd-btn').onclick = () => {
        const matrixA = parseMatrix(matrixA_Input.value);
        if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
        let initMatrix = undefined;
        if (initMatrixInput && initMatrixInput.value.trim() !== '') {
            initMatrix = parseMatrix(initMatrixInput.value);
            if (initMatrix.error) { errorMessage.classList.remove('hidden'); errorMessage.textContent = initMatrix.error; resultsArea.innerHTML = ''; return; }
        }
        const body = { matrix_a: matrixA };
        if (initMatrix) body.init_matrix = initMatrix;
        handleCalculation('/matrix/svd', body);
    };
}

// Sửa lại setupHptCalculation để nhận đúng input/result area
function setupHptCalculation(endpoint, matrixA_Input, matrixB_Input, resultsArea, loadingSpinner, errorMessage) {
    const matrixA = parseMatrix(matrixA_Input.value);
    if (matrixA.error || matrixA.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixA.error || 'Ma trận A không được để trống.'; resultsArea.innerHTML = ''; return; }
    const matrixB = parseMatrix(matrixB_Input.value);
    if (matrixB.error || matrixB.length === 0) { errorMessage.classList.remove('hidden'); errorMessage.textContent = matrixB.error || 'Ma trận B không được để trống.'; resultsArea.innerHTML = ''; return; }
    if (matrixA.length !== matrixB.length) { errorMessage.classList.remove('hidden'); errorMessage.textContent = `Số hàng của ma trận A (${matrixA.length}) và B (${matrixB.length}) phải bằng nhau.`; resultsArea.innerHTML = ''; return; }
    handleCalculation(endpoint, { matrix_a: matrixA, matrix_b: matrixB });
}

// === DISPLAY FUNCTIONS ===
function displayGenericHptResults(title, result) {
    let html = `<h3 class="result-heading">${title}</h3>`;
    if (result.message) {
         html += `<div class="text-center font-medium text-lg mb-6 p-4 bg-gray-50 rounded-lg shadow-inner">${result.message}</div>`;
    }
    if (result.transformation_message) {
        html += `<p class="text-center text-gray-600 mb-4">${result.transformation_message}</p>`;
    }

    if (result.status === 'unique_solution') {
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm duy nhất X:</h4><div class="matrix-display">${formatMatrix(result.solution)}</div></div>`;
    } else if (result.status === 'infinite_solutions') {
        const { particular_solution, null_space_vectors, num_free_vars } = result.general_solution;
        
        let termHtml = '';
        for (let i = 0; i < num_free_vars; i++) {
            const v_k = null_space_vectors.map(row => [row[i]]);
            termHtml += `&nbsp; + &nbsp; t<sub>${i+1}</sub> &nbsp; <div class="matrix-display !inline-block">${formatMatrix(v_k)}</div>`;
        }

        html += `
            <div class="mb-8">
                <h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm Tổng Quát</h4>
                <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
                    <div class="flex justify-center items-center flex-wrap">
                        <span class="text-2xl mr-4">X &nbsp; = </span>
                        <div class="matrix-display !inline-block" title="Nghiệm riêng Xp">${formatMatrix(particular_solution)}</div>
                        <div class="flex justify-center items-center flex-wrap">
                            ${termHtml}
                        </div>
                    </div>
                </div>
                <p class="text-center text-sm text-gray-500 mt-2">Trong đó ma trận đầu tiên là nghiệm riêng, các ma trận cột sau là vector cơ sở của không gian null, và t<sub>k</sub> là các tham số tự do.</p>
            </div>
        `;
    } else if (result.status === 'no_solution' && (result.solution_matrix || (result.forward_steps && result.forward_steps.length > 0) ) ) {
        const last_matrix = result.solution_matrix || result.forward_steps[result.forward_steps.length - 1].matrix;
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Dạng ma trận cuối cùng cho thấy sự mâu thuẫn:</h4><div class="matrix-display">${formatMatrix(last_matrix)}</div></div>`;
    }
    return html;
}

function displaySvdResults(result) {
    let html = `<h3 class="result-heading">Kết Quả Phân Tích SVD (A = UΣVᵀ)</h3>`;
    // Nếu số cột của U, Sigma, V^T lớn (ví dụ > 8), hiển thị dọc, còn lại giữ dạng lưới ngang
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
        html += `
            <div class="mt-10">
                <h3 class="result-heading">Các Bước Tính Toán Trung Gian</h3>
                <div class="space-y-6">
                    <div><h4 class="font-medium text-gray-700">Ma trận AᵀA</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.A_transpose_A)}</div></div>
                    <div><h4 class="font-medium text-gray-700">Giá trị riêng của AᵀA (λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.eigenvalues_of_ATA.map(v => formatNumber(v)).join(', ')} ]</div></div>
                    <div><h4 class="font-medium text-gray-700">Giá trị kỳ dị (σ = √λ)</h4><div class="p-3 bg-gray-50 rounded-md text-sm font-mono">[ ${result.intermediate_steps.singular_values.map(v => formatNumber(v)).join(', ')} ]</div></div>
                    <div><h4 class="font-medium text-gray-700">Ma trận V</h4><div class="matrix-display">${formatMatrix(result.intermediate_steps.V_matrix)}</div></div>
                </div>
            </div>
        `;
    }
    resultsArea.innerHTML = html;
}

function displayGaussJordanResults(result) {
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
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách LU', result);
    // Hiển thị L, U, P nếu có
    if ((result.decomposition && (result.decomposition.L || result.decomposition.P)) || result.L) {
        html += `<div class="mt-10"><h3 class="result-heading">Các Ma Trận L, U${result.decomposition?.P ? ', P' : ''}</h3>`;
        html += `<div class="grid grid-cols-1 md:grid-cols-3 gap-8">`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận L</h4><div class="matrix-display">${formatMatrix(result.decomposition?.L || result.L)}</div></div>`;
        html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.decomposition?.U || result.U)}</div></div>`;
        if (result.decomposition?.P) {
            html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận P</h4><div class="matrix-display">${formatMatrix(result.decomposition.P)}</div></div>`;
        }
        html += `</div></div>`;
    }
    if (result.status === 'unique_solution') {
        html += `<div class="mt-10"><h3 class="result-heading">Các Bước Trung Gian</h3>`;
        if (result.intermediate_y) {
            html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Ly = PB, ta được ma trận Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
        }
        html += `</div>`;
        html += `<div class="mb-8"><h4 class="font-semibold text-gray-700 text-center text-xl mb-2">Nghiệm X:</h4><div class="matrix-display">${formatMatrix(result.solution)}</div></div>`;
    } else if (result.status === 'infinite_solutions') {
        // Xử lý nghiệm tổng quát dạng object hoặc array
        let gs = result.general_solution;
        let Xp = [];
        let nullspace = [];
        let num_free_vars = 0;
        if (gs) {
            Xp = gs.particular_solution || [];
            nullspace = gs.null_space_vectors || [];
            num_free_vars = (Array.isArray(nullspace) && nullspace.length > 0 && Array.isArray(nullspace[0])) ? nullspace[0].length : 0;
        }
        let termHtml = '';
        for (let i = 0; i < num_free_vars; i++) {
            const v_k = nullspace.map(row => [row[i]]);
            termHtml += `&nbsp; + &nbsp; t<sub>${i+1}</sub> &nbsp; <div class="matrix-display !inline-block">${formatMatrix(v_k)}</div>`;
        }
        html += `
            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center mb-4">
                <div class="flex justify-center items-center flex-wrap">
                    <span class="text-2xl mr-4">X &nbsp; = </span>
                    <div class="matrix-display !inline-block" title="Nghiệm riêng Xp">${formatMatrix(Xp)}</div>
                    <div class="flex justify-center items-center flex-wrap">
                        ${termHtml}
                    </div>
                </div>
            </div>
        `;
        html += `<p class="text-center text-sm text-gray-500 mt-2">Xp là nghiệm riêng (mỗi cột ứng với một vế phải), các ma trận cột sau là vector cơ sở của không gian null, và t<sub>k</sub> là các tham số tự do.</p>`;
    }
    resultsArea.innerHTML = html;
}

function displayCholeskyResults(result) {
    let html = displayGenericHptResults('Kết Quả Giải Hệ Bằng Phân Tách Cholesky', result);
    if (result.decomposition.M && result.transformation_message.includes('không đối xứng')) {
         html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Ma trận đối xứng M = AᵀA</h4><div class="matrix-display">${formatMatrix(result.decomposition.M)}</div></div>`;
    }
    html += `<div class="mt-10"><h3 class="result-heading">Các Bước Phân Tách</h3>`;
    html += `<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">`;
    html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận U</h4><div class="matrix-display">${formatMatrix(result.decomposition.U)}</div></div>`;
    html += `<div><h4 class="font-medium text-center text-gray-700">Ma trận Uᵀ (chuyển vị liên hợp)</h4><div class="matrix-display">${formatMatrix(result.decomposition.Ut)}</div></div>`;
    html += `</div>`;
    html += `<div class="mt-6"><h4 class="font-medium text-center text-gray-700">Giải Uᵀy = d, ta được ma trận Y:</h4><div class="matrix-display">${formatMatrix(result.intermediate_y)}</div></div>`;
    html += `</div>`;
    resultsArea.innerHTML = html;
}

// Đảm bảo bảng ma trận luôn scroll ngang nếu quá rộng
// XÓA style tạo viền bảng, chỉ giữ scroll ngang nếu muốn
const style = document.createElement('style');
style.innerHTML = `
    .matrix-container { overflow-x: auto; max-width: 100vw; }
    .matrix-table { border-collapse: collapse; }
    .matrix-table td { text-align: left; }
    @media (max-width: 600px) {
        .matrix-table td { min-width: 40px; font-size: 13px; }
    }
`;
document.head.appendChild(style);