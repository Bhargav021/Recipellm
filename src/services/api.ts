const API_URL = "http://localhost:5001";

export async function queryLLM(userQuery: string, mode: string = "mongo") {
  try {
    const response = await fetch(`${API_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userQuery, mode }),
    });

    if (!response.ok) {
      let backendError = '';
      try {
        const payload = await response.json();
        backendError = payload?.error || payload?.message || '';
      } catch {
        backendError = await response.text();
      }
      const detail = backendError ? ` - ${backendError}` : '';
      throw new Error(`API error: ${response.status}${detail}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error querying LLM:', error);
    throw error;
  }
}

export async function checkHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}
