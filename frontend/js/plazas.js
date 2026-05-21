// js/plazas.js

const API_BASE_URL = `gestor-ffeoe-mpj-production.up.railway.app`;



let plazasAlumnos = [];
let plazasEmpresas = [];
let plazasProfesores = [];

// Función principal para cargar todos los datos de Plazas FCT
export async function loadPlazasData() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const empresasListContainer = document.getElementById('plazas-empresas-list');
    const alumnosListContainer = document.getElementById('plazas-sin-asignar-list');

    empresasListContainer.innerHTML = `
        <div class="text-center" style="padding: 40px; color: var(--text-secondary);">
            <div class="skeleton skeleton-text" style="width: 90%; height: 24px; margin-bottom: 12px;"></div>
            <div class="skeleton skeleton-text" style="width: 70%; height: 20px;"></div>
        </div>
    `;
    alumnosListContainer.innerHTML = `
        <div class="text-center" style="padding: 20px;">
            <div class="skeleton skeleton-text" style="width: 100%; height: 20px; margin-bottom: 8px;"></div>
            <div class="skeleton skeleton-text" style="width: 80%; height: 20px;"></div>
        </div>
    `;

    try {
        // Cargar en paralelo Alumnos, Empresas y Profesores
        const [alumnosRes, empresasRes, profesoresRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/v1/alumnos/`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${API_BASE_URL}/api/v1/empresas/`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${API_BASE_URL}/api/v1/profesores/`, { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        if (!alumnosRes.ok || !empresasRes.ok || !profesoresRes.ok) {
            throw new Error('Error al cargar datos del servidor');
        }

        plazasAlumnos = await alumnosRes.json();
        plazasEmpresas = await empresasRes.json();
        plazasProfesores = await profesoresRes.json();

        // Renderizar las vistas
        renderPlazasEmpresas();
        renderPlazasAlumnosSinAsignar();

        // Configurar buscadores en tiempo real
        setupPlazasSearch();

    } catch (error) {
        console.error('Error al cargar pantalla de plazas:', error);
        empresasListContainer.innerHTML = `<div class="text-center" style="color: #EF4444; padding: 40px;">Error al cargar la distribución de plazas FCT</div>`;
        alumnosListContainer.innerHTML = `<div class="text-center" style="color: #EF4444; padding: 20px;">Error al cargar alumnos</div>`;
    }
}

// Renderiza la columna izquierda: Empresas y Plazas (Asignadas y Vacías)
function renderPlazasEmpresas(filterText = '') {
    const container = document.getElementById('plazas-empresas-list');
    container.innerHTML = '';

    const filteredEmpresas = plazasEmpresas.filter(emp => 
        emp.nombre.toLowerCase().includes(filterText.toLowerCase())
    );

    if (filteredEmpresas.length === 0) {
        container.innerHTML = `<div class="text-center" style="color: var(--text-secondary); padding: 40px;">No se encontraron empresas</div>`;
        return;
    }

    filteredEmpresas.forEach(empresa => {
        // Alumnos asignados a esta empresa
        const asignados = plazasAlumnos.filter(al => al.empresa_asignada_id === empresa.id);
        
        // Plazas totales y vacías
        const plazasTotalesVisibles = asignados.length + empresa.plazas_totales;

        const card = document.createElement('div');
        card.className = 'data-card glass-panel card-padded';
        card.style.display = 'flex';
        card.style.flexDirection = 'column';
        card.style.gap = '14px';
        card.style.border = '1px solid var(--border-glass)';
        card.style.borderRadius = 'var(--radius-md)';
        card.style.transition = 'transform var(--trans-fast)';
        
        // Cabecera de la empresa
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.borderBottom = '1px solid var(--border-glass)';
        header.style.paddingBottom = '8px';

        header.innerHTML = `
            <div>
                <h4 style="font-size: 1.05rem; font-weight: 600; color: var(--text-primary); margin-bottom: 2px;">${empresa.nombre}</h4>
                <p style="font-size: 0.8rem; color: var(--text-muted);">CIF: ${empresa.cif} &bull; Contacto: ${empresa.contacto_nombre || 'No asignado'}</p>
            </div>
            <span style="background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                ${asignados.length} / ${plazasTotalesVisibles} Plazas
            </span>
        `;
        card.appendChild(header);

        // Listado de slots (plazas)
        const slotsContainer = document.createElement('div');
        slotsContainer.style.display = 'flex';
        slotsContainer.style.flexDirection = 'column';
        slotsContainer.style.gap = '8px';

        // Renderizar slots asignados
        asignados.forEach(alumno => {
            const slot = document.createElement('div');
            slot.setAttribute('draggable', 'true');
            slot.style.cursor = 'grab';
            slot.style.display = 'flex';
            slot.style.justifyContent = 'space-between';
            slot.style.alignItems = 'center';
            slot.style.padding = '10px 14px';
            slot.style.background = 'rgba(255,255,255,0.03)';
            slot.style.border = '1px solid rgba(255,255,255,0.06)';
            slot.style.borderRadius = 'var(--radius-sm)';
            slot.style.transition = 'all var(--trans-fast)';

            slot.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 4px; flex: 1;">
                    <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 6px;">
                        <span style="color: var(--text-muted); cursor: grab; font-size: 0.8rem; user-select: none;">☰</span>
                        👨‍🎓 ${alumno.nombre} ${alumno.apellido}
                    </span>
                    <div style="display: flex; gap: 14px; font-size: 0.78rem; color: var(--text-secondary); padding-left: 16px;">
                        <span><strong>Docente:</strong> ${alumno.tutor_docente_nombre || 'Pendiente'}</span>
                        <span><strong>Laboral:</strong> ${alumno.tutor_laboral_nombre || 'Pendiente'}</span>
                    </div>
                </div>
                <button type="button" class="btn-quitar-asignacion" data-alumno-id="${alumno.id}" style="background: rgba(239, 68, 68, 0.1); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius-sm); padding: 4px 8px; font-size: 0.75rem; cursor: pointer; display: flex; align-items: center; gap: 4px; font-family: inherit; font-weight: 500; transition: var(--trans-fast);">
                    ✕ Quitar
                </button>
            `;

            slot.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('alumno_id', String(alumno.id));
                e.dataTransfer.setData('alumno_nombre', `${alumno.nombre} ${alumno.apellido}`);
                slot.style.opacity = '0.5';
                slot.style.cursor = 'grabbing';
            });

            slot.addEventListener('dragend', () => {
                slot.style.opacity = '1';
                slot.style.cursor = 'grab';
            });

            // Agregar evento para quitar asignación
            slot.querySelector('.btn-quitar-asignacion').addEventListener('click', () => handleQuitarAsignacion(alumno.id));
            slotsContainer.appendChild(slot);
        });

        // Renderizar slots vacíos (zonas de Drop)
        for (let i = 0; i < empresa.plazas_totales; i++) {
            const slot = document.createElement('div');
            slot.className = 'plaza-dropzone';
            slot.setAttribute('data-empresa-id', empresa.id);
            slot.style.display = 'flex';
            slot.style.alignItems = 'center';
            slot.style.justifyContent = 'center';
            slot.style.padding = '12px';
            slot.style.border = '2px dashed var(--border-glass)';
            slot.style.borderRadius = 'var(--radius-sm)';
            slot.style.background = 'rgba(0, 0, 0, 0.1)';
            slot.style.color = 'var(--text-secondary)';
            slot.style.fontSize = '0.85rem';
            slot.style.fontStyle = 'italic';
            slot.style.transition = 'all var(--trans-fast)';
            slot.innerHTML = `📥 Arrastra un alumno aquí`;

            // Configurar Listeners de Drag and Drop programáticamente
            slot.addEventListener('dragover', (e) => {
                e.preventDefault();
                slot.style.borderStyle = 'solid';
                slot.style.borderColor = 'var(--accent-blue)';
                slot.style.background = 'rgba(59, 130, 246, 0.08)';
                slot.style.color = 'var(--accent-blue)';
            });

            slot.addEventListener('dragleave', () => {
                slot.style.borderStyle = 'dashed';
                slot.style.borderColor = 'var(--border-glass)';
                slot.style.background = 'rgba(0, 0, 0, 0.1)';
                slot.style.color = 'var(--text-secondary)';
            });

            slot.addEventListener('drop', (e) => {
                e.preventDefault();
                slot.style.borderStyle = 'dashed';
                slot.style.borderColor = 'var(--border-glass)';
                slot.style.background = 'rgba(0, 0, 0, 0.1)';
                slot.style.color = 'var(--text-secondary)';
                
                const alumnoId = e.dataTransfer.getData('alumno_id');
                const alumnoNombre = e.dataTransfer.getData('alumno_nombre');
                
                if (alumnoId) {
                    abrirModalTutorAsignacion(alumnoId, alumnoNombre, empresa.id, empresa.nombre, empresa.contacto_nombre);
                }
            });

            slotsContainer.appendChild(slot);
        }

        if (plazasTotalesVisibles === 0) {
            const noSlots = document.createElement('div');
            noSlots.style.textAlign = 'center';
            noSlots.style.color = 'var(--text-muted)';
            noSlots.style.fontSize = '0.85rem';
            noSlots.style.padding = '8px 0';
            noSlots.innerHTML = '⚠️ Esta empresa no tiene plazas pactadas asignadas';
            slotsContainer.appendChild(noSlots);
        }

        card.appendChild(slotsContainer);
        container.appendChild(card);
    });
}

