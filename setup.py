from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="horecabot",
    version="1.0.0",
    author="HorecaBot Team",
    author_email="info@horecabot.ru",
    description="Специализированная библиотека для создания Telegram ботов для предприятий сферы HoReCa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Slava47/telegram-bot-easy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "flask>=2.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.10.0",
        "redis>=4.5.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "postgresql": ["psycopg2-binary>=2.9.0"],
        "payments": ["yookassa>=2.3.0"],
        "analytics": ["pandas>=2.0.0", "openpyxl>=3.1.0"],
    },
)
