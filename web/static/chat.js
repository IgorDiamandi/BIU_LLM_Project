$(function() {
    // Make the chat container draggable and resizable
    $("#chat-container").draggable({
        handle: "#chat-header"
    }).resizable();
});

function addUserMessage(event) {
    event.preventDefault(); // Prevent default form submission

    // Get the user message from the input field
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();

    // If the input is empty, do nothing
    if (userMessage === '') return;

    // Create a new div for the user's message
    const messagesDiv = document.getElementById('messages');
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.textContent = userMessage;

    // Append the user's message to the messages div
    messagesDiv.appendChild(userMessageDiv);

    // Clear the input field
    userInput.value = '';

    // Show the typing indicator
    const typingIndicator = document.getElementById('typing-indicator');
    typingIndicator.style.display = 'flex';

    // Scroll to the bottom of the messages div after adding the user message
    scrollToBottom();

    // Submit the form via HTMX
    htmx.ajax('POST', '/ask', {
        target: '#messages',
        swap: 'beforeend',
        values: {
            question: userMessage
        }
    });
}

// Function to scroll to the bottom of the messages div
function scrollToBottom() {
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight;
}

// Hide typing indicator after the response has been swapped into the page
document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === 'messages') {
        // Hide the typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'none';

        // Scroll to the bottom of the messages div after a new response is added
        scrollToBottom();
    }
});

// Hide typing indicator if an error occurs during the request
document.addEventListener("htmx:responseError", function() {
    const typingIndicator = document.getElementById('typing-indicator');
    typingIndicator.style.display = 'none';
});