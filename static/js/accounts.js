function initializeAccountForm() {
    console.log('Initializing account form...');
    
    const typeSelect = document.getElementById('type');
    const tdsContainer = document.getElementById('tdsContainer');
    const tdsInput = document.getElementById('tds_percentage');
    
    if (!typeSelect || !tdsContainer || !tdsInput) {
        console.error('Required elements not found');
        return;
    }
    
    console.log('All elements found');
    
    function toggleTDSField() {
        console.log('Type changed to:', typeSelect.value);
        if (typeSelect.value === 'Process') {
            console.log('Showing TDS field');
            tdsContainer.style.display = 'block';
            tdsInput.required = true;
        } else {
            console.log('Hiding TDS field');
            tdsContainer.style.display = 'none';
            tdsInput.required = false;
            tdsInput.value = '';
        }
    }
    
    // Add event listener
    typeSelect.addEventListener('change', toggleTDSField);
    
    // Initial check
    toggleTDSField();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAccountForm); 
