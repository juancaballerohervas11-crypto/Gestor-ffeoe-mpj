// js/main.js

const API_BASE_URL = 'http://localhost:8000'; // Asegúrate de que el backend esté corriendo en este puerto

// Variables de estado global
let currentUserRole = null;
let currentUserEmail = null;
let allAlumnos = [];
let cicloMapGlobal = {};

document.addEventListener('DOMContentLoaded', () => {
    // Verificar sesión al cargar
    checkSession();

    // Configurar event listeners
    document.getElementById('btn-refresh').addEventListener('click', loadDashboardData);
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('btn-logout').addEventListener('click', handleLogout);
    
    // Navegación Real
    document.getElementById('nav-dashboard').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('dashboard-view');
    });
    document.getElementById('nav-ciclos').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('ciclos-view');
    });
    document.getElementById('nav-alumnos').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('alumnos-view');
    });
    document.getElementById('nav-empresas').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('empresas-view');
    });
    document.getElementById('nav-profesores').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('profesores-view');
    });
    document.getElementById('nav-config').addEventListener('click', (e) => {
        e.preventDefault();
        switchView('config-view');
    });

    // Ciclos buttons
    document.getElementById('btn-nuevo-ciclo').addEventListener('click', () => abrirModalCiclo());
    document.getElementById('btn-close-ciclo').addEventListener('click', () => closeModal('modal-ciclo'));
    document.getElementById('btn-cancelar-ciclo').addEventListener('click', () => closeModal('modal-ciclo'));
    document.getElementById('form-ciclo').addEventListener('submit', guardarCiclo);

    // Asignar Profesor buttons
    document.getElementById('btn-close-asig-prof').addEventListener('click', () => closeModal('modal-asignar-profesor'));
    document.getElementById('btn-cancelar-asig-prof').addEventListener('click', () => closeModal('modal-asignar-profesor'));
    document.getElementById('form-asignar-profesor').addEventListener('submit', guardarAsignarProfesor);

    // Gestionar Alumnos buttons
    document.getElementById('btn-close-gest-alumnos').addEventListener('click', () => closeModal('modal-gestionar-alumnos'));
    document.getElementById('btn-vincular-alumno').addEventListener('click', guardarAsignarAlumno);

    // Alumnos (Gestor) buttons
    document.getElementById('btn-nuevo-alumno').addEventListener('click', () => abrirModalAlumno());
    document.getElementById('btn-close-alumno').addEventListener('click', () => closeModal('modal-alumno'));
    document.getElementById('btn-cancelar-alumno').addEventListener('click', () => closeModal('modal-alumno'));
    document.getElementById('form-alumno').addEventListener('submit', guardarAlumno);
    document.getElementById('btn-importar-alumnos-csv').addEventListener('click', () => abrirModalImportarCSV());
    document.getElementById('btn-close-importar-csv').addEventListener('click', () => closeModal('modal-importar-csv'));
    document.getElementById('btn-cancelar-importar-csv').addEventListener('click', () => closeModal('modal-importar-csv'));
    document.getElementById('form-importar-csv').addEventListener('submit', importarAlumnosCSV);
    document.getElementById('alumnos-buscar').addEventListener('input', filtrarAlumnosTabla);

    // Empresas buttons
    document.getElementById('btn-nueva-empresa').addEventListener('click', () => abrirModalEmpresa());
    document.getElementById('btn-close-empresa').addEventListener('click', () => closeModal('modal-empresa'));
    document.getElementById('btn-cancelar-empresa').addEventListener('click', () => closeModal('modal-empresa'));
    document.getElementById('form-empresa').addEventListener('submit', guardarEmpresa);
    
    document.getElementById('btn-importar-empresas-csv').addEventListener('click', () => openModal('modal-importar-empresas'));
    document.getElementById('btn-close-importar-empresas').addEventListener('click', () => closeModal('modal-importar-empresas'));
    document.getElementById('btn-cancelar-importar-empresas').addEventListener('click', () => closeModal('modal-importar-empresas'));
    document.getElementById('form-importar-empresas').addEventListener('submit', importarEmpresasCSV);
    document.getElementById('empresas-buscar').addEventListener('input', filtrarEmpresasTabla);

    // Profesores buttons
    document.getElementById('btn-nuevo-profesor').addEventListener('click', () => abrirModalProfesor());
    document.getElementById('btn-close-profesor').addEventListener('click', () => closeModal('modal-profesor'));
    document.getElementById('btn-cancelar-profesor').addEventListener('click', () => closeModal('modal-profesor'));
    document.getElementById('form-profesor').addEventListener('submit', guardarProfesor);
    document.getElementById('profesores-buscar').addEventListener('input', filtrarProfesoresTabla);

    // Bitacora buttons
    document.getElementById('btn-close-bitacora').addEventListener('click', () => closeModal('modal-bitacora'));
    document.getElementById('form-bitacora-nuevo').addEventListener('submit', guardarBitacora);

    // Configuración buttons
    document.getElementById('form-config-perfil').addEventListener('submit', guardarConfigPerfil);
    
    // Theme switching logic
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const selectedTheme = btn.getAttribute('data-theme');
            document.body.setAttribute('data-theme', selectedTheme);
            localStorage.setItem('selected-theme', selectedTheme);
        });
    });

    // Load theme setting if saved
    const savedTheme = localStorage.getItem('selected-theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }

    // Alumno (Self Profile) buttons
    document.getElementById('form-alumno-perfil-self').addEventListener('submit', guardarMiPerfil);
    document.getElementById('form-alumno-cv').addEventListener('submit', subirMiCV);
});

