## Task:
Develop REST API server using django-rest-framework with pagination, sorting and filtering for two models:

    Transaction (id, wallet_id (fk), txid, amount);

    Wallet (id, label, balance);

Where txid is required unique string field, amount is a number with 18-digits precision, label is a string field, 
balance is a summary of all transactions’s amounts.  
Transaction amount may be negative. Wallet balance should NEVER be negative.

## HOWTO:
The simplest way to run a project is to use docker compose to start django-app and PostgreSQL
- Navigate to the project root (same folder where `docker-compose.yml`)
- Create `.env` file in the root folder with minimum required environs:
```
    DB_NAME=<any_name>
    DB_USER=<any_user>
    DB_PASSWORD=<any_password>
    DB_HOST=walletx_db
    DB_PORT=5432
    API_SECRET_KEY=<any secret>
```
- Execute `docker compose up -d --build`
- Execute `docker compose exec app python manage.py migrate`
- Now the API is accessible from the host machine at `http://localhost:8038/api/`
    
    ### Tests
    To run tests execute `docker compose exec app pytest`
    ### Linter
    - To run linter and formatter execute: `docker compose exec app ruff check` and `docker compose exec app ruff format`
    - Additionally linter and formatter might be installed on host machine as pre-commit hook with `pre-commit install`

## Developer's notes:
Since therese is no clear context behind the task, but based on models' names and the company's area of activity,  
I made a decision that Transaction model should not be editable via API, since in financial systems, transactions are usually immutable once created.
