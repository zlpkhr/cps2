export class Chat {
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
