function typeLLMResponse(text, container, speed=30) {
    container.textContent = '';
    let i = 0;
    function type() {
        if (i < text.length) {
            container.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}