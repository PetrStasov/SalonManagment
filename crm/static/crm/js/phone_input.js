document.addEventListener('DOMContentLoaded', function() {
    new Cleave('#phone', {
        numericOnly: true,
        blocks: [13],
        prefix: '+375',
        noImmediatePrefix: true,
        onValueChanged: function(e) {
            if (!e.target.value.startsWith('+375') && e.target.value) {
                e.target.value = '+375' + e.target.value.replace(/\D/g, '');
            }
        }
    });
});