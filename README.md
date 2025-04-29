## Installation

1. **Clone the repository**  

   ```
   git clone https://github.com/NagyDezso/VotingSystem.git
   cd VotingSystem
   ```

2. **Install dependencies**  

   ```
   pip install -r requirements.txt
   ```

3. **(Optional) Configure environment variables**  
   Copy `.env-example` to `.env` and adjust as needed:

   ```
   cp web-server/.env-example web-server/.env
   ```

## Running the Server

1. **Navigate to the web-server directory**  

   ```
   cd web-server
   ```

2. **Start the FastAPI server**  

   ```bash
   python server.py
   ```

   The server will start on [http://localhost:8000](http://localhost:8000) by default.
