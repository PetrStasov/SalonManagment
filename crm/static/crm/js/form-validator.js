// static/crm/js/form-validator.js
const FormValidator = {
    validatePhone: function() {
        const phoneInput = document.getElementById('phone');
        if (!phoneInput) return false;
        
        const phoneValue = phoneInput.value.trim();
        const phoneRegex = /^\+375\d{9}$/;
        
        if (!phoneRegex.test(phoneValue)) {
            const errorElement = document.getElementById('phoneError');
            if (errorElement) {
                errorElement.textContent = 'Введите номер в формате +375XXXXXXXXX';
                errorElement.style.display = 'block';
            }
            return false;
        }
        
        const errorElement = document.getElementById('phoneError');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
        return true;
    },
    
    validateClientData: function() {
        const fullNameInput = document.getElementById('fullName');
        if (!fullNameInput) return false;
        
        const fullName = fullNameInput.value.trim();
        
        if (!fullName || fullName.split(' ').length < 2) {
            const errorElement = document.getElementById('nameError');
            if (errorElement) {
                errorElement.textContent = 'Введите ФИО полностью';
                errorElement.style.display = 'block';
            }
            return false;
        }
        
        const errorElement = document.getElementById('nameError');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
        return true;
    }
};