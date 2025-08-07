// Habit tracker logic only

// Track dismissed popups for this session
const dismissedPopups = {};

// Habit Tracker (GitHub-style grid) for multiple habits
function renderAllHabits(habitsData) {
    const habitsList = document.getElementById('habits-list');
    habitsList.innerHTML = '';
    Object.entries(habitsData).forEach(([habitName, habitObj]) => {
        const container = document.createElement('div');
        container.className = 'habit-container';
        let showPopup = false;
        // --- Per-habit popup for today's completion ---
        const todayDate = new Date();
        const yyyy = todayDate.getFullYear();
        const mm = String(todayDate.getMonth() + 1).padStart(2, '0');
        const dd = String(todayDate.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}-${mm}-${dd}`;
        const isDoneToday = habitObj.dates && habitObj.dates[todayStr];
        if (!isDoneToday && !dismissedPopups[habitName]) {
            const popup = document.createElement('div');
            popup.className = 'habit-popup';
            popup.innerHTML = `
                <span>Task completed today?</span>
                <button class="icon-btn popup-btn tick" title="Mark as done">✔️</button>
                <button class="icon-btn popup-btn cross" title="Dismiss">✖️</button>
            `;
            popup.querySelector('.tick').onclick = () => {
                fetch('/api/habits', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ habit: habitName, date: todayStr })
                }).then(() => loadHabits());
            };
            popup.querySelector('.cross').onclick = () => {
                dismissedPopups[habitName] = true;
                popup.remove();
                container.classList.remove('show-popup');
            };
            container.appendChild(popup);
            showPopup = true;
        }
        if (showPopup) container.classList.add('show-popup');
        // Header with name and controls
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.justifyContent = 'space-between';
        header.style.width = '100%';
        // Habit name
        const title = document.createElement('h3');
        title.textContent = habitName;
        title.className = 'habit-name';
        title.style.flex = '1';
        header.appendChild(title);
        // Controls: color, apply, refresh as icons
        const controls = document.createElement('div');
        controls.className = 'habit-controls';
        // Color icon
        const colorBtn = document.createElement('button');
        colorBtn.className = 'icon-btn';
        colorBtn.title = 'Change color';
        colorBtn.innerHTML = '🎨';
        colorBtn.onclick = () => colorInput.click();
        // Hidden color input
        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.value = habitObj.color || '#39d353';
        colorInput.style.display = 'none';
        colorInput.oninput = () => {
            colorBtn.style.color = colorInput.value;
        };
        // Apply icon
        const applyBtn = document.createElement('button');
        applyBtn.className = 'icon-btn';
        applyBtn.title = 'Apply color';
        applyBtn.innerHTML = '✔️';
        applyBtn.onclick = () => {
            updateHabitColor(habitName, colorInput.value, () => {
                fetch('/api/habits').then(res => res.json()).then(data => {
                    const updatedHabit = data.habits[habitName];
                    if (updatedHabit) {
                        container.querySelectorAll('.habit-cell.done').forEach(cell => {
                            cell.style.background = updatedHabit.color || '#39d353';
                        });
                        colorInput.value = updatedHabit.color || '#39d353';
                        colorBtn.style.color = updatedHabit.color || '#39d353';
                    }
                });
            });
        };
        // Refresh icon
        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'icon-btn';
        refreshBtn.title = 'Refresh habit';
        refreshBtn.innerHTML = '⟳';
        refreshBtn.onclick = () => {
            fetch('/api/habits').then(res => res.json()).then(data => {
                const updatedHabit = data.habits[habitName];
                if (updatedHabit) {
                    container.querySelectorAll('.habit-cell.done').forEach(cell => {
                        cell.style.background = updatedHabit.color || '#39d353';
                    });
                    colorInput.value = updatedHabit.color || '#39d353';
                    colorBtn.style.color = updatedHabit.color || '#39d353';
                }
            });
        };
        controls.appendChild(colorBtn);
        controls.appendChild(colorInput);
        controls.appendChild(applyBtn);
        controls.appendChild(refreshBtn);
        header.appendChild(controls);
        // Three-dot menu
        const menuWrapper = document.createElement('div');
        menuWrapper.style.position = 'relative';
        const menuBtn = document.createElement('button');
        menuBtn.textContent = '⋮';
        menuBtn.className = 'menu-btn';
        menuBtn.style.background = 'none';
        menuBtn.style.border = 'none';
        menuBtn.style.fontSize = '1.3em';
        menuBtn.style.cursor = 'pointer';
        menuBtn.onclick = (e) => {
            e.stopPropagation();
            menuDropdown.style.display = menuDropdown.style.display === 'block' ? 'none' : 'block';
        };
        const menuDropdown = document.createElement('div');
        menuDropdown.className = 'menu-dropdown';
        menuDropdown.style.display = 'none';
        menuDropdown.style.position = 'absolute';
        menuDropdown.style.right = '0';
        menuDropdown.style.top = '28px';
        menuDropdown.style.background = '#232b2b';
        menuDropdown.style.border = '1px solid #2ecc40';
        menuDropdown.style.borderRadius = '8px';
        menuDropdown.style.boxShadow = '0 2px 8px #0006';
        menuDropdown.style.zIndex = '10';
        // Edit name option
        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit Name';
        editBtn.style.display = 'block';
        editBtn.style.width = '100%';
        editBtn.style.background = 'none';
        editBtn.style.border = 'none';
        editBtn.style.padding = '8px 16px';
        editBtn.style.cursor = 'pointer';
        editBtn.onclick = (e) => {
            e.stopPropagation();
            menuDropdown.style.display = 'none';
            // Replace title with input
            const input = document.createElement('input');
            input.type = 'text';
            input.value = habitName;
            input.className = 'edit-name-input';
            input.style.fontSize = '1.1em';
            input.style.width = '80%';
            title.replaceWith(input);
            input.focus();
            input.onblur = () => {
                const newName = input.value.trim() || habitName;
                if (newName !== habitName) {
                    fetch('/api/habits/rename', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ old: habitName, new: newName })
                    }).then(() => loadHabits());
                } else {
                    input.replaceWith(title);
                }
            };
            input.onkeydown = (ev) => {
                if (ev.key === 'Enter') input.blur();
            };
        };
        menuDropdown.appendChild(editBtn);
        // Delete option
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.style.display = 'block';
        deleteBtn.style.width = '100%';
        deleteBtn.style.background = 'none';
        deleteBtn.style.border = 'none';
        deleteBtn.style.padding = '8px 16px';
        deleteBtn.style.cursor = 'pointer';
        deleteBtn.style.color = '#ff4d4d';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            menuDropdown.style.display = 'none';
            if (confirm('Delete this habit?')) {
                fetch('/api/habits/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ habit: habitName })
                }).then(() => loadHabits());
            }
        };
        menuDropdown.appendChild(deleteBtn);
        menuWrapper.appendChild(menuBtn);
        menuWrapper.appendChild(menuDropdown);
        header.appendChild(menuWrapper);
        container.appendChild(header);
        // --- Improved grid: day labels in first column, months as blocks, all cells visible and aligned ---
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        // Monday as first day of week
        const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        const year = todayDate.getFullYear();
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'habit-matrix-wrapper';
        gridWrapper.style.overflowX = 'auto';
        gridWrapper.style.paddingBottom = '1em';
        // Outer grid: CSS grid, first column is day labels, then each month is a block
        const outerGrid = document.createElement('div');
        outerGrid.style.display = 'grid';
        // Calculate number of columns: 1 for day labels + sum of week columns for each month
        let monthWeekCounts = [];
        for (let m = 0; m < 12; m++) {
            // Monday as first day
            const firstDay = (new Date(year, m, 1).getDay() + 6) % 7;
            const daysInMonth = new Date(year, m + 1, 0).getDate();
            const totalCells = firstDay + daysInMonth;
            const weekCols = Math.ceil(totalCells / 7);
            monthWeekCounts.push(weekCols);
        }
        // Add 12px gap between months for clear separation
        const totalCols = 1 + monthWeekCounts.reduce((a, b) => a + b, 0) + 11; // 11 gaps between 12 months
        let gridTemplateCols = '60px';
        for (let i = 0; i < 12; i++) {
            gridTemplateCols += ` repeat(${monthWeekCounts[i]}, 16px)`;
            if (i < 11) gridTemplateCols += ' 12px';
        }
        outerGrid.style.gridTemplateColumns = gridTemplateCols;
        outerGrid.style.gap = '5px';
        // Day labels (first column, 7 rows)
        for (let row = 0; row < 7; row++) {
            const label = document.createElement('div');
            label.textContent = daysOfWeek[row];
            label.style.color = '#b0b0b0';
            label.style.fontSize = '0.95em';
            label.style.height = '16px';
            label.style.display = 'flex';
            label.style.alignItems = 'center';
            label.style.justifyContent = 'flex-end';
            label.style.paddingRight = '4px';
            label.style.gridRow = `${row + 2}`;
            label.style.gridColumn = '1';
            outerGrid.appendChild(label);
        }
        // Month labels (above each month block)
        let colStart = 2;
        for (let m = 0; m < 12; m++) {
            const weekCols = monthWeekCounts[m];
            const monthLabel = document.createElement('div');
            monthLabel.textContent = months[m];
            monthLabel.className = 'month-label';
            monthLabel.style.textAlign = 'center';
            monthLabel.style.fontWeight = 'bold';
            monthLabel.style.fontSize = '1em';
            monthLabel.style.color = '#f5f5f5';
            monthLabel.style.gridRow = '1';
            monthLabel.style.gridColumn = `${colStart} / span ${weekCols}`;
            monthLabel.style.borderLeft = m > 0 ? '2px solid #39d353' : 'none';
            monthLabel.style.paddingLeft = m > 0 ? '12px' : '0';
            monthLabel.style.paddingRight = '0';
            outerGrid.appendChild(monthLabel);
            colStart += weekCols + 1; // +1 for the gap
        }
        // Month day cells
        colStart = 2;
        for (let m = 0; m < 12; m++) {
            // Monday as first day
            const firstDay = (new Date(year, m, 1).getDay() + 6) % 7;
            const daysInMonth = new Date(year, m + 1, 0).getDate();
            const weekCols = monthWeekCounts[m];
            // Fill cells for this month
            let cellIdx = 0;
            for (let col = 0; col < weekCols; col++) {
                for (let row = 0; row < 7; row++) {
                    const gridPos = col * 7 + row;
                    let cellDiv;
                    if (gridPos < firstDay || cellIdx >= daysInMonth) {
                        // Empty cell (before 1st or after last day)
                        cellDiv = document.createElement('div');
                        cellDiv.className = 'habit-cell';
                        cellDiv.style.opacity = '0';
                    } else {
                        const day = cellIdx + 1;
                        const dateObj = new Date(year, m, day);
                        const dateStr = dateObj.toISOString().slice(0, 10);
                        const done = habitObj.dates && habitObj.dates[dateStr];
                        cellDiv = document.createElement('div');
                        cellDiv.className = 'habit-cell' + (done ? ' done' : '');
                        cellDiv.title = dateStr;
                        cellDiv.style.background = done ? (habitObj.color || '#39d353') : '#222';
                        cellDiv.style.border = done ? `1px solid ${(habitObj.color || '#39d353')}` : '1px solid #222';
                        cellDiv.onclick = () => toggleHabit(habitName, dateStr);
                        cellIdx++;
                    }
                    cellDiv.style.gridRow = `${row + 2}`;
                    cellDiv.style.gridColumn = `${colStart + col}`;
                    outerGrid.appendChild(cellDiv);
                }
            }
            colStart += weekCols + 1; // +1 for the gap
        }
        gridWrapper.appendChild(outerGrid);
        container.appendChild(gridWrapper);
        habitsList.appendChild(container);
        // Hide menu on click outside
        document.addEventListener('click', function hideMenu(e) {
            if (!menuWrapper.contains(e.target)) {
                menuDropdown.style.display = 'none';
                document.removeEventListener('click', hideMenu);
            }
        });
    });
}

// Populate quick-check habit dropdown and handle quick check
function populateQuickHabitSelect(habitsData) {
    const select = document.getElementById('quick-habit-select');
    if (!select) return;
    select.innerHTML = '';
    Object.keys(habitsData).forEach(habit => {
        const opt = document.createElement('option');
        opt.value = habit;
        opt.textContent = habit;
        select.appendChild(opt);
    });
}

const quickCheckForm = document.getElementById('quick-check-form');
if (quickCheckForm) {
    quickCheckForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const select = document.getElementById('quick-habit-select');
        if (!select || !select.value) return;
        const habitName = select.value;
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const dateStr = `${yyyy}-${mm}-${dd}`;
        fetch('/api/habits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ habit: habitName, date: dateStr })
        }).then(() => loadHabits());
    });
}

// Patch loadHabits to also update the quick-check dropdown
function loadHabits() {
    fetch('/api/habits').then(res => res.json()).then(data => {
        renderAllHabits(data.habits || {});
        populateQuickHabitSelect(data.habits || {});
    });
}

function toggleHabit(habitName, dateStr) {
    fetch('/api/habits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit: habitName, date: dateStr })
    }).then(() => loadHabits());
}

function updateHabitColor(habitName, color, cb) {
    fetch('/api/habits/color', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit: habitName, color })
    }).then(() => { if (cb) cb(); });
}

// Only add event listeners if the elements exist (for page-specific JS)
const addHabitForm = document.getElementById('add-habit-form');
if (addHabitForm) {
    addHabitForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('new-habit-name').value.trim();
        if (!name) return;
        fetch('/api/habits/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ habit: name })
        }).then(() => {
            document.getElementById('new-habit-name').value = '';
            loadHabits();
        });
    });
}

// On load
window.addEventListener('DOMContentLoaded', () => {
    fetch('/api/motivation')
        .then(res => res.json())
        .then(data => {
            document.getElementById('motivation').textContent = data.motivation;
        })
        .catch(() => {
            document.getElementById('motivation').textContent = 'Stay motivated!';
        });
    loadHabits();
    
    // Add voice assistant script and styles
    if (!document.querySelector('script[src="/static/voice.js"]')) {
        const voiceScript = document.createElement('script');
        voiceScript.src = '/static/voice.js';
        document.head.appendChild(voiceScript);
        
        const voiceStyles = document.createElement('link');
        voiceStyles.rel = 'stylesheet';
        voiceStyles.href = '/static/voice.css';
        document.head.appendChild(voiceStyles);
    }
});