// Renderiza la columna derecha: Alumnos sin Asignar (Draggables)
function renderPlazasAlumnosSinAsignar(filterText = '') {
    const container = document.getElementById('plazas-sin-asignar-list');
    container.innerHTML = '';

    const sinAsignar = plazasAlumnos.filter(al => 
        !al.empresa_asignada_id && 
        (`${al.nombre} ${al.apellido}`).toLowerCase().includes(filterText.toLowerCase())
    );

    if (sinAsignar.length === 0) {
        container.innerHTML = `<div class="text-center" style="color: var(--text-secondary); padding: 30px;">Ningún alumno sin asignar</div>`;
        return;
    }

    sinAsignar.forEach(alumno => {
        const item = document.createElement('div');
        item.className = 'alumno-draggable-item';
        item.setAttribute('draggable', 'true');
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.gap = '12px';
        item.style.padding = '10px 14px';
        item.style.background = 'rgba(255,255,255,0.04)';
        item.style.border = '1px solid var(--border-glass)';
        item.style.borderRadius = 'var(--radius-sm)';
        item.style.cursor = 'grab';
        item.style.transition = 'all var(--trans-fast)';

        item.innerHTML = `
            <span style="color: var(--text-muted); font-size: 1rem; user-select: none;">☰</span>
            <div style="display: flex; flex-direction: column; gap: 2px; flex: 1;">
                <span style="font-size: 0.88rem; font-weight: 600; color: var(--text-primary);">${alumno.nombre} ${alumno.apellido}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted);">${alumno.email} &bull; ${alumno.dni || 'Sin DNI'}</span>
            </div>
        `;

        // Eventos de arrastre
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('alumno_id', String(alumno.id));
            e.dataTransfer.setData('alumno_nombre', `${alumno.nombre} ${alumno.apellido}`);
            item.style.opacity = '0.5';
            item.style.cursor = 'grabbing';
        });

        item.addEventListener('dragend', () => {
            item.style.opacity = '1';
            item.style.cursor = 'grab';
        });

        container.appendChild(item);
    });
}

