# 🛡️ Secure Telegram Bot 🕊️

[![UV Package Manager](https://img.shields.io/badge/PackageManager-UV-purple.svg)](https://pypi.org/project/uv/)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-brightgreen.svg?logo=telegram&logoColor=white)](https://aiogram.dev/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.x-blue.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.7-orange.svg)](https://alembic.sqlalchemy.org/en/latest/)
[![asyncio](https://img.shields.io/badge/asyncio-3.11-blue.svg)](https://docs.python.org/3/library/asyncio.html)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-green.svg)](https://www.sqlite.org/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![Telegram API](https://img.shields.io/badge/Telegram%20API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)


## 🤖 Welcome to TgramBuddy — A Secure & Ethical Telegram Bot

Welcome to the repository of my Telegram bot, built with a focus on secure and ethical usage!  
This bot leverages the power of the `aiogram` library within an Object-Oriented Programming (OOP) architecture and is containerized for easy deployment.  
I am passionate about contributing to a safer Telegram environment and promoting positive interactions.

**⚠️ Important Disclaimer:** I strictly **forbid** the use of this project or any part of it for fraudulent schemes, scams, or any activities that could harm or deceive individuals. This project is developed with the intention of promoting peace, friendship, and positive development within the Telegram community. 🚫

## ✨ Key Advantages of This Approach

* **Modular and Maintainable (OOP):** The Object-Oriented Programming architecture promotes code reusability, organization, and easier maintenance. Each part of the bot's functionality is encapsulated within classes, making the codebase cleaner and more scalable.
* **Efficient Dependency Management (UV):** Using `uv` as the package manager ensures faster and more efficient installation of dependencies compared to traditional `pip`. This leads to quicker build times for the Docker image.
* **Simplified Deployment (Containerization):** Docker containerization packages the bot and all its dependencies into a single, portable container. This eliminates environment inconsistencies and makes deployment across different platforms seamless and reliable.
* **Scalability:** Containerization makes it easier to scale the bot horizontally by running multiple instances of the Docker container.
* **Isolation:** Docker provides a level of isolation, ensuring that the bot's dependencies do not interfere with other applications on the same system.

## 🛠️ Getting Started

Follow these steps to get your local environment up and running:

1. **Prerequisites:**
    * 🐍 Python 3.12 or higher installed on your system ([python.org](https://www.python.org/downloads/)).
    * 🐳 Docker installed on your system ([docker.com](https://www.docker.com/get-started)).
    * 📦 `uv` installed (`pip install uv`).

2. **Cloning the Repository:**

3. **Building the Docker Image:**

    ```bash
    docker build -t tgrambuddy-app -f tgrambuddy.dockerfile . 
    ```

4. **Create .env file**
   Create .env file with following format:

   ``` text
   BOT_TOKEN=<your telegram:token>
   ASYNCSQLITE_DB_URL=sqlite+aiosqlite:///data/database/tgrambuddy.db
   ```

* Make sure you do not use any quotes around your token  " or ' or any other.
* Plase .env file in the same folder with dockerfile.

5. **Running the Docker Container**
    You will need to provide your Telegram Bot token as an environment variable.

    ```bash
    # Production mode (Windows environmet)
    docker run --env-file .env -v ${PWD}/data:/app/data -d tgrambuddy-app

    # Debug mode  (Windows environmet)
    docker run --env-file .env -v ${PWD}/data:/app/data --rm -it tgrambuddy-app /bin/bash
    ```

## ⚙️ Usage

comming soon

## 📄 Project Structure  

``` text
TgramBuddy/
├── src/                                                | 📂 Source code directory
│   ├── api/                                            |
|   |
│   ├── bot/                                            |
│   │   ├── core/                                       |
│   │   │   ├── aiobot.py                               |
│   │   │   ├── localization.py                         |
│   │   │   └── t_cc.py                                 | currently excluded
|   |   |
│   │   ├── features/                                   |
│   │   │   ├── onboarding/                             |
│   │   │   │   ├── locales/                            |
│   │   │   │   │   └── en.json                         |
│   │   │   │   │
│   │   │   │   ├── __init__.py                         |
│   │   │   │   └── start_handler.py                    |
│   │   │   │   └── start_router.py                     |
│   │   │   │
│   │   │   ├── imgupload/                             |
│   │   │   │   ├── locales/                            |
│   │   │   │   │   └── en.json                         |
│   │   │   │   │
│   │   │   │   ├── __init__.py                         |
│   │   │   │   └── imgupload_callback.py              |
│   │   │   │   └── imgupload_handler.py               |
│   │   │   │   └── imgupload_router.py                |
│   │   │   │
│   │   │   └── __init-_.py                             |
|   |   |
│   │   ├── middleware/                                 |
│   │   │   ├── cc_middleware.py                        | currently excluded
│   │   │   └── db_middleware.py                        |
|   |   |
│   │   └── services/                                   |
|   |
│   └── database/                                       |
│       ├── __init__.py                                 |
│       ├── db_adapter.py                               |
│       └── models.py                                   |
│           
├── .dockerignore                                       | 🐳 Docker configuration for containerization                
├── alembic.ini                                         |
├── main.py                                             | 🚀 Main entry point of the bot application
├── tgrambuddy.dockerfile
└── .env
```

## ☕ Support My Work

[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-yellow?logo=kofi)](https://buymeacoffee.com/max.v.zaikin)
[![Donate](https://img.shields.io/badge/Donate-orange?logo=paypal)](coming-up)

If you find this project helpful or appreciate my commitment to ethical development, consider buying me a coffee or making a donation!  
Your support helps me continue working on projects like this and contributing to a positive online environment. 🙏

Also, don't forget to:

- ⭐ Star this project on GitHub  
- 👍 Like and share if you find it useful  
- 👔 Connect with me on [LinkedIn](https://www.linkedin.com/in/maxzaikin)  
- 📢 Subscribe to my [Telegram channel](https://t.me/makszaikin) for updates and insights

## 🕊️ My Vision for a Safer Telegram

I believe in the power of Telegram for positive communication and community building. Through this project, I aim to explore ways to contribute to a more secure and trustworthy Telegram ecosystem. I am committed to developing tools and promoting practices that help users stay safe and informed.

## 🤝 Contributing

Any contribution are highly apprciated and welcome 👋

## 📜 License

[MIT.]

## 📧 Contact

[Max.V.Zaikin / #OpenToWork] - [Max.V.Zaikin@gmail.com]

---

✨ Thank you for exploring this project! Let's build a better and safer digital world together! 🌍