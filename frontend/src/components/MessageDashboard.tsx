import React, { useState, useEffect } from "react";
import {
  TextField,
  Button,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";

interface Message {
  id: string;
  content: string;
}

const MessageDashboard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageText, setMessageText] = useState<string>("");
  const [messageSendResultText, setMessageSendResultText] =
    useState<string>("");

  useEffect(() => {
    const ws = new WebSocket("ws://app.localhost/api/ws/1");
    ws.onopen = () => {
      console.log("WebSocket connected");
    };
    ws.onmessage = (event) => {
      const receivedMessage: Message = JSON.parse(event.data);
      setMessages((prevMessages) => [...prevMessages, receivedMessage]);
    };
    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = async () => {
    try {
      const response = await fetch("http://app.localhost/api/send-message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: messageText }),
      });

      if (response.ok) {
        setMessageSendResultText("Message sent successfully");
        setMessageText("");
      } else {
        setMessageSendResultText("Failed to send message");
        console.error("Failed to send message");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessageSendResultText("Error sending message");
    }
  };

  const handleMessageChange = (
    event: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    setMessageText(event.target.value);
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: "20px" }}>
      <Paper elevation={3} style={{ padding: "20px" }}>
        <Typography variant="h4" gutterBottom>
          Message Dashboard
        </Typography>
        <List style={{ maxHeight: "300px", overflow: "auto" }}>
          {messages.map((message) => (
            <ListItem key={message.id}>
              <ListItemText primary={message.content} />
            </ListItem>
          ))}
        </List>
        <TextField
          variant="outlined"
          label="Enter your message"
          fullWidth
          multiline
          rows={4}
          value={messageText}
          onChange={handleMessageChange}
          style={{ marginTop: "20px" }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={sendMessage}
          style={{ marginTop: "10px" }}
        >
          Send
        </Button>
        {/* Display messageSendResultText */}
        {messageSendResultText && (
          <Typography
            variant="body1"
            color="textSecondary"
            style={{ marginTop: "10px" }}
          >
            {messageSendResultText}
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default MessageDashboard;
