# 🚀 Quick Start Guide - AI SQL Chatbot

## ✅ Everything is READY!

Your complete AI SQL chatbot with interactive visualizations is ready to use.

---

## 🎯 What You Have

1. **Backend** - Django + LangChain + OpenAI AI Agent (✅ Complete)
2. **Visualizations** - Plotly interactive charts (✅ Complete)
3. **Frontend** - Modern React chat UI (✅ Complete)

---

## 🏃 Run It NOW (3 Steps)

### Step 1: Start Backend
```bash
cd /Users/yermakhansultan/Desktop/microsoft/backend
python manage.py runserver
```
✅ Backend running at `http://localhost:8000`

### Step 2: Start Frontend (new terminal)
```bash
cd /Users/yermakhansultan/Desktop/microsoft/frontend
npm run dev
```
✅ Frontend running at `http://localhost:5173`

### Step 3: Open Browser
```
http://localhost:5173
```

---

## 💬 Try These Questions

Once the app loads, try asking:

1. **"How many transactions were made in Almaty?"**
   → Shows SQL query + bar chart

2. **"Show me top 10 cities by transaction count"**
   → Interactive bar chart with top cities

3. **"What is the distribution of transaction amounts?"**
   → Histogram with distribution

4. **"Show transactions over time"**
   → Line chart with trends

---

## 🎨 What You'll See

### 1. Chat Interface
- Message bubbles (you vs AI)
- SQL queries displayed
- Interactive charts embedded
- Insights automatically generated

### 2. Interactive Charts
- **Hover** - See exact values
- **Zoom** - Focus on specific data
- **Pan** - Explore the chart
- **Download** - Save as PNG

### 3. Smart Features
- Suggested queries to get started
- Database connection status
- Typing indicator while AI thinks
- Error messages if something breaks

---

## 📊 Chart Types You'll Get

| Your Question | Chart Type |
|--------------|------------|
| "Transactions by city" | Bar Chart |
| "Transactions over time" | Line Chart |
| "Market share" | Pie Chart |
| "Amount distribution" | Histogram |
| "Correlation between X and Y" | Scatter Plot |

---

## 🔧 If Something Doesn't Work

### Backend not starting?
```bash
# Check if port 8000 is free
lsof -ti:8000
# If needed, kill the process
kill -9 <PID>
```

### Frontend not starting?
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Charts not showing?
1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify backend is running
4. Check `.env` file has correct API URL

---

## 📁 Project Structure

```
microsoft/
├── backend/                    # Django backend
│   ├── mcp/
│   │   ├── ai_agent.py        # LangChain AI agent
│   │   ├── visualization.py    # Plotly chart generator
│   │   └── views.py           # API endpoints
│   └── manage.py
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── ai-chatbot.ts  # Backend integration
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── PlotlyChart.tsx
│   │   ├── App.tsx            # Main app
│   │   └── App.css            # Styling
│   └── package.json
├── FRONTEND_README.md          # Detailed frontend docs
├── VISUALIZATION_UPGRADE.md    # Visualization docs
└── QUICK_START.md             # This file
```

---

## 🎯 Example Flow

1. **User types**: "How many transactions in Almaty?"
2. **AI Agent**: Generates SQL query
3. **Backend**: Executes SQL on database
4. **Visualization System**: Analyzes results, creates chart
5. **Frontend**: Shows answer + SQL + interactive chart + insights
6. **User**: Can zoom, hover, explore the chart

---

## 💡 Tips

- **Use suggested queries** - Great for testing/demos
- **Check SQL queries** - Learn what's happening
- **Explore charts** - Hover, zoom, pan
- **Ask follow-ups** - "Show me more", "What about Astana?"
- **Copy SQL** - Use in your own tools

---

## 🚀 Ready to Use!

1. ✅ Backend: `python manage.py runserver`
2. ✅ Frontend: `npm run dev`
3. ✅ Browser: `http://localhost:5173`
4. ✅ Ask questions about your data!

---

**Status: 🎉 COMPLETE - Enjoy your AI SQL Chatbot!**
