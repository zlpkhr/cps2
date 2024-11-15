class Chat {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async getMessages() {
    const url = new URL("/chat", this.baseUrl);
    const response = await fetch(url);
    return response.json();
  }

  async createMessage({ author, message }) {
    const url = new URL("/message", this.baseUrl);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ author, message }),
    });
    return response.json();
  }

  async censorMessage(message) {
    const url = new URL("/censorMessage", this.baseUrl);
    url.search = new URLSearchParams({ message }).toString();
    const response = await fetch(url);
    const data = await response.json();
    return data.censoredMessage;
  }

  async deleteMessages() {
    const url = new URL("/chat", this.baseUrl);
    const response = await fetch(url, { method: "DELETE" });
    return response.json();
  }
}

const chatWindow = document.querySelector(".chat-window");
const messageInput = document.querySelector(".new-message-input");
const usernameInput = document.querySelector(".username-input");
const sendBtn = document.querySelector(".send-message-btn");
const clearBtn = document.querySelector(".clear-chat-btn");
const errorPopup = document.querySelector(".error-message-popup");
const errorCloseBtn = errorPopup.querySelector(".close-btn");

function showErrorPopup() {
  errorPopup.classList.add("active");
}

function hideErrorPopup() {
  errorPopup.classList.remove("active");
}

const chat = new Chat("http://localhost:3014");

function createMessageElement({ author, message }) {
  const el = document.createElement("div");
  el.className = "chat-entry";

  const name = document.createElement("span");
  name.className = "author";
  name.textContent = author;

  const delimiter = document.createElement("span");
  delimiter.className = "delimiter";
  delimiter.textContent = ": ";

  const text = document.createElement("span");
  text.className = "message";
  text.textContent = message;

  el.append(name, delimiter, text);
  return el;
}

function render(container, messages) {
  container.textContent = "";
  const fragment = document.createDocumentFragment();

  for (const message of messages) {
    fragment.appendChild(createMessageElement(message));
  }

  container.appendChild(fragment);
  container.lastElementChild?.scrollIntoView();
}

function updateButton(button, username, message) {
  const isValid = username.length > 0 && message.length > 0;
  button.disabled = !isValid;
  button.classList.toggle("disabled", !isValid);
}

async function handleSendButtonClick() {
  const message = messageInput.value;
  const username = usernameInput.value;

  if (!username || !message) return;

  try {
    const censored = await chat.censorMessage(message);
    const messages = await chat.createMessage({
      author: username,
      message: censored,
    });
    render(chatWindow, messages);
    messageInput.value = "";
    updateButton(sendBtn, username, "");
  } catch {
    showErrorPopup();
  }
}

async function handleClearButtonClick() {
  try {
    const messages = await chat.deleteMessages();
    render(chatWindow, messages);
  } catch {
    showErrorPopup();
  }
}

async function handleChatReload() {
  try {
    const messages = await chat.getMessages();
    render(chatWindow, messages);
  } catch {
    showErrorPopup();
  }
}

function handleMessageInputEnter(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    handleSendButtonClick();
  }
}

function handleInputChange() {
  updateButton(sendBtn, usernameInput.value, messageInput.value);
}

sendBtn.addEventListener("click", handleSendButtonClick);
messageInput.addEventListener("keydown", handleMessageInputEnter);
messageInput.addEventListener("input", handleInputChange);
usernameInput.addEventListener("input", handleInputChange);
errorCloseBtn.addEventListener("click", hideErrorPopup);
clearBtn.addEventListener("click", handleClearButtonClick);

handleInputChange();
handleChatReload();
setInterval(handleChatReload, 500);
