/*
═══════════════════════════════════════════════════════════════════
📁 ФАЙЛ: static/script.js
📝 ОПИСАНИЕ: Клиентская логика "Генератора отмазок"
═══════════════════════════════════════════════════════════════════

✅ Загрузка списка ситуаций с сервера
✅ Генерация отмазки через POST /generate
✅ Копирование в буфер обмена + уведомление "ОТПРАВЛЕНО!"
✅ Загрузка и отображение истории
✅ Перегенерация отмазки
✅ Показ/скрытие спиннера загрузки

═══════════════════════════════════════════════════════════════════
*/

let currentExcuse = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadSituations();
    loadHistory();
});

// Загрузка списка ситуаций
async function loadSituations() {
    try {
        const response = await fetch('/situations');
        const data = await response.json();

        const select = document.getElementById('situation');
        select.innerHTML = '<option value="">Выберите ситуацию...</option>';

        data.situations.forEach(situation => {
            const option = document.createElement('option');
            option.value = situation;
            option.textContent = situation;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки ситуаций:', error);
    }
}

// Обработка изменения выбора ситуации
function handleSituationChange() {
    const select = document.getElementById('situation');
    const customGroup = document.getElementById('custom-text-group');

    if (select.value === 'Другое') {
        customGroup.style.display = 'block';
    } else {
        customGroup.style.display = 'none';
    }
}

// Генерация отмазки
async function generateExcuse() {
    const select = document.getElementById('situation');
    const customText = document.getElementById('custom-text').value;

    if (!select.value) {
        alert('Пожалуйста, выберите ситуацию!');
        return;
    }

    if (select.value === 'Другое' && !customText.trim()) {
        alert('Пожалуйста, опишите свою ситуацию!');
        return;
    }

    // Показываем загрузку
    showLoading(true);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                situation: select.value,
                custom_text: customText
            })
        });

        if (!response.ok) {
            throw new Error('Ошибка генерации отмазки');
        }

        const excuse = await response.json();
        currentExcuse = excuse;

        // Отображаем результат
        displayResult(excuse);

        // Обновляем историю
        loadHistory();

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при генерации отмазки. Попробуйте ещё раз.');
    } finally {
        showLoading(false);
    }
}

// Отображение результата
function displayResult(excuse) {
    const resultSection = document.getElementById('result-section');
    const excuseText = document.getElementById('excuse-text');
    const ratingValue = document.getElementById('rating-value');
    const ratingBadge = document.getElementById('rating-badge');

    excuseText.textContent = excuse.excuse_text;
    ratingValue.textContent = excuse.rating;

    // Цвет рейтинга в зависимости от значения
    if (excuse.rating >= 80) {
        ratingBadge.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
    } else if (excuse.rating >= 60) {
        ratingBadge.style.background = 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)';
    } else {
        ratingBadge.style.background = 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)';
    }

    resultSection.style.display = 'block';

    // Прокрутка к результату
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Копирование отмазки
async function copyExcuse() {
    if (!currentExcuse) return;

    try {
        await navigator.clipboard.writeText(currentExcuse.excuse_text);
        showNotification();

        // Меняем текст кнопки временно
        const copyBtn = document.getElementById('copy-btn');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '✅ Скопировано!';
        copyBtn.style.background = 'rgba(76, 175, 80, 0.3)';

        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '';
        }, 2000);

    } catch (error) {
        console.error('Ошибка копирования:', error);
        alert('Не удалось скопировать текст. Попробуйте вручную.');
    }
}

// Загрузка истории
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();

        const historyList = document.getElementById('history-list');

        if (data.history.length === 0) {
            historyList.innerHTML = '<p class="empty-history">История пуста. Сгенерируйте первую отмазку!</p>';
            return;
        }

        historyList.innerHTML = data.history.map(item => `
            <div class="history-item">
                <div class="history-item-header">
                    <span class="history-item-situation">${item.situation}</span>
                    <span class="history-item-rating">${item.rating}%</span>
                </div>
                <div class="history-item-text">${item.excuse_text}</div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Ошибка загрузки истории:', error);
    }
}

// Показ/скрытие загрузки
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// Показ уведомления
function showNotification(message = '✅ ОТПРАВЛЕНО!') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}