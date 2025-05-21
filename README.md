## Installation

1. **Clone the repository**  

   ```cmd
   git clone https://github.com/NagyDezso/VotingSystem.git
   cd VotingSystem
   ```

2. **Install dependencies**  

   ```cmd
   pip install -r requirements.txt
   ```

3. **(Optional) Configure environment variables**  
   Copy `.env-example` to `.env` and adjust as needed:

   ```cmd
   cp web-server/.env-example web-server/.env
   ```

## Running the Server

1. **Start the FastAPI server**  

   ```cmd
   python ./web-server/server.py
   ```

   The server will start on [http://localhost:8000](http://localhost:8000) by default.
