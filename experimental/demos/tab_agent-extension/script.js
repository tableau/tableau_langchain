async function runAgent() {
    const input = document.getElementById("query").value;
    const output = document.getElementById("response");
    output.textContent = "Thinking...";

    const payload = {
      assistant_id: "17909892-e2f4-479b-825e-d97f4120b62e",
      input: {
        messages: [
          { type: "human", content: input }
        ]
      }
    };
    console.log(payload);

    try {
      const response = await fetch("http://127.0.0.1:2024/runs/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });

        // Process SSE-formatted chunk (lines like "event: values", "data: {...}")
        const lines = chunk.split("\n").filter(line => line.startsWith("data: "));
        for (const line of lines) {
          try {
            const jsonStr = line.replace("data: ", "").trim();
            const eventData = JSON.parse(jsonStr);

            const messages = eventData.messages || [];
            for (const msg of messages) {
              if (msg.type === "ai" && msg.content) {
                fullText += msg.content;
                output.textContent = fullText;
              }
            }
          } catch (e) {
            console.error("Error parsing JSON line:", line, e);
          }
        }
      }
    } catch (err) {
      output.textContent = "Error: " + err.message;
    }
  }
