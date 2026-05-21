// js/perfil.js
// Modal de perfil de usuario


const hostname = window.location.hostname || 'localhost';
const protocol = window.location.protocol;
const API_BASE = `gestor-ffeoe-mpj-production.up.railway.app`; // ASEGURAR de que el backend esté en este puerto



export async function abrirModalPerfil() {
    const token = localStorage.getItem('token');
    if (!token) return;

    document.getElementById('modal-perfil-usuario').classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('No autenticado');
        const user = await res.json();

        // Avatar con iniciales
        const initials = (user.full_name || user.email || 'U')
            .split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();

        document.getElementById('pm-avatar').textContent = initials;
        document.getElementById('pm-nombre').textContent = user.full_name || 'Sin nombre';
        document.getElementById('pm-email').textContent = user.email;

        const badge = document.getElementById('pm-role-badge');
        badge.textContent = user.role.toUpperCase();
        badge.className = 'role-badge' + (user.role === 'admin' ? ' role-admin' : '');

        // Seccion adicional solo para alumnos
        const alumnoSection = document.getElementById('pm-alumno-section');
        if (user.role !== 'alumno') {
            alumnoSection.classList.add('hidden');
            return;
        }

        alumnoSection.classList.remove('hidden');

        const alumRes = await fetch(`${API_BASE}/api/v1/alumnos/perfil/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!alumRes.ok) return;
        const alum = await alumRes.json();

        // Estado FCT
        const estadoEl = document.getElementById('pm-estado-fct');
        if (alum.empresa_asignada_id) {
            estadoEl.textContent = 'Asignado';
            estadoEl.className = 'status-assigned';
        } else {
            estadoEl.textContent = 'Pendiente';
            estadoEl.className = 'status-pending';
        }

        // Ciclo formativo
        let cicloText = 'Sin ciclo asignado';
        if (alum.ciclo_id) {
            try {
                const ciclosRes = await fetch(`${API_BASE}/api/v1/ciclos/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const ciclos = await ciclosRes.json();
                const found = ciclos.find(c => c.id === alum.ciclo_id);
                cicloText = found ? found.nombre : `Ciclo #${alum.ciclo_id}`;
            } catch (_) {
                cicloText = `Ciclo #${alum.ciclo_id}`;
            }
        }
        document.getElementById('pm-ciclo').textContent = cicloText;

        // Estado CV
        const cvEl = document.getElementById('pm-cv-status');
        if (alum.cv_path) {
            cvEl.innerHTML = `
                <div class="cv-status-ok">
                    <span>CV subido y activo</span>
                    <button type="button" class="btn-text-accent"
                        onclick="window.descargarCVAlumno(${alum.id}, '${alum.nombre} ${alum.apellido}')">
                        Descargar
                    </button>
                </div>`;
        } else {
            cvEl.innerHTML = `<div class="cv-status-missing">Sin CV subido aun. Accede a tu perfil para subirlo.</div>`;
        }

    } catch (err) {
        console.error('Error en modal de perfil:', err);
    }
}