// Configuración de los buscadores
function setupPlazasSearch() {
    const searchEmpresa = document.getElementById('plazas-search-empresa');
    const searchAlumno = document.getElementById('plazas-search-alumno');

    // Remove existing listeners by cloning
    const newSearchEmpresa = searchEmpresa.cloneNode(true);
    searchEmpresa.parentNode.replaceChild(newSearchEmpresa, searchEmpresa);
    newSearchEmpresa.addEventListener('input', (e) => {
        renderPlazasEmpresas(e.target.value);
    });

    const newSearchAlumno = searchAlumno.cloneNode(true);
    searchAlumno.parentNode.replaceChild(newSearchAlumno, searchAlumno);
    newSearchAlumno.addEventListener('input', (e) => {
        renderPlazasAlumnosSinAsignar(e.target.value);
    });
}

// Actualizar el display de información del tutor laboral seleccionado
function actualizarTutorLaboralInfo(nombreTutor, empresaId) {
    const infoDisplay = document.getElementById('at-tutor-laboral-info-display');
    if (!infoDisplay) return;

    if (!nombreTutor || nombreTutor === '-- Selecciona Tutor Laboral --') {
        infoDisplay.style.display = 'none';
        infoDisplay.innerHTML = '';
        return;
    }

    // Buscar empresa
    const empIdInt = parseInt(empresaId);
    const empresa = plazasEmpresas.find(e => e.id === empIdInt);
    
    let tutorInfo = null;

    if (empresa) {
        // 1. ¿Es el contacto principal de la empresa?
        const isPrimary = (empresa.contacto_nombre && empresa.contacto_nombre.trim() === nombreTutor.trim()) || 
                          (empresa.contacto && empresa.contacto.trim() === nombreTutor.trim());
        if (isPrimary) {
            tutorInfo = {
                nombre: empresa.contacto_nombre || empresa.contacto || nombreTutor,
                email: empresa.contacto_email || empresa.email || null,
                telefono: empresa.contacto_telefono || empresa.telefono || null,
                dni: empresa.contacto_dni || null,
                tipo: 'Contacto Principal'
            };
        } else if (empresa.tutores && Array.isArray(empresa.tutores)) {
            // 2. ¿Es uno de los tutores adicionales?
            const foundTutor = empresa.tutores.find(t => t.nombre && t.nombre.trim() === nombreTutor.trim());
            if (foundTutor) {
                tutorInfo = {
                    nombre: foundTutor.nombre,
                    email: foundTutor.email,
                    telefono: foundTutor.telefono,
                    dni: foundTutor.dni,
                    tipo: 'Personal / Tutor'
                };
            }
        }
    }

    // Si es un tutor personalizado creado en el acto (no guardado en empresa)
    if (!tutorInfo) {
        tutorInfo = {
            nombre: nombreTutor,
            email: null,
            telefono: null,
            dni: null,
            tipo: 'Personalizado'
        };
    }

    // Renderizar display
    infoDisplay.style.display = 'flex';
    infoDisplay.style.flexDirection = 'column';
    infoDisplay.style.gap = '6px';
    infoDisplay.style.background = 'rgba(255, 255, 255, 0.04)';
    infoDisplay.style.border = '1px solid rgba(255, 255, 255, 0.12)';
    infoDisplay.style.borderRadius = 'var(--radius-sm)';
    infoDisplay.style.padding = '12px';

    infoDisplay.innerHTML = `
        <div style="font-weight: 600; color: var(--accent-blue); display: flex; align-items: center; gap: 6px; font-size: 0.9rem;">
            <span>👤</span> ${tutorInfo.nombre}
            <span style="font-size: 0.72rem; font-weight: 600; background: rgba(59, 130, 246, 0.15); color: #93c5fd; padding: 2px 8px; border-radius: 20px; margin-left: auto;">
                ${tutorInfo.tipo}
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-top: 4px; font-size: 0.8rem; color: var(--text-secondary);">
            <div><strong>🪪 DNI:</strong> <span style="font-family: monospace;">${tutorInfo.dni || 'No disponible'}</span></div>
            <div><strong>📧 Email:</strong> ${tutorInfo.email || 'No disponible'}</div>
            <div><strong>📞 Tel:</strong> ${tutorInfo.telefono || 'No disponible'}</div>
        </div>
    `;
}

