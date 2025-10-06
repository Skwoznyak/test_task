/**
 * Основной JavaScript для приложения управления задачами
 */

class TaskManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.tasks = [];
        this.taskLists = [];
        this.users = [];
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.loadInitialData();
        this.setupEventListeners();
    }
    
    connectWebSocket() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/tasks/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.socket.send(JSON.stringify({type: 'ping'}));
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connectWebSocket();
                }, 2000 * this.reconnectAttempts);
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'notification':
                this.showNotification(data.message);
                this.updateNotificationCount();
                break;
            case 'tasks_data':
                this.tasks = data.tasks;
                this.renderTasks(data.tasks);
                break;
            case 'pong':
                // Соединение активно
                break;
        }
    }
    
    showNotification(message) {
        // Показываем уведомление в браузере
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                new Notification('Новое уведомление', {
                    body: message,
                    icon: '/static/favicon.ico'
                });
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        new Notification('Новое уведомление', {
                            body: message,
                            icon: '/static/favicon.ico'
                        });
                    }
                });
            }
        }
        
        // Показываем toast уведомление
        this.showToast(message, 'info');
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Удаляем toast после скрытия
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    updateNotificationCount() {
        fetch('/api/notifications/unread_count/')
            .then(response => response.json())
            .then(data => {
                const count = data.unread_count;
                const badge = document.getElementById('notification-count');
                const notificationBadge = document.querySelector('.notification-badge');
                
                if (badge) badge.textContent = count;
                
                if (notificationBadge) {
                    if (count > 0) {
                        notificationBadge.classList.add('has-notifications');
                    } else {
                        notificationBadge.classList.remove('has-notifications');
                    }
                }
            });
    }
    
    loadInitialData() {
        this.loadTasks();
        this.loadTaskLists();
        this.loadUsers();
        this.loadStats();
        this.loadNotifications();
    }
    
    loadTasks() {
        return fetch('/api/tasks/my_tasks/')
            .then(response => response.json())
            .then(data => {
                this.tasks = data;
                this.renderTasks(data);
            })
            .catch(error => {
                console.error('Error loading tasks:', error);
                this.showToast('Ошибка загрузки задач', 'danger');
            });
    }
    
    loadTaskLists() {
        return fetch('/api/task-lists/')
            .then(response => response.json())
            .then(data => {
                this.taskLists = data;
                this.renderTaskLists(data);
            })
            .catch(error => {
                console.error('Error loading task lists:', error);
            });
    }
    
    loadUsers() {
        return fetch('/api/users/')
            .then(response => response.json())
            .then(data => {
                this.users = data;
            })
            .catch(error => {
                console.error('Error loading users:', error);
            });
    }
    
    loadStats() {
        return fetch('/api/tasks/my_tasks/')
            .then(response => response.json())
            .then(data => {
                const stats = this.calculateStats(data);
                this.renderStats(stats);
            })
            .catch(error => {
                console.error('Error loading stats:', error);
            });
    }
    
    loadNotifications() {
        return fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                this.renderNotifications(data);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
            });
    }
    
    calculateStats(tasks) {
        const total = tasks.length;
        const completed = tasks.filter(t => t.status === 'completed').length;
        const inProgress = tasks.filter(t => t.status === 'in_progress').length;
        const pending = tasks.filter(t => t.status === 'pending').length;
        const overdue = tasks.filter(t => t.is_overdue).length;
        
        return { total, completed, inProgress, pending, overdue };
    }
    
    renderStats(stats) {
        const container = document.getElementById('stats-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <div class="h4 text-primary">${stats.total}</div>
                    <div class="small text-muted">Всего</div>
                </div>
                <div class="col-6">
                    <div class="h4 text-success">${stats.completed}</div>
                    <div class="small text-muted">Выполнено</div>
                </div>
            </div>
            <hr>
            <div class="row text-center">
                <div class="col-4">
                    <div class="h5 text-warning">${stats.inProgress}</div>
                    <div class="small text-muted">В работе</div>
                </div>
                <div class="col-4">
                    <div class="h5 text-info">${stats.pending}</div>
                    <div class="small text-muted">Ожидание</div>
                </div>
                <div class="col-4">
                    <div class="h5 text-danger">${stats.overdue}</div>
                    <div class="small text-muted">Просрочено</div>
                </div>
            </div>
        `;
    }
    
    renderTaskLists(lists) {
        const container = document.getElementById('task-lists-container');
        if (!container) return;
        
        if (lists.length === 0) {
            container.innerHTML = '<p class="text-muted">Нет списков задач</p>';
            return;
        }
        
        let html = '';
        lists.forEach(list => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${list.name}</strong>
                        <br><small class="text-muted">${list.task_count} задач</small>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" onclick="taskManager.createTaskInList(${list.id})">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            `;
        });
        container.innerHTML = html;
    }
    
    renderTasks(tasksToRender) {
        const container = document.getElementById('tasks-container');
        if (!container) return;
        
        if (tasksToRender.length === 0) {
            container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-inbox fa-3x mb-3"></i><p>Нет задач</p></div>';
            return;
        }
        
        let html = '';
        tasksToRender.forEach(task => {
            const statusClass = `status-${task.status}`;
            const priorityClass = `priority-${task.priority}`;
            const isOverdue = task.is_overdue;
            
            const statusIcons = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            };
            
            const priorityIcons = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🔴'
            };
            
            const dueDate = task.due_date ? new Date(task.due_date).toLocaleString() : 'Не указан';
            
            html += `
                <div class="card task-card mb-3 ${statusClass} ${priorityClass} ${isOverdue ? 'border-danger' : ''} fade-in">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h5 class="card-title">
                                    ${statusIcons[task.status]} ${priorityIcons[task.priority]} ${task.title}
                                    ${isOverdue ? '<span class="badge bg-danger ms-2">Просрочено</span>' : ''}
                                </h5>
                                <p class="card-text">${task.description || 'Без описания'}</p>
                                <div class="row">
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-user"></i> Создатель: ${task.created_by.username}<br>
                                            <i class="fas fa-calendar"></i> Срок: ${dueDate}
                                        </small>
                                    </div>
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-list"></i> Список: ${task.task_list.name}<br>
                                            <i class="fas fa-clock"></i> Создана: ${new Date(task.created_at).toLocaleString()}
                                        </small>
                                    </div>
                                </div>
                            </div>
                            <div class="btn-group-vertical">
                                <button class="btn btn-sm btn-outline-primary" onclick="taskManager.editTask(${task.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                ${task.status !== 'completed' ? `
                                    <button class="btn btn-sm btn-outline-success" onclick="taskManager.markTaskCompleted(${task.id})">
                                        <i class="fas fa-check"></i>
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    renderNotifications(notifications) {
        const container = document.getElementById('notification-list');
        if (!container) return;
        
        container.innerHTML = '<li><h6 class="dropdown-header">Уведомления</h6></li><li><hr class="dropdown-divider"></li>';
        
        if (notifications.length === 0) {
            container.innerHTML += '<li><a class="dropdown-item" href="#" id="no-notifications">Нет уведомлений</a></li>';
        } else {
            notifications.slice(0, 5).forEach(notification => {
                const item = document.createElement('li');
                item.innerHTML = `
                    <a class="dropdown-item ${notification.is_read ? '' : 'fw-bold'}" href="#" onclick="taskManager.markNotificationRead(${notification.id})">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${notification.title}</h6>
                            <small>${new Date(notification.created_at).toLocaleString()}</small>
                        </div>
                        <p class="mb-1">${notification.message}</p>
                    </a>
                `;
                container.appendChild(item);
            });
        }
    }
    
    setupEventListeners() {
        // Фильтры задач
        const statusFilter = document.getElementById('status-filter');
        const priorityFilter = document.getElementById('priority-filter');
        
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterTasks());
        }
        
        if (priorityFilter) {
            priorityFilter.addEventListener('change', () => this.filterTasks());
        }
        
        // Обновление уведомлений каждые 30 секунд
        setInterval(() => {
            this.loadNotifications();
            this.updateNotificationCount();
        }, 30000);
    }
    
    filterTasks() {
        const statusFilter = document.getElementById('status-filter');
        const priorityFilter = document.getElementById('priority-filter');
        
        if (!statusFilter || !priorityFilter) return;
        
        const statusValue = statusFilter.value;
        const priorityValue = priorityFilter.value;
        
        let filteredTasks = this.tasks;
        
        if (statusValue) {
            filteredTasks = filteredTasks.filter(task => task.status === statusValue);
        }
        
        if (priorityValue) {
            filteredTasks = filteredTasks.filter(task => task.priority === priorityValue);
        }
        
        this.renderTasks(filteredTasks);
    }
    
    showOverdueTasks() {
        const overdueTasks = this.tasks.filter(task => task.is_overdue);
        this.renderTasks(overdueTasks);
        
        // Сбрасываем фильтры
        const statusFilter = document.getElementById('status-filter');
        const priorityFilter = document.getElementById('priority-filter');
        
        if (statusFilter) statusFilter.value = '';
        if (priorityFilter) priorityFilter.value = '';
    }
    
    refreshTasks() {
        this.loadTasks();
        this.loadStats();
        this.showToast('Задачи обновлены', 'success');
    }
    
    // Методы для работы с задачами
    showCreateTaskModal() {
        const taskListSelect = document.getElementById('task-list');
        const assignedToSelect = document.getElementById('assigned-to');
        
        if (taskListSelect) {
            taskListSelect.innerHTML = '<option value="">Выберите список</option>';
            this.taskLists.forEach(list => {
                taskListSelect.innerHTML += `<option value="${list.id}">${list.name}</option>`;
            });
        }
        
        if (assignedToSelect) {
            assignedToSelect.innerHTML = '<option value="">Выберите исполнителя</option>';
            this.users.forEach(user => {
                assignedToSelect.innerHTML += `<option value="${user.id}">${user.username}</option>`;
            });
        }
        
        const modal = new bootstrap.Modal(document.getElementById('createTaskModal'));
        modal.show();
    }
    
    createTask() {
        const formData = {
            title: document.getElementById('task-title').value,
            description: document.getElementById('task-description').value,
            task_list: document.getElementById('task-list').value,
            assigned_to: document.getElementById('assigned-to').value,
            priority: document.getElementById('task-priority').value,
            due_date: document.getElementById('due-date').value
        };
        
        if (!formData.title || !formData.task_list || !formData.assigned_to) {
            this.showToast('Заполните обязательные поля', 'warning');
            return;
        }
        
        fetch('/api/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                this.showToast('Задача создана', 'success');
                bootstrap.Modal.getInstance(document.getElementById('createTaskModal')).hide();
                document.getElementById('create-task-form').reset();
                this.loadTasks();
                this.loadStats();
            } else {
                this.showToast('Ошибка создания задачи', 'danger');
            }
        })
        .catch(error => {
            console.error('Error creating task:', error);
            this.showToast('Ошибка создания задачи', 'danger');
        });
    }
    
    editTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;
        
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-task-title').value = task.title;
        document.getElementById('edit-task-description').value = task.description;
        document.getElementById('edit-task-status').value = task.status;
        document.getElementById('edit-task-priority').value = task.priority;
        document.getElementById('edit-due-date').value = task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '';
        
        const assignedToSelect = document.getElementById('edit-assigned-to');
        if (assignedToSelect) {
            assignedToSelect.innerHTML = '<option value="">Выберите исполнителя</option>';
            this.users.forEach(user => {
                const selected = user.id === task.assigned_to.id ? 'selected' : '';
                assignedToSelect.innerHTML += `<option value="${user.id}" ${selected}>${user.username}</option>`;
            });
        }
        
        const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
        modal.show();
    }
    
    updateTask() {
        const taskId = document.getElementById('edit-task-id').value;
        const formData = {
            title: document.getElementById('edit-task-title').value,
            description: document.getElementById('edit-task-description').value,
            assigned_to: document.getElementById('edit-assigned-to').value,
            status: document.getElementById('edit-task-status').value,
            priority: document.getElementById('edit-task-priority').value,
            due_date: document.getElementById('edit-due-date').value
        };
        
        if (!formData.title || !formData.assigned_to) {
            this.showToast('Заполните обязательные поля', 'warning');
            return;
        }
        
        fetch(`/api/tasks/${taskId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                this.showToast('Задача обновлена', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editTaskModal')).hide();
                this.loadTasks();
                this.loadStats();
            } else {
                this.showToast('Ошибка обновления задачи', 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating task:', error);
            this.showToast('Ошибка обновления задачи', 'danger');
        });
    }
    
    markTaskCompleted(taskId) {
        fetch(`/api/tasks/${taskId}/mark_completed/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            this.showToast('Задача отмечена как выполненная', 'success');
            this.loadTasks();
            this.loadStats();
        })
        .catch(error => {
            console.error('Error marking task completed:', error);
            this.showToast('Ошибка обновления задачи', 'danger');
        });
    }
    
    markNotificationRead(notificationId) {
        fetch(`/api/notifications/${notificationId}/mark_read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
            }
        }).then(() => {
            this.updateNotificationCount();
            this.loadNotifications();
        });
    }
    
    createTaskInList(listId) {
        this.showCreateTaskModal();
        document.getElementById('task-list').value = listId;
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Глобальные функции для совместимости с HTML
let taskManager;

document.addEventListener('DOMContentLoaded', function() {
    taskManager = new TaskManager();
    
    // Глобальные функции для вызова из HTML
    window.showCreateTaskModal = () => taskManager.showCreateTaskModal();
    window.filterTasks = () => taskManager.filterTasks();
    window.showOverdueTasks = () => taskManager.showOverdueTasks();
    window.refreshTasks = () => taskManager.refreshTasks();
    window.createTask = () => taskManager.createTask();
    window.editTask = (id) => taskManager.editTask(id);
    window.updateTask = () => taskManager.updateTask();
    window.markTaskCompleted = (id) => taskManager.markTaskCompleted(id);
    window.createTaskInList = (id) => taskManager.createTaskInList(id);
    window.markNotificationRead = (id) => taskManager.markNotificationRead(id);
});
