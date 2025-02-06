# Dining Info API

This API provides a conversational interface to access and query information about dining options from the U of R dining hall

## Setup

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/dining-info-api.git
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

* Create a `.env` file based on `.env.example`.
* Fill in the required values, including API keys and database credentials.

4. **Run the application:**

```bash
uvicorn app.main:app --reload
```

## Usage

Once the application is running, you can interact with the API using any HTTP client.

**Example Request:**

```
POST /api/v1/message

{
  "title": "Lunch Recommendations",
  "message_text": "What should I eat for lunch today?"
}
```

**Example Response:**

```json
{
  "response": "Based on your preferences and today's menu, I recommend the grilled chicken salad with a side of brown rice. It's a good source of protein and complex carbohydrates, perfect for your bodybuilding goals."
}
```

## TODO
* **Scraping**: Move over code for scraping from old project
* **Auth**: Add refresh token functionality instead of just constantly refreshing access token
* **DB**: Implement the rest of the db functions to simplify endpoint code
* **Documentation**: Add API documentation
* **Refactoring**: Make code more organized
* **.env**: Create example .env file
* **Tests**: Improve code quality and maintainability by adding comprehensive unit tests
