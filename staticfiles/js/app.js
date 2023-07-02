console.log('Hello from app.js')

function addQueryParamAndReload(current_chat_id) {
    const currentUrl = window.location.href;

    const hasQuery = currentUrl.includes('?');
    const currentUrlWithoutQuery = hasQuery ? currentUrl.split('?')[0] : currentUrl;

    const queryParams = new URLSearchParams();
    queryParams.set('current_chat_id', current_chat_id);

    const updatedUrl =  currentUrlWithoutQuery + '?' + queryParams.toString();

    window.location.href = updatedUrl;
}

function scrollToBottom() {
  var chatContainer = document.getElementById('chat-log');
  chatContainer.scrollTop = chatContainer.scrollHeight;
  console.log('scrollToBottom');
}
