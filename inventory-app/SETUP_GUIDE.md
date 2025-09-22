# Complete Setup Guide for VS Code

## Prerequisites
- **Node.js** (version 18 or higher) - Download from [nodejs.org](https://nodejs.org/)
- **Python** (version 3.8 or higher) - Download from [python.org](https://python.org/)
- **VS Code** - Download from [code.visualstudio.com](https://code.visualstudio.com/)

## Step 1: Download and Extract the Code

1. **Download the ZIP file** from v0 by clicking the three dots → "Download ZIP"
2. **Extract the ZIP file** to your desired location (e.g., `~/Desktop/inventory-app`)
3. **Open VS Code**
4. **Open the folder** in VS Code: `File → Open Folder` → Select the extracted folder

## Step 2: Install VS Code Extensions (Recommended)

Install these helpful extensions:
- **ES7+ React/Redux/React-Native snippets**
- **Tailwind CSS IntelliSense**
- **Python** (by Microsoft)
- **Prettier - Code formatter**
- **Auto Rename Tag**

## Step 3: Set Up the Frontend (Next.js)

1. **Open Terminal in VS Code**: `Terminal → New Terminal`
2. **Install dependencies**:
   \`\`\`bash
   npm install
   \`\`\`
3. **Start the development server**:
   \`\`\`bash
   npm run dev
   \`\`\`
4. **Open your browser** and go to `http://localhost:3000`

You should see the Smart Inventory app with "Backend Offline" status - this is normal!

## Step 4: Set Up the Backend (Flask) - Optional

The app works with mock data, but if you want the full backend:

1. **Open a new terminal** in VS Code: `Terminal → New Terminal`
2. **Navigate to the project root** (if not already there)
3. **Install Python dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
   
   If you get permission errors on Mac, try:
   \`\`\`bash
   pip install --user -r requirements.txt
   \`\`\`
   
   Or use a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   pip install -r requirements.txt
   \`\`\`

4. **Start the Flask backend**:
   \`\`\`bash
   python app.py
   \`\`\`

5. **Verify backend is running**: You should see "Backend Connected" in the app

## Step 5: Using the App

### With Mock Data (No Backend Required)
1. Click "Take Photo of Your Inventory"
2. Select any image from your device
3. Wait for processing (uses demo data)
4. Select items you want to include
5. Click "Create Shopping List"
6. View your generated shopping list

### With Backend Running
- Same steps as above, but the app will process your actual photos
- The backend will analyze your inventory images
- Shopping lists will be generated based on your actual inventory

## Troubleshooting

### Frontend Issues
- **Port 3000 already in use**: Try `npm run dev -- -p 3001`
- **Module not found**: Delete `node_modules` and run `npm install` again
- **Permission errors**: Try `sudo npm install` (not recommended) or fix npm permissions

### Backend Issues
- **Port 8000 already in use**: Change port in `app.py` to `5000` or another port
- **Python module errors**: Make sure you're in the right directory and dependencies are installed
- **CORS errors**: The Flask app includes CORS headers, but try restarting both servers

### General Tips
- **Always restart both servers** after making changes
- **Check the browser console** for detailed error messages
- **Use the VS Code integrated terminal** for easier debugging
- **The app works perfectly with mock data** - backend is optional for testing

## File Structure
\`\`\`
inventory-app/
├── app/                 # Next.js app directory
│   ├── page.tsx        # Main app component
│   ├── layout.tsx      # App layout
│   └── globals.css     # Global styles
├── components/         # Reusable components
├── app.py             # Flask backend
├── requirements.txt   # Python dependencies
├── package.json       # Node.js dependencies
└── README.md          # Project documentation
\`\`\`

## Next Steps
- Customize the inventory categories
- Add more sophisticated image processing
- Integrate with grocery store APIs
- Add user accounts and history
- Deploy to production

Happy coding! 🚀