function checkSession() {
    const token = localStorage.getItem('token');
    const overlay = document.getElementById('login-overlay');
    
    if (token) {
        overlay.classList.remove('active');
        loadUserProfile();
        switchView('dashboard-view');
    } else {
        overlay.classList.add('active');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    const btnSubmit = document.getElementById('btn-login-submit');

    errorEl.textContent = '';
    btnSubmit.disabled = true;
    btnSubmit.querySelector('span').textContent = 'Iniciando...';

    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error de credenciales' }));
            throw new Error(errData.detail || 'Email o contraseña incorrectos');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        
        document.getElementById('login-overlay').classList.remove('active');
        await loadUserProfile();
        switchView('dashboard-view');

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.querySelector('span').textContent = 'Entrar';
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    document.getElementById('login-overlay').classList.add('active');
    
    // Limpiar variables globales
    currentUserRole = null;
    currentUserEmail = null;
    allAlumnos = [];
    
    // Limpiar perfil sidebar
    document.getElementById('user-avatar').textContent = '--';
    document.getElementById('user-name').textContent = 'Cargando...';
    document.getElementById('user-role').textContent = '...';
}

async function loadUserProfile() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error al obtener perfil');

        const user = await response.json();
        
        currentUserRole = user.role;
        currentUserEmail = user.email;
        
        // Actualizar sidebar
        document.getElementById('user-name').textContent = user.full_name || user.email;
        document.getElementById('user-role').textContent = user.role.toUpperCase();
        
        const initials = (user.full_name || 'U')
            .split(' ')
            .map(n => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
        document.getElementById('user-avatar').textContent = initials;

        // Ocultar tabs si el usuario es alumno
        const navCiclos = document.getElementById('nav-ciclos').parentElement;
        const navEmpresas = document.getElementById('nav-empresas').parentElement;
        const navProfesores = document.getElementById('nav-profesores').parentElement;
        
        if (currentUserRole === 'alumno') {
            navCiclos.style.display = 'none';
            navEmpresas.style.display = 'none';
            navProfesores.style.display = 'none';
        } else {
            navCiclos.style.display = 'block';
            navEmpresas.style.display = 'block';
            navProfesores.style.display = 'block';
        }

    } catch (error) {
        console.error('Error loading user profile:', error);
        handleLogout();
    }
}

function switchView(viewId) {
    const views = ['dashboard-view', 'ciclos-view', 'alumnos-view', 'empresas-view', 'profesores-view', 'config-view'];
    views.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === viewId) {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        }
    });

    const navMapping = {
        'dashboard-view': 'nav-dashboard',
        'ciclos-view': 'nav-ciclos',
        'alumnos-view': 'nav-alumnos',
        'empresas-view': 'nav-empresas',
        'profesores-view': 'nav-profesores',
        'config-view': 'nav-config'
    };
    
    const activeNavId = navMapping[viewId];
    const navItems = document.querySelectorAll('.sidebar-nav li');
    navItems.forEach(item => {
        const link = item.querySelector('a');
        if (link && link.id === activeNavId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    if (viewId === 'dashboard-view') {
        loadDashboardData();
    } else if (viewId === 'ciclos-view') {
        loadCiclosData();
    } else if (viewId === 'alumnos-view') {
        loadAlumnosData();
    } else if (viewId === 'empresas-view') {
        loadEmpresasData();
    } else if (viewId === 'profesores-view') {
        loadProfesoresData();
    } else if (viewId === 'config-view') {
        loadConfigData();
    }
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

async function loadDashboardData() {
    const token = localStorage.getItem('token');
    if (!token) {
        checkSession();
        return;
    }

    showLoadingState();
    
    try {
        const response = await fetch(`${API_BASE_URL}/stats/resumen`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.status === 401 || response.status === 403) {
            handleLogout();
            return;
        }

        if (!response.ok) {
            throw new Error("No se pudo obtener datos del servidor.");
        }

        const data = await response.json();
        updateDashboardUI(data);

    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        loadMockData();
    }
}

function showLoadingState() {
    const ids = [
        'stat-alumnos-totales', 
        'stat-alumnos-asignados', 
        'stat-alumnos-pendientes', 
        'stat-plazas-disponibles',
        'stat-empresas-totales',
        'stat-profesores-totales'
    ];
    
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = '<div class="skeleton skeleton-text" style="width: 40px; height: 30px;"></div>';
        }
    });

    const tbody = document.getElementById('empresas-tbody');
    tbody.innerHTML = Array(3).fill(`
        <tr>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text"></div></td>
            <td><div class="skeleton skeleton-text" style="width: 30px;"></div></td>
            <td><div class="skeleton skeleton-text" style="width: 60px;"></div></td>
        </tr>
    `).join('');
}

function updateDashboardUI(data) {
    animateValue('stat-alumnos-totales', 0, data.alumnos.total, 1000);
    animateValue('stat-alumnos-asignados', 0, data.alumnos.asignados, 1000);
    animateValue('stat-alumnos-pendientes', 0, data.alumnos.pendientes, 1000);
    animateValue('stat-plazas-disponibles', 0, data.empresas.plazas_disponibles_totales, 1000);
    animateValue('stat-empresas-totales', 0, data.empresas.total || 0, 1000);
    animateValue('stat-profesores-totales', 0, data.profesores ? data.profesores.total : 0, 1000);

    const tbody = document.getElementById('empresas-tbody');
    const badge = document.getElementById('badge-ofertas-count');
    
    const ofertas = data.empresas.listado_ofertas || [];
    badge.textContent = `${ofertas.length} empresas`;

    if (ofertas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center" style="color: var(--text-muted); padding: 30px;">
                    No hay ofertas de empresas disponibles en este momento.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    ofertas.forEach((oferta, index) => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in';
        tr.style.animationDelay = `${index * 0.1}s`;
        
        tr.innerHTML = `
            <td>
                <div class="company-name">${oferta.nombre}</div>
            </td>
            <td>
                <div class="contact-info">${oferta.contacto || 'No especificado'}</div>
            </td>
            <td>
                <span class="plazas-badge">${oferta.plazas} plazas</span>
            </td>
            <td>
                <button class="btn-text">Ver detalle</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}


// ==========================================
// SECCIÓN DE GESTIÓN DE CICLOS (CRUD)
// ==========================================

async function loadCiclosData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('ciclos-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center" style="padding: 20px;">
                <div class="skeleton skeleton-text" style="width: 80%; margin: 0 auto; height: 24px;"></div>
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/ciclos/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error al obtener los ciclos');

        const ciclos = await response.json();
        document.getElementById('badge-ciclos-count').textContent = `${ciclos.length} ciclos`;

        if (ciclos.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center" style="color: var(--text-muted); padding: 30px;">
                        No hay ciclos formativos registrados. Haz clic en "Nuevo Ciclo" para empezar.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = '';
        ciclos.forEach((ciclo, index) => {
            const tr = document.createElement('tr');
            tr.className = 'fade-in';
            tr.style.animationDelay = `${index * 0.05}s`;

            const profNames = ciclo.profesores && ciclo.profesores.length > 0
                ? ciclo.profesores.map(p => p.full_name || p.email).join(', ')
                : 'Ninguno asignado';

            tr.innerHTML = `
                <td><strong class="company-name">${ciclo.nombre}</strong></td>
                <td>${ciclo.ano_inicio} - ${ciclo.ano_fin}</td>
                <td>
                    <button class="btn-text-accent" onclick="abrirGestionarAlumnos(${ciclo.id})">
                        👨‍🎓 ${ciclo.alumnos ? ciclo.alumnos.length : 0} alumnos
                    </button>
                </td>
                <td>
                    <button class="btn-text" onclick="abrirAsignarProfesor(${ciclo.id})">
                        👤 ${profNames}
                    </button>
                </td>
                <td>
                    <button class="btn-text" onclick="abrirModalCiclo(${ciclo.id}, '${ciclo.nombre}', ${ciclo.ano_inicio}, ${ciclo.ano_fin})" style="margin-right: 8px;">✏️ Editar</button>
                    <button class="btn-text-delete" onclick="eliminarCiclo(${ciclo.id})">🗑️ Borrar</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error('Error loading ciclos:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center" style="color: #EF4444; padding: 20px;">
                    Error al cargar los ciclos formativos.
                </td>
            </tr>
        `;
    }
}

function abrirModalCiclo(id = null, nombre = '', inicio = '', fin = '') {
    const titleEl = document.getElementById('modal-ciclo-title');
    const idEl = document.getElementById('ciclo-id');
    const nombreEl = document.getElementById('ciclo-nombre');
    const inicioEl = document.getElementById('ciclo-inicio');
    const finEl = document.getElementById('ciclo-fin');
    const errorEl = document.getElementById('ciclo-form-error');

    errorEl.textContent = '';
    
    if (id) {
        titleEl.textContent = 'Modificar Ciclo Académico';
        idEl.value = id;
        nombreEl.value = nombre;
        inicioEl.value = inicio;
        finEl.value = fin;
    } else {
        titleEl.textContent = 'Nuevo Ciclo Académico';
        idEl.value = '';
        nombreEl.value = '';
        inicioEl.value = new Date().getFullYear();
        finEl.value = new Date().getFullYear() + 1;
    }

    openModal('modal-ciclo');
}

async function guardarCiclo(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const id = document.getElementById('ciclo-id').value;
    const nombre = document.getElementById('ciclo-nombre').value;
    const inicio = parseInt(document.getElementById('ciclo-inicio').value);
    const fin = parseInt(document.getElementById('ciclo-fin').value);
    const errorEl = document.getElementById('ciclo-form-error');
    const btnGuardar = document.getElementById('btn-guardar-ciclo');

    btnGuardar.disabled = true;
    errorEl.textContent = '';

    const url = id ? `${API_BASE_URL}/api/v1/ciclos/${id}` : `${API_BASE_URL}/api/v1/ciclos/`;
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                nombre: nombre,
                ano_inicio: inicio,
                ano_fin: fin
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al procesar ciclo' }));
            throw new Error(errData.detail || 'Error al guardar el ciclo formativo');
        }

        closeModal('modal-ciclo');
        loadCiclosData();

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnGuardar.disabled = false;
    }
}

async function eliminarCiclo(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este ciclo? Todos los alumnos de este ciclo quedarán desasignados de forma segura.')) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/ciclos/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al eliminar ciclo' }));
            throw new Error(errData.detail || 'Error al eliminar el ciclo');
        }

        loadCiclosData();

    } catch (error) {
        alert(error.message);
    }
}

async function abrirAsignarProfesor(cicloId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    document.getElementById('asig-prof-ciclo-id').value = cicloId;
    const select = document.getElementById('asig-prof-select');
    select.innerHTML = '<option value="">Cargando profesores...</option>';
    document.getElementById('asig-prof-error').textContent = '';

    openModal('modal-asignar-profesor');

    try {
        const profResponse = await fetch(`${API_BASE_URL}/api/v1/profesores/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!profResponse.ok) throw new Error('Error al listar profesores');
        const profesores = await profResponse.json();

        const ciclosResponse = await fetch(`${API_BASE_URL}/api/v1/ciclos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const ciclos = await ciclosResponse.json();
        const ciclo = ciclos.find(c => c.id === cicloId);
        const yaAsignadosIds = ciclo && ciclo.profesores ? ciclo.profesores.map(p => p.id) : [];

        const disponibles = profesores.filter(p => !yaAsignadosIds.includes(p.id));

        if (disponibles.length === 0) {
            select.innerHTML = '<option value="">Todos los profesores ya están asignados a este ciclo</option>';
            return;
        }

        select.innerHTML = '<option value="">Selecciona un profesor...</option>';
        disponibles.forEach(prof => {
            const opt = document.createElement('option');
            opt.value = prof.id;
            opt.textContent = `${prof.full_name || prof.email} (${prof.role.toUpperCase()})`;
            select.appendChild(opt);
        });

    } catch (error) {
        select.innerHTML = '<option value="">Error al cargar los profesores</option>';
        console.error(error);
    }
}

async function guardarAsignarProfesor(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const cicloId = document.getElementById('asig-prof-ciclo-id').value;
    const profesorId = parseInt(document.getElementById('asig-prof-select').value);
    const errorEl = document.getElementById('asig-prof-error');
    const btnSubmit = document.getElementById('btn-submit-asig-prof');

    if (!profesorId) {
        errorEl.textContent = 'Por favor, selecciona un profesor';
        return;
    }

    btnSubmit.disabled = true;
    errorEl.textContent = '';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/ciclos/${cicloId}/asignar_profesor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ profesor_id: profesorId })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al asignar profesor' }));
            throw new Error(errData.detail || 'Error al asignar profesor al ciclo');
        }

        closeModal('modal-asignar-profesor');
        loadCiclosData();

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
    }
}

async function abrirGestionarAlumnos(cicloId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    document.getElementById('gest-alumnos-ciclo-id').value = cicloId;
    document.getElementById('asig-alumno-error').textContent = '';
    
    openModal('modal-gestionar-alumnos');
    loadCicloAlumnos(cicloId);
}

async function loadCicloAlumnos(cicloId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('ciclo-alumnos-tbody');
    const select = document.getElementById('asig-alumno-select');

    tbody.innerHTML = '<tr><td colspan="3" class="text-center" style="padding:20px;">Cargando alumnos...</td></tr>';
    select.innerHTML = '<option value="">Cargando alumnos...</option>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Error al listar alumnos');
        const alumnos = await response.json();

        const matriculados = alumnos.filter(a => a.ciclo_id === cicloId);
        const sinCiclo = alumnos.filter(a => a.ciclo_id === null || a.ciclo_id === undefined);

        if (matriculados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center" style="color: var(--text-secondary); padding: 20px;">No hay alumnos matriculados en este ciclo.</td></tr>';
        } else {
            tbody.innerHTML = '';
            matriculados.forEach(alum => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${alum.nombre} ${alum.apellido}</strong></td>
                    <td>${alum.email}</td>
                    <td>
                        <button class="btn-text-delete" onclick="desvincularAlumno(${cicloId}, ${alum.id})">Desmatricular</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        if (sinCiclo.length === 0) {
            select.innerHTML = '<option value="">Todos los alumnos ya están matriculados en un ciclo</option>';
        } else {
            select.innerHTML = '<option value="">Seleccionar alumno sin ciclo...</option>';
            sinCiclo.forEach(alum => {
                const opt = document.createElement('option');
                opt.value = alum.id;
                opt.textContent = `${alum.nombre} ${alum.apellido} (${alum.email})`;
                select.appendChild(opt);
            });
        }

    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center" style="color: #EF4444; padding:20px;">Error al cargar alumnos</td></tr>';
        select.innerHTML = '<option value="">Error al cargar alumnos</option>';
        console.error(error);
    }
}

async function guardarAsignarAlumno() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const cicloId = document.getElementById('gest-alumnos-ciclo-id').value;
    const alumnoId = parseInt(document.getElementById('asig-alumno-select').value);
    const errorEl = document.getElementById('asig-alumno-error');
    const btnMatricular = document.getElementById('btn-vincular-alumno');

    if (!alumnoId) {
        errorEl.textContent = 'Por favor, selecciona un alumno';
        return;
    }

    btnMatricular.disabled = true;
    errorEl.textContent = '';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/ciclos/${cicloId}/asignar_alumno/${alumnoId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al asignar alumno' }));
            throw new Error(errData.detail || 'Error al asignar alumno al ciclo');
        }

        await loadCicloAlumnos(parseInt(cicloId));
        loadCiclosData();

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnMatricular.disabled = false;
    }
}

async function desvincularAlumno(cicloId, alumnoId) {
    if (!confirm('¿Estás seguro de que deseas retirar a este alumno de este ciclo formativo?')) return;
    
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/ciclos/${cicloId}/desasignar_alumno/${alumnoId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al retirar alumno' }));
            throw new Error(errData.detail || 'Error al retirar alumno del ciclo');
        }

        await loadCicloAlumnos(cicloId);
        loadCiclosData();

    } catch (error) {
        alert(error.message);
    }
}


// ==========================================
// SECCIÓN DE ALUMNADO (DUAL GESTOR / ALUMNO)
// ==========================================

async function loadAlumnosData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const gestorContainer = document.getElementById('alumnos-gestor-container');
    const selfProfileContainer = document.getElementById('alumno-self-profile');

    if (currentUserRole === 'alumno') {
        gestorContainer.classList.add('hidden');
        selfProfileContainer.classList.remove('hidden');
        loadMiPerfilData();
    } else {
        selfProfileContainer.classList.add('hidden');
        gestorContainer.classList.remove('hidden');
        loadAlumnosGestorList();
    }
}

// LÓGICA DE GESTIÓN (ADMINISTRADORES / PROFESORES)
async function loadAlumnosGestorList() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('alumnos-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center" style="padding: 20px;">
                <div class="skeleton skeleton-text" style="width: 80%; margin: 0 auto; height: 24px;"></div>
            </td>
        </tr>
    `;

    try {
        // Cargar mapa de ciclos
        const ciclosResponse = await fetch(`${API_BASE_URL}/api/v1/ciclos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const ciclos = await ciclosResponse.json();
        cicloMapGlobal = {};
        ciclos.forEach(c => { cicloMapGlobal[c.id] = c.nombre; });

        // Cargar alumnos
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Error al listar alumnos');
        allAlumnos = await response.json();
        
        // Calcular estadísticas
        const total = allAlumnos.length;
        const asignados = allAlumnos.filter(a => a.empresa_asignada_id).length;
        const pendientes = allAlumnos.filter(a => !a.empresa_asignada_id).length;
        const cvs = allAlumnos.filter(a => a.cv_path).length;

        // Mostrar estadísticas con micro-animaciones numéricas
        animateValue('gestor-stat-alumnos-totales', 0, total, 1000);
        animateValue('gestor-stat-alumnos-asignados', 0, asignados, 1000);
        animateValue('gestor-stat-alumnos-pendientes', 0, pendientes, 1000);
        animateValue('gestor-stat-alumnos-cvs', 0, cvs, 1000);

        renderAlumnosTabla(allAlumnos);

    } catch (error) {
        console.error('Error al cargar alumnos:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color: #EF4444; padding:20px;">Error al cargar directorio de alumnos</td></tr>';
    }
}

function renderAlumnosTabla(alumnos) {
    const tbody = document.getElementById('alumnos-tbody');
    document.getElementById('badge-alumnos-count').textContent = `${alumnos.length} alumnos`;

    if (alumnos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center" style="color: var(--text-muted); padding: 30px;">
                    No se encontraron estudiantes registrados.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    alumnos.forEach((alum, index) => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in';
        tr.style.animationDelay = `${index * 0.05}s`;

        const cicloNombre = alum.ciclo_id ? (cicloMapGlobal[alum.ciclo_id] || `Ciclo #${alum.ciclo_id}`) : 'Sin matricular';
        
        let cvButton = '<span style="color: var(--text-muted); font-size: 0.85rem;">No subido</span>';
        if (alum.cv_path) {
            cvButton = `
                <button class="btn-text-accent" onclick="descargarCVAlumno(${alum.id}, '${alum.nombre} ${alum.apellido}')" title="Descargar currículum en PDF">
                    📄 Descargar CV
                </button>
            `;
        }

        tr.innerHTML = `
            <td>
                <strong class="company-name">${alum.nombre} ${alum.apellido}</strong>
            </td>
            <td>
                <div style="font-size: 0.9rem;">${alum.email}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${alum.telefono || 'Sin teléfono'}</div>
            </td>
            <td>
                <span class="badge" style="background: rgba(255,255,255,0.03); color: var(--text-primary); border-color: var(--border-glass);">
                    ${cicloNombre}
                </span>
            </td>
            <td>${cvButton}</td>
            <td>
                <button class="btn-text" onclick="abrirModalAlumno(${alum.id}, '${alum.nombre}', '${alum.apellido}', '${alum.email}', '${alum.telefono || ''}')" style="margin-right: 8px;">✏️ Editar</button>
                <button class="btn-text-delete" onclick="eliminarAlumno(${alum.id})">🗑️ Borrar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarAlumnosTabla() {
    const q = document.getElementById('alumnos-buscar').value.toLowerCase().trim();
    if (!q) {
        renderAlumnosTabla(allAlumnos);
        return;
    }

    const filtrados = allAlumnos.filter(a => {
        const nombreCompleto = `${a.nombre} ${a.apellido}`.toLowerCase();
        const email = a.email.toLowerCase();
        const telefono = (a.telefono || '').toLowerCase();
        const ciclo = a.ciclo_id ? (cicloMapGlobal[a.ciclo_id] || '').toLowerCase() : 'sin matricular';

        return nombreCompleto.includes(q) || 
               email.includes(q) || 
               telefono.includes(q) || 
               ciclo.includes(q);
    });

    renderAlumnosTabla(filtrados);
}

function abrirModalAlumno(id = null, nombre = '', apellido = '', email = '', telefono = '') {
    const titleEl = document.getElementById('modal-alumno-title');
    const idEl = document.getElementById('alumno-id');
    const nombreEl = document.getElementById('alumno-nombre');
    const apellidoEl = document.getElementById('alumno-apellido');
    const emailEl = document.getElementById('alumno-email');
    const telefonoEl = document.getElementById('alumno-telefono');
    const errorEl = document.getElementById('alumno-form-error');

    errorEl.textContent = '';
    
    if (id) {
        titleEl.textContent = 'Modificar Ficha de Alumno';
        idEl.value = id;
        nombreEl.value = nombre;
        apellidoEl.value = apellido;
        emailEl.value = email;
        telefonoEl.value = telefono;
    } else {
        titleEl.textContent = 'Nuevo Estudiante';
        idEl.value = '';
        nombreEl.value = '';
        apellidoEl.value = '';
        emailEl.value = '';
        telefonoEl.value = '';
    }

    openModal('modal-alumno');
}

async function guardarAlumno(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const id = document.getElementById('alumno-id').value;
    const nombre = document.getElementById('alumno-nombre').value;
    const apellido = document.getElementById('alumno-apellido').value;
    const email = document.getElementById('alumno-email').value;
    const telefono = document.getElementById('alumno-telefono').value;
    const errorEl = document.getElementById('alumno-form-error');
    const btnGuardar = document.getElementById('btn-guardar-alumno');

    btnGuardar.disabled = true;
    errorEl.textContent = '';

    const url = id ? `${API_BASE_URL}/api/v1/alumnos/${id}` : `${API_BASE_URL}/api/v1/alumnos/`;
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                nombre: nombre,
                apellido: apellido,
                email: email,
                telefono: telefono
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al guardar alumno' }));
            throw new Error(errData.detail || 'Error al guardar la ficha del alumno');
        }

        closeModal('modal-alumno');
        loadAlumnosGestorList();

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnGuardar.disabled = false;
    }
}

async function eliminarAlumno(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar permanentemente la ficha de este estudiante?')) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al eliminar alumno' }));
            throw new Error(errData.detail || 'Error al borrar el estudiante');
        }

        loadAlumnosGestorList();

    } catch (error) {
        alert(error.message);
    }
}

function abrirModalImportarCSV() {
    document.getElementById('importar-csv-error').textContent = '';
    document.getElementById('importar-csv-success').textContent = '';
    document.getElementById('csv-file').value = '';
    openModal('modal-importar-csv');
}

async function importarAlumnosCSV(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const fileInput = document.getElementById('csv-file');
    const errorEl = document.getElementById('importar-csv-error');
    const successEl = document.getElementById('importar-csv-success');
    const btnSubmit = document.getElementById('btn-submit-importar-csv');

    if (fileInput.files.length === 0) {
        errorEl.textContent = 'Por favor, selecciona un archivo CSV';
        return;
    }

    btnSubmit.disabled = true;
    errorEl.textContent = '';
    successEl.textContent = '';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/importar-csv`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error en la importación masiva' }));
            throw new Error(errData.detail || 'Error al procesar el archivo CSV');
        }

        const data = await response.json();
        successEl.textContent = `✅ Importación completada. Alumnos nuevos: ${data.nuevos_alumnos}. Saltados: ${data.saltados}.`;
        
        setTimeout(() => {
            closeModal('modal-importar-csv');
            loadAlumnosGestorList();
        }, 2000);

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
    }
}

async function descargarCVAlumno(alumnoId, nombreAlumno) {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/${alumnoId}/descargar-cv`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Error al descargar el CV o el archivo no existe.');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `CV_${nombreAlumno.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        alert(error.message);
    }
}


// LÓGICA DE ALUMNO PROPIO (SELF PERFIL)
async function loadMiPerfilData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    document.getElementById('alumno-self-error').textContent = '';
    document.getElementById('alumno-self-success').textContent = '';
    document.getElementById('alumno-cv-error').textContent = '';
    document.getElementById('alumno-cv-success').textContent = '';

    try {
        // Cargar mapa de ciclos
        const ciclosResponse = await fetch(`${API_BASE_URL}/api/v1/ciclos/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const ciclos = await ciclosResponse.json();
        const localCicloMap = {};
        ciclos.forEach(c => { localCicloMap[c.id] = c.nombre; });

        // Cargar perfil
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/perfil/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('No se pudo cargar el perfil del alumno logueado');
        const alum = await response.json();

        // Rellenar formulario de contacto
        document.getElementById('alumno-self-nombre').value = `${alum.nombre} ${alum.apellido}`;
        document.getElementById('alumno-self-email').value = alum.email;
        document.getElementById('alumno-self-telefono').value = alum.telefono || '';

        // Rellenar ciclo y estado de asignación
        const cicloNombre = alum.ciclo_id ? (localCicloMap[alum.ciclo_id] || `Ciclo #${alum.ciclo_id}`) : 'Ninguno asignado aún';
        document.getElementById('alumno-self-ciclo').textContent = cicloNombre;

        const estadoEl = document.getElementById('alumno-self-estado');
        if (alum.empresa_asignada_id) {
            estadoEl.textContent = 'ASIGNADO';
            estadoEl.style.color = 'var(--accent-green)';
        } else {
            estadoEl.textContent = 'PENDIENTE DE ASIGNACIÓN';
            estadoEl.style.color = 'var(--accent-orange)';
        }

        // Rellenar estado del CV
        const cvContainer = document.getElementById('cv-status-container');
        if (alum.cv_path) {
            cvContainer.innerHTML = `
                <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); padding: 12px; border-radius: var(--radius-sm); color: var(--text-primary); display: flex; align-items: center; justify-content: space-between;">
                    <span>📄 Currículum subido y activo en el sistema</span>
                    <button type="button" class="btn-text-accent" onclick="descargarCVAlumno(${alum.id}, '${alum.nombre} ${alum.apellido}')" style="font-weight:600;">
                        Descargar/Ver CV ⬇️
                    </button>
                </div>
            `;
        } else {
            cvContainer.innerHTML = `
                <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 12px; border-radius: var(--radius-sm); color: #F87171;">
                    ❌ No has subido ningún currículum aún. Sube un archivo PDF para que los tutores y empresas puedan seleccionarte.
                </div>
            `;
        }

    } catch (error) {
        console.error('Error loading self profile:', error);
        document.getElementById('alumno-self-error').textContent = 'Error al cargar tu ficha de perfil';
    }
}

async function guardarMiPerfil(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const email = document.getElementById('alumno-self-email').value;
    const telefono = document.getElementById('alumno-self-telefono').value;
    const errorEl = document.getElementById('alumno-self-error');
    const successEl = document.getElementById('alumno-self-success');
    const btnSubmit = document.getElementById('btn-guardar-self-perfil');

    errorEl.textContent = '';
    successEl.textContent = '';
    btnSubmit.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/perfil/me`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                email: email,
                telefono: telefono
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al actualizar perfil' }));
            throw new Error(errData.detail || 'Error al actualizar tus datos');
        }

        successEl.textContent = '¡Datos actualizados con éxito!';
        
        // Recargar perfil del sidebar si cambiaron credenciales
        await loadUserProfile();
        setTimeout(() => { loadMiPerfilData(); }, 1500);

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
    }
}

async function subirMiCV(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const fileInput = document.getElementById('alumno-cv-file');
    const errorEl = document.getElementById('alumno-cv-error');
    const successEl = document.getElementById('alumno-cv-success');
    const btnSubmit = document.getElementById('btn-subir-cv');

    if (fileInput.files.length === 0) {
        errorEl.textContent = 'Por favor, selecciona un archivo PDF';
        return;
    }

    const file = fileInput.files[0];
    if (file.type !== 'application/pdf') {
        errorEl.textContent = 'El archivo debe ser de tipo PDF únicamente';
        return;
    }

    errorEl.textContent = '';
    successEl.textContent = '';
    btnSubmit.disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/alumnos/perfil/me/cv`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al subir currículum' }));
            throw new Error(errData.detail || 'Error al procesar la subida del currículum');
        }

        successEl.textContent = '¡Currículum PDF subido y guardado correctamente!';
        fileInput.value = '';

        setTimeout(() => { loadMiPerfilData(); }, 1500);

    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
    }
}


// ==========================================
// EXPOSICIÓN GLOBAL PARA MANIPULACIÓN EN DOM
// ==========================================

window.abrirModalCiclo = abrirModalCiclo;
window.eliminarCiclo = eliminarCiclo;
window.abrirAsignarProfesor = abrirAsignarProfesor;
window.abrirGestionarAlumnos = abrirGestionarAlumnos;
window.desvincularAlumno = desvincularAlumno;
window.closeModal = closeModal;

window.abrirModalAlumno = abrirModalAlumno;
window.eliminarAlumno = eliminarAlumno;
window.descargarCVAlumno = descargarCVAlumno;

window.abrirModalEmpresa = abrirModalEmpresa;
window.eliminarEmpresa = eliminarEmpresa;
window.abrirBitacoraEmpresa = abrirBitacoraEmpresa;
window.abrirModalProfesor = abrirModalProfesor;
window.eliminarProfesor = eliminarProfesor;


// ==========================================
// SISTEMA DE ANIMACIONES Y MOCKS
// ==========================================

function animateValue(id, start, end, duration) {
    if (start === end) {
        const el = document.getElementById(id);
        if (el) el.textContent = end;
        return;
    }
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 4);
        const currentVal = Math.floor(easeProgress * (end - start) + start);
        const el = document.getElementById(id);
        if (el) {
            el.textContent = currentVal;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        }
    };
    window.requestAnimationFrame(step);
}