// Abrir el Modal de Asignación de Tutores
function abrirModalTutorAsignacion(alumnoId, alumnoNombre, empresaId, empresaNombre, contactoNombre) {
    document.getElementById('at-alumno-id').value = alumnoId;
    document.getElementById('at-empresa-id').value = empresaId;
    document.getElementById('at-alumno-nombre').textContent = alumnoNombre;
    document.getElementById('at-empresa-nombre').textContent = empresaNombre;

    // Resetear custom dropdown de tutor laboral
    const optionsContainer = document.getElementById('at-tutor-laboral-options');
    const displayEl = document.getElementById('at-tutor-laboral-display');
    const hiddenInput = document.getElementById('at-tutor-laboral');
    const wrapper = document.getElementById('at-tutor-laboral-wrapper');

    optionsContainer.innerHTML = '';
    displayEl.textContent = '-- Selecciona Tutor Laboral --';
    displayEl.classList.add('placeholder');
    hiddenInput.value = '';
    wrapper.classList.remove('open');

    // Resetear display de info
    const infoDisplay = document.getElementById('at-tutor-laboral-info-display');
    if (infoDisplay) {
        infoDisplay.style.display = 'none';
        infoDisplay.innerHTML = '';
    }

    // Helper para añadir items al dropdown
    function addItem(value, text, isSelected = false, extraClass = '') {
        const div = document.createElement('div');
        div.className = 'custom-dropdown-item' + (extraClass ? ' ' + extraClass : '') + (isSelected ? ' selected' : '');
        div.dataset.value = value;
        div.textContent = text;
        if (isSelected) {
            displayEl.textContent = text;
            displayEl.classList.remove('placeholder');
            hiddenInput.value = value;
        }
        optionsContainer.appendChild(div);
    }

    // Recopilar contactos únicos de empresas y alumnos
    const contactosUnicos = new Set();

    plazasEmpresas.forEach(emp => {
        if (emp.contacto_nombre && emp.contacto_nombre.trim()) contactosUnicos.add(emp.contacto_nombre.trim());
        if (emp.contacto && emp.contacto.trim()) contactosUnicos.add(emp.contacto.trim());
        if (emp.tutores && Array.isArray(emp.tutores)) {
            emp.tutores.forEach(t => { if (t.nombre && t.nombre.trim()) contactosUnicos.add(t.nombre.trim()); });
        }
    });

    plazasAlumnos.forEach(al => {
        if (al.tutor_laboral_nombre && al.tutor_laboral_nombre.trim() && al.tutor_laboral_nombre.trim() !== 'Pendiente de Asignar') {
            contactosUnicos.add(al.tutor_laboral_nombre.trim());
        }
    });

    console.log('Contactos únicos para dropdown:', Array.from(contactosUnicos));

    // Primero el contacto de esta empresa (preseleccionado)
    const currentContacto = contactoNombre ? contactoNombre.trim() : '';
    if (currentContacto) {
        addItem(currentContacto, `⭐ ${currentContacto} (Contacto de esta empresa)`, true);
        contactosUnicos.delete(currentContacto);
        actualizarTutorLaboralInfo(currentContacto, empresaId);
    } else {
        actualizarTutorLaboralInfo('', empresaId);
    }

    // El resto de contactos
    contactosUnicos.forEach(contacto => {
        const empAsociadas = plazasEmpresas.filter(emp => {
            const hasPrimary = emp.contacto_nombre && emp.contacto_nombre.trim() === contacto;
            const hasLegacy = emp.contacto && emp.contacto.trim() === contacto;
            const hasAdditional = emp.tutores && emp.tutores.some(t => t.nombre && t.nombre.trim() === contacto);
            return hasPrimary || hasLegacy || hasAdditional;
        });
        const label = empAsociadas.length > 0
            ? `${contacto} (${empAsociadas.map(e => e.nombre).join(', ')})`
            : contacto;
        addItem(contacto, label);
    });

    // Si no hay ningún contacto aún, mostrar mensaje informativo
    if (optionsContainer.children.length === 0) {
        const div = document.createElement('div');
        div.className = 'custom-dropdown-item item-disabled';
        div.textContent = '⚠️ Sin contactos — añade uno con la opción de abajo';
        optionsContainer.appendChild(div);
    }

    // Opción escribir personalizado
    addItem('OTRO', '➕ Añadir tutor personalizado...', false, 'item-otro');

    // Cargar select de profesores docentes (nativo, sin problemas)
    const select = document.getElementById('at-tutor-docente');
    select.innerHTML = '<option value="">-- Selecciona Tutor Docente --</option>';
    plazasProfesores.forEach(prof => {
        const opt = document.createElement('option');
        opt.value = prof.id;
        opt.textContent = prof.full_name || prof.email;
        select.appendChild(opt);
    });

    const modal = document.getElementById('modal-asignar-tutors');
    modal.classList.add('active');
}

