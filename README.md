# 🤖 AgentLens

AgentLens is an AI-powered Shopify operations agent and web dashboard that automatically analyzes, scores, and optimizes your Shopify store's products in real time. It identifies SEO issues, low-quality descriptions, and missing tags, then uses AI to rewrite and fix them instantly.

It also features a **Studio Mockup Optimizer** that uses AI to seamlessly swap product backgrounds into beautiful studio environments (like marble countertops, neon cyberpunk styles, organic wood desks, and tropical beaches).

## ✨ Features
- **Real-Time Shopify Sync**: Fetches your live Shopify products and syncs updates instantly.
- **AI Scoring Engine**: Grades products out of 100 based on SEO, description length, media count, and policy presence.
- **Batch Auto-Optimization**: Fixes your entire store's issues with one click.
- **Studio Mockup Generator**: Automatically swaps standard product backgrounds for high-quality studio scenes.
- **Dark Mode Glassmorphism UI**: A beautiful, modern, and highly interactive user interface.

## 🚀 Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/agentlens.git
   cd agentlens
   ```

2. **Create a Virtual Environment (Optional but recommended)**
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On Mac/Linux:
   source env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   Rename `.env.example` to `.env` and fill in your Shopify API details:
   ```env
   SHOPIFY_STORE_URL="https://your-store.myshopify.com"
   SHOPIFY_ACCESS_TOKEN="your_shopify_access_token_here"
   OPENAI_API_KEY="your_openai_api_key_here" # Optional
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`

## 🌍 Deploying to Vercel

This project is configured to run on Vercel as a Serverless Python (Flask) application.

1. Push your code to GitHub.
2. Go to [Vercel](https://vercel.com/) and click **Add New** > **Project**.
3. Import your GitHub repository.
4. Open the **Environment Variables** section and add:
   - `SHOPIFY_STORE_URL`
   - `SHOPIFY_ACCESS_TOKEN`
   - `OPENAI_API_KEY` (Optional)
5. Click **Deploy**.

## 🛠 Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML5, Vanilla JavaScript, CSS (Custom Glassmorphism Design)
- **Integrations**: Shopify Admin API, OpenAI / DALL-E (Optional)

---
*Built with ❤️ for Shopify Merchants.*