function loadMockData() {
    setTimeout(() => {
        const mockData = {
            alumnos: {
                total: 124,
                asignados: 89,
                pendientes: 35
            },
            empresas: {
                total: 24,
                plazas_disponibles_totales: 42,
                listado_ofertas: [
                    { nombre: "Tech Solutions S.L. (MOCK)", plazas: 5, contacto: "rrhh@techsolutions.es" },
                    { nombre: "Desarrollo Web Madrid (MOCK)", plazas: 3, contacto: "contacto@dwmadrid.com" },
                    { nombre: "Sistemas Inteligentes SA (MOCK)", plazas: 8, contacto: "info@sistemasintel.com" },
                    { nombre: "Innovación Digital (MOCK)", plazas: 2, contacto: "talento@innovadigital.es" },
                    { nombre: "Cloud Networks (MOCK)", plazas: 4, jobs: "jobs@cloudnetworks.net" }
                ]
            },
            profesores: {
                total: 8
            }
        };
        updateDashboardUI(mockData);
    }, 800);
}


// ==========================================
// SECCIÓN DE GESTIÓN DE EMPRESAS (CRUD)
// ==========================================
let allEmpresas = [];

async function loadEmpresasData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('empresas-listado-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="skeleton skeleton-text" style="width: 80%; height: 20px; margin: 10px auto;"></div>
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/empresas/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al listar empresas');
        allEmpresas = await response.json();
        renderEmpresasTabla(allEmpresas);
    } catch (error) {
        console.error('Error loading empresas:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: #F87171;">Error al cargar empresas colaboradoras</td></tr>`;
    }
}

