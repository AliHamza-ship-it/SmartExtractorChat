Smart AI Chat & Workspace
Welcome to the Smart AI Chat & Workspace! This project is a modern, highly intelligent web application designed to give you a "ChatGPT-like" experience. It allows users to have real-time conversations with an AI, manage their chat history, and even extract complex data (like invoices) automatically.

We built this with a focus on a beautiful design, lightning-fast responses, and a completely seamless user experience.

🌟 What Can This App Do?
This application is packed with features designed to make working with AI as smooth and helpful as possible:

🔐 Secure User Accounts: Users can securely register, log in, and verify their identity using OTP (One-Time Passwords). Everyone gets their own private workspace.

🎭 Custom AI Personas: You aren't just talking to a generic robot. You can choose from built-in personas like an AI Tech Mentor, Executive Assistant, Creative Writer, or a Strict Code Auditor to get the exact help you need.

⚡ Real-Time Typing (Streaming): Just like human messaging, the AI types out its answers in real-time. You don't have to wait 30 seconds staring at a loading screen to read the response.

📚 Persistent Chat History: Every conversation is safely saved to a database. You can log out, come back days later, and pick up right where you left off.

🧾 Smart Invoice Extractor: Beyond just chatting, the app has a specialized tool that can read messy, raw text from invoices and perfectly organize it into clean, structured data for business use.

✨ The "Magic" Features (What makes this special)
We solved some of the most annoying problems found in standard AI chat apps to make this extremely robust:

1. Unbreakable Chat Switching 🛡️
Have you ever asked an AI a long question, clicked away to look at an older chat, and the app crashed or the AI forgot to finish your answer? Not here.
If you ask our AI a question and switch chats while it is still "typing", the app gracefully pauses the screen, but the AI keeps thinking in the background. It will finish writing the answer and safely file it into your database so it's ready for you when you go back to it.

2. Auto-Generated Smart Titles 🏷️
When you start a new chat, you don't have to name it. The moment you send your first message, a lightweight background AI reads your question and instantly creates a catchy, 3-to-4 word title for that chat (e.g., "Fix Code Error" or "Plan Vacation Itinerary"). This keeps your sidebar perfectly organized without any extra effort on your part.

🏗️ How It Works (Behind the Scenes)
Even though it looks simple on the outside, there are three main pieces working together:

The Frontend (The Face): Built with React, this is the beautiful "Glassmorphism" interface you see and click on. It handles the smooth animations, the sidebar, and formatting the AI's text so that code and lists look perfect.

The Backend (The Brain): Built with Python (FastAPI), this acts as the traffic controller. It talks to the AI models securely, handles user logins, and runs background tasks (like generating chat titles) so the main app never slows down.

The Database (The Memory): Powered by Supabase, this is a highly secure vault that remembers who you are, saves all your past chats, and organizes your custom AI instructions.

🚀 Getting Started
(For Developers or System Admins)

To run this project locally, your technical team will need to:

Set up a Supabase project for the database.

Provide an OpenRouter/OpenAI API Key to power the AI brain.

Run the Python backend server.

Run the React frontend application.

Once connected, simply open your web browser, log in, and start chatting!