// Cerrar Modal
function cerrarModalTutors() {
    const modal = document.getElementById('modal-asignar-tutors');
    modal.classList.remove('active');
    document.getElementById('form-asignar-tutors').reset();
    // También cerrar el dropdown custom si está abierto
    const wrapper = document.getElementById('at-tutor-laboral-wrapper');
    if (wrapper) wrapper.classList.remove('open');
    const hiddenInput = document.getElementById('at-tutor-laboral');
    if (hiddenInput) hiddenInput.value = '';
    const displayEl = document.getElementById('at-tutor-laboral-display');
    if (displayEl) { displayEl.textContent = '-- Selecciona Tutor Laboral --'; displayEl.classList.add('placeholder'); }
    
    // Resetear horas al valor por defecto
    const horasInput = document.getElementById('at-horas-practicas');
    if (horasInput) horasInput.value = 380;

    // Ocultar y limpiar el display de info del tutor
    const infoDisplay = document.getElementById('at-tutor-laboral-info-display');
    if (infoDisplay) {
        infoDisplay.style.display = 'none';
        infoDisplay.innerHTML = '';
    }
}

// Registrar eventos del modal al inicializar
export function initPlazasEvents() {
    document.getElementById('btn-close-asignar-tutors').addEventListener('click', cerrarModalTutors);
    document.getElementById('btn-cancelar-asignar-tutors').addEventListener('click', cerrarModalTutors);

    // --- Custom Dropdown Tutor Laboral ---
    const laboralWrapper = document.getElementById('at-tutor-laboral-wrapper');
    const laboralTrigger = document.getElementById('at-tutor-laboral-trigger');
    const laboralOptions = document.getElementById('at-tutor-laboral-options');
    const laboralDisplay = document.getElementById('at-tutor-laboral-display');
    const laboralHidden = document.getElementById('at-tutor-laboral');

    // Abrir/cerrar al hacer clic en el trigger
    laboralTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        laboralWrapper.classList.toggle('open');
    });

    laboralTrigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); laboralWrapper.classList.toggle('open'); }
        if (e.key === 'Escape') laboralWrapper.classList.remove('open');
    });

    // Seleccionar una opción
    laboralOptions.addEventListener('click', (e) => {
        const item = e.target.closest('.custom-dropdown-item');
        if (!item || !item.dataset.value) return;

        const empresaId = document.getElementById('at-empresa-id').value;

        if (item.dataset.value === 'OTRO') {
            laboralWrapper.classList.remove('open');
            const nuevoTutor = prompt('Introduce el nombre del tutor laboral:');
            if (nuevoTutor && nuevoTutor.trim()) {
                laboralHidden.value = nuevoTutor.trim();
                laboralDisplay.textContent = nuevoTutor.trim();
                laboralDisplay.classList.remove('placeholder');
                actualizarTutorLaboralInfo(nuevoTutor.trim(), empresaId);
            }
        } else {
            laboralHidden.value = item.dataset.value;
            laboralDisplay.textContent = item.textContent;
            laboralDisplay.classList.remove('placeholder');
            laboralOptions.querySelectorAll('.custom-dropdown-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            laboralWrapper.classList.remove('open');
            actualizarTutorLaboralInfo(item.dataset.value, empresaId);
        }
    });

    // Cerrar si se hace clic fuera
    document.addEventListener('click', () => {
        if (laboralWrapper) laboralWrapper.classList.remove('open');
    });

    document.getElementById('form-asignar-tutors').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('token');
        if (!token) return;

        const alumnoId = document.getElementById('at-alumno-id').value;
        const empresaId = document.getElementById('at-empresa-id').value;
        const docenteId = document.getElementById('at-tutor-docente').value;
        const laboralNombre = document.getElementById('at-tutor-laboral').value;
        const horas = parseInt(document.getElementById('at-horas-practicas').value) || 380;

        // Armar URL con query params opcionales
        let url = `${API_BASE_URL}/api/v1/asignaciones/${alumnoId}/${empresaId}`;
        const params = [`horas=${horas}`];
        if (docenteId) params.push(`tutor_docente_id=${docenteId}`);
        if (laboralNombre) params.push(`tutor_laboral_nombre=${encodeURIComponent(laboralNombre)}`);
        url += `?${params.join('&')}`;

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Error al guardar la asignación');
            }

            cerrarModalTutors();
            
            // Recargar pantalla de plazas silenciosamente
            loadPlazasData();

        } catch (error) {
            console.error('Error al guardar asignación:', error);
            alert(`Error: ${error.message}`);
        }
    });

    // Configurar columna derecha (Alumnos sin Asignar) como zona de Drop para Desasignar
    const sinAsignarContainer = document.getElementById('plazas-sin-asignar-list');
    
    sinAsignarContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        sinAsignarContainer.style.background = 'rgba(255, 255, 255, 0.04)';
        sinAsignarContainer.style.border = '2px dashed var(--accent-blue)';
    });

    sinAsignarContainer.addEventListener('dragleave', () => {
        sinAsignarContainer.style.background = '';
        sinAsignarContainer.style.border = '';
    });

    sinAsignarContainer.addEventListener('drop', async (e) => {
        e.preventDefault();
        sinAsignarContainer.style.background = '';
        sinAsignarContainer.style.border = '';

        const alumnoId = e.dataTransfer.getData('alumno_id');
        if (alumnoId) {
            // Buscar si el alumno ya está asignado a alguna empresa
            const alumno = plazasAlumnos.find(al => al.id === parseInt(alumnoId));
            if (alumno && alumno.empresa_asignada_id) {
                // Quitar la asignación de forma completamente silenciosa e instantánea
                await ejecutarQuitarAsignacionSilenciosa(alumno.id);
            }
        }
    });
}

// Quitar asignación de forma completamente silenciosa (sin confirm ni alert)
async function ejecutarQuitarAsignacionSilenciosa(alumnoId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/asignaciones/${alumnoId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'Error al eliminar la asignación');
        }

        loadPlazasData();

    } catch (error) {
        console.error('Error al quitar asignación silenciosa:', error);
    }
}

// Quitar Asignación (desde botón Quitar) - ahora también silenciosa e instantánea
async function handleQuitarAsignacion(alumnoId) {
    await ejecutarQuitarAsignacionSilenciosa(alumnoId);
}