function renderEmpresasTabla(empresas) {
    const tbody = document.getElementById('empresas-listado-tbody');
    const countEl = document.getElementById('badge-empresas-count');
    
    if (countEl) countEl.textContent = `${empresas.length} empresas`;
    
    if (empresas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-secondary); padding: 30px;">No se encontraron empresas registradas</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    empresas.forEach((empresa, index) => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in';
        tr.style.animationDelay = `${index * 0.05}s`;
        
        tr.innerHTML = `
            <td><strong style="color: var(--text-primary); font-size: 0.95rem;">${empresa.nombre}</strong></td>
            <td><code>${empresa.cif}</code></td>
            <td><span style="color: var(--text-secondary);">${empresa.contacto || 'Sin contacto'}</span></td>
            <td>
                <span class="plazas-badge" style="background: rgba(16,185,129,0.15); color: var(--accent-green); padding: 4px 10px; border-radius: var(--radius-sm); font-weight:600; font-size:0.85rem;">
                    ${empresa.plazas_totales} plazas
                </span>
            </td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary" onclick="abrirBitacoraEmpresa(${empresa.id}, '${empresa.nombre}')" style="padding: 6px 12px; font-size: 0.8rem; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); color: #60A5FA;">
                        📞 Bitácora
                    </button>
                    <button class="btn btn-secondary" onclick="abrirModalEmpresa(${empresa.id}, '${empresa.nombre}', '${empresa.cif}', '${empresa.contacto || ''}', ${empresa.plazas_totales})" style="padding: 6px 12px; font-size: 0.8rem;">
                        ✏️ Editar
                    </button>
                    <button class="btn btn-secondary" onclick="eliminarEmpresa(${empresa.id})" style="padding: 6px 12px; font-size: 0.8rem; border-color: rgba(239,68,68,0.2); color: #F87171; background: rgba(239,68,68,0.05);">
                        🗑️ Borrar
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarEmpresasTabla() {
    const query = document.getElementById('empresas-buscar').value.toLowerCase();
    const filtrados = allEmpresas.filter(e => 
        e.nombre.toLowerCase().includes(query) || 
        e.cif.toLowerCase().includes(query) ||
        (e.contacto && e.contacto.toLowerCase().includes(query))
    );
    renderEmpresasTabla(filtrados);
}

function abrirModalEmpresa(id = '', nombre = '', cif = '', contacto = '', plazas = 0) {
    document.getElementById('empresa-id').value = id;
    document.getElementById('empresa-nombre').value = nombre;
    document.getElementById('empresa-cif').value = cif;
    document.getElementById('empresa-contacto').value = contacto;
    document.getElementById('empresa-plazas').value = plazas;
    
    document.getElementById('empresa-form-error').textContent = '';
    document.getElementById('modal-empresa-title').textContent = id ? 'Editar Empresa' : 'Nueva Empresa Colaboradora';
    
    openModal('modal-empresa');
}

async function guardarEmpresa(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const id = document.getElementById('empresa-id').value;
    const nombre = document.getElementById('empresa-nombre').value;
    const cif = document.getElementById('empresa-cif').value;
    const contacto = document.getElementById('empresa-contacto').value;
    const plazas = parseInt(document.getElementById('empresa-plazas').value) || 0;

    const errorEl = document.getElementById('empresa-form-error');
    errorEl.textContent = '';

    const url = id ? `${API_BASE_URL}/api/v1/empresas/${id}` : `${API_BASE_URL}/api/v1/empresas/`;
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                nombre: nombre,
                cif: cif,
                contacto: contacto,
                plazas_totales: plazas
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al procesar solicitud' }));
            throw new Error(errData.detail || 'Error al guardar la empresa');
        }

        closeModal('modal-empresa');
        loadEmpresasData();
    } catch (error) {
        errorEl.textContent = error.message;
    }
}

async function eliminarEmpresa(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta empresa? Se borrará también su historial de contactos.')) return;
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/empresas/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Error al eliminar la empresa');
        loadEmpresasData();
    } catch (error) {
        alert(error.message);
    }
}

async function importarEmpresasCSV(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const fileInput = document.getElementById('importar-empresas-csv-file');
    const errorEl = document.getElementById('importar-empresas-error');
    const successEl = document.getElementById('importar-empresas-success');
    const btnSubmit = document.getElementById('btn-submit-importar-empresas');

    errorEl.textContent = '';
    successEl.textContent = '';
    btnSubmit.disabled = true;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/empresas/importar-empresas`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al importar CSV' }));
            throw new Error(errData.detail || 'Fallo al procesar importación');
        }

        const res = await response.json();
        successEl.textContent = `¡Importación con éxito! Creados: ${res.nuevos_registros}, Saltados/Duplicados: ${res.duplicados_o_invalidos_saltados}`;
        fileInput.value = '';
        setTimeout(() => {
            closeModal('modal-importar-empresas');
            loadEmpresasData();
        }, 2000);
    } catch (error) {
        errorEl.textContent = error.message;
    } finally {
        btnSubmit.disabled = false;
    }
}

// ==========================================
// SECCIÓN DE BITÁCORA DE CONTACTOS
// ==========================================
async function abrirBitacoraEmpresa(empresaId, nombre) {
    document.getElementById('bitacora-empresa-id').value = empresaId;
    document.getElementById('modal-bitacora-subtitle').textContent = `Empresa: ${nombre}`;
    document.getElementById('bitacora-observaciones').value = '';
    document.getElementById('bitacora-plazas').value = '0';
    document.getElementById('bitacora-form-error').textContent = '';
    
    await cargarBitacoraHistorial(empresaId);
    openModal('modal-bitacora');
}

async function cargarBitacoraHistorial(empresaId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('bitacora-tbody');
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">Cargando bitácora de llamadas...</td></tr>`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/empresas/${empresaId}/contactos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al cargar contactos');
        const logs = await response.json();

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-secondary); padding: 15px;">No hay llamadas ni reuniones registradas para esta empresa</td></tr>`;
            return;
        }

        tbody.innerHTML = '';
        logs.forEach(log => {
            const date = new Date(log.fecha_contacto).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
            const tr = document.createElement('tr');
            
            let badgeColor = 'var(--text-secondary)';
            if (log.estado === 'Acepta') badgeColor = 'var(--accent-green)';
            if (log.estado === 'Rechaza') badgeColor = '#F87171';
            if (log.estado === 'Pendiente') badgeColor = 'var(--accent-orange)';

            tr.innerHTML = `
                <td><code>${date}</code></td>
                <td><strong>${log.nombre_profesor || 'Tutor'}</strong></td>
                <td><span style="color: ${badgeColor}; font-weight:600;">${log.estado}</span></td>
                <td>${log.plazas_ofrecidas} plazas</td>
                <td><span style="font-size: 0.85rem; color: var(--text-secondary);">${log.observaciones || ''}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: #F87171;">Error al cargar bitácoras</td></tr>`;
    }
}

async function guardarBitacora(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const empresaId = parseInt(document.getElementById('bitacora-empresa-id').value);
    const estado = document.getElementById('bitacora-estado').value;
    const plazas = parseInt(document.getElementById('bitacora-plazas').value) || 0;
    const obs = document.getElementById('bitacora-observaciones').value;

    const errorEl = document.getElementById('bitacora-form-error');
    errorEl.textContent = '';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/contactos/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                empresa_id: empresaId,
                estado: estado,
                plazas_ofrecidas: plazas,
                observaciones: obs,
                horas_totales: 0
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al registrar contacto' }));
            throw new Error(errData.detail || 'Fallo al enviar bitácora');
        }

        document.getElementById('bitacora-observaciones').value = '';
        document.getElementById('bitacora-plazas').value = '0';
        
        await cargarBitacoraHistorial(empresaId);
        loadDashboardData();
    } catch (error) {
        errorEl.textContent = error.message;
    }
}


// ==========================================
// SECCIÓN DE GESTIÓN DE PROFESORES (CRUD)
// ==========================================
let allProfesores = [];

async function loadProfesoresData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const tbody = document.getElementById('profesores-listado-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="4" class="text-center">
                <div class="skeleton skeleton-text" style="width: 80%; height: 20px; margin: 10px auto;"></div>
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/profesores/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al listar profesores');
        allProfesores = await response.json();
        renderProfesoresTabla(allProfesores);
    } catch (error) {
        console.error('Error loading profesores:', error);
        tbody.innerHTML = `<tr><td colspan="4" class="text-center" style="color: #F87171;">Error al cargar directorio docente</td></tr>`;
    }
}

function renderProfesoresTabla(profesores) {
    const tbody = document.getElementById('profesores-listado-tbody');
    const countEl = document.getElementById('badge-profesores-count');
    
    if (countEl) countEl.textContent = `${profesores.length} profesores`;
    
    if (profesores.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 30px;">No se encontraron docentes registrados</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    profesores.forEach((profesor, index) => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in';
        tr.style.animationDelay = `${index * 0.05}s`;
        
        const isSelf = profesor.email === currentUserEmail;
        
        tr.innerHTML = `
            <td>
                <strong style="color: var(--text-primary); font-size: 0.95rem;">${profesor.full_name || 'Profesor'}</strong>
                ${isSelf ? '<span class="badge" style="background: var(--accent-blue); color: white; padding: 2px 6px; font-size:0.75rem; margin-left: 6px;">Tú</span>' : ''}
            </td>
            <td><code>${profesor.email}</code></td>
            <td>
                <span style="font-weight:600; color: ${profesor.role === 'admin' ? 'var(--accent-orange)' : 'var(--text-secondary)'}">
                    ${profesor.role.toUpperCase()}
                </span>
            </td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary" onclick="abrirModalProfesor(${profesor.id}, '${profesor.full_name || ''}', '${profesor.email}', '${profesor.role}')" style="padding: 6px 12px; font-size: 0.8rem;">
                        ✏️ Editar
                    </button>
                    <button class="btn btn-secondary" onclick="eliminarProfesor(${profesor.id})" ${isSelf ? 'disabled' : ''} style="padding: 6px 12px; font-size: 0.8rem; border-color: rgba(239,68,68,0.2); color: #F87171; background: rgba(239,68,68,0.05); opacity: ${isSelf ? 0.4 : 1}; cursor: ${isSelf ? 'not-allowed' : 'pointer'};">
                        🗑️ Borrar
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarProfesoresTabla() {
    const query = document.getElementById('profesores-buscar').value.toLowerCase();
    const filtrados = allProfesores.filter(p => 
        (p.full_name && p.full_name.toLowerCase().includes(query)) || 
        p.email.toLowerCase().includes(query) ||
        p.role.toLowerCase().includes(query)
    );
    renderProfesoresTabla(filtrados);
}

function abrirModalProfesor(id = '', nombre = '', email = '', rol = 'profesor') {
    document.getElementById('profesor-id').value = id;
    document.getElementById('profesor-nombre').value = nombre;
    document.getElementById('profesor-email').value = email;
    document.getElementById('profesor-rol').value = rol;
    document.getElementById('profesor-password').value = '';
    
    document.getElementById('profesor-form-error').textContent = '';
    document.getElementById('modal-profesor-title').textContent = id ? 'Editar Profesor / Tutor' : 'Nuevo Profesor / Tutor';
    
    const passGroup = document.getElementById('profesor-password-group');
    if (id) {
        passGroup.querySelector('label').textContent = 'Nueva Contraseña (Opcional)';
    } else {
        passGroup.querySelector('label').textContent = 'Contraseña';
    }
    
    openModal('modal-profesor');
}

async function guardarProfesor(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const id = document.getElementById('profesor-id').value;
    const nombre = document.getElementById('profesor-nombre').value;
    const email = document.getElementById('profesor-email').value;
    const password = document.getElementById('profesor-password').value;
    const rol = document.getElementById('profesor-rol').value;

    const errorEl = document.getElementById('profesor-form-error');
    errorEl.textContent = '';

    if (!id && !password) {
        errorEl.textContent = 'La contraseña es obligatoria para nuevos profesores';
        return;
    }

    const url = id ? `${API_BASE_URL}/api/v1/profesores/${id}` : `${API_BASE_URL}/api/v1/profesores/`;
    const method = id ? 'PUT' : 'POST';

    const bodyData = {
        full_name: nombre,
        email: email
    };
    
    if (password) bodyData.password = password;
    if (!id) bodyData.role = rol;

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(bodyData)
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al procesar solicitud' }));
            throw new Error(errData.detail || 'Error al guardar el profesor');
        }

        closeModal('modal-profesor');
        loadProfesoresData();
    } catch (error) {
        errorEl.textContent = error.message;
    }
}

async function eliminarProfesor(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este profesor del directorio? Se desvinculará de todos los ciclos asignados.')) return;
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/profesores/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Error al eliminar el profesor');
        loadProfesoresData();
    } catch (error) {
        alert(error.message);
    }
}


// ==========================================
// SECCIÓN DE CONFIGURACIÓN Y TEMA
// ==========================================
let currentUserId = null;

async function loadConfigData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const errorEl = document.getElementById('config-perfil-error');
    const successEl = document.getElementById('config-perfil-success');
    if (errorEl) errorEl.textContent = '';
    if (successEl) successEl.textContent = '';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('No se pudo obtener información de la cuenta');
        const user = await response.json();
        
        currentUserId = user.id;
        document.getElementById('config-email').value = user.email;
        document.getElementById('config-nombre').value = user.full_name || '';
        document.getElementById('config-password').value = '';
    } catch (error) {
        if (errorEl) errorEl.textContent = error.message;
    }
}

async function guardarConfigPerfil(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) return;

    const email = document.getElementById('config-email').value;
    const nombre = document.getElementById('config-nombre').value;
    const password = document.getElementById('config-password').value;

    const errorEl = document.getElementById('config-perfil-error');
    const successEl = document.getElementById('config-perfil-success');
    if (errorEl) errorEl.textContent = '';
    if (successEl) successEl.textContent = '';

    const bodyData = {
        email: email,
        full_name: nombre
    };
    if (password) bodyData.password = password;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/profesores/${currentUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(bodyData)
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: 'Error al actualizar credenciales' }));
            throw new Error(errData.detail || 'Fallo al guardar configuración');
        }

        if (successEl) successEl.textContent = '¡Perfil de cuenta actualizado correctamente!';
        await loadUserProfile();
        setTimeout(() => { loadConfigData(); }, 1500);
    } catch (error) {
        if (errorEl) errorEl.textContent = error.message;
    }
}
