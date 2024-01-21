                                                 Game Geek

![GameGeek](https://github.com/HanaAlfozan/2023-GP1-5/assets/52613576/ffff66c3-1a0e-4402-a504-30008186ae0a)

   Individuals are exposed to various content on multiple platforms such as social media and
video games. Concentrating on video games, majority of people play games as way of
entertainment, socialize, and a method to unwind. However, many of them have
trouble choosing games that are appropriate for their needs, particularly parents who are worried
about the games their children play. In most cases, the exposure to harmful content may lead
kids to risks such as in-game bullying, identity theft, credit card fraud, sexual exploitation.
Without the right guidance on what games are appropriate for them to play, kids are prone to one
of these risks. Therefore, we thought of building a system that helps find the appropriate games
for each user based on their age group. The following markup and programming languages are required to complete our project: HTML, CSS, JavaScript, Python, and tools: Jira, GitHub, and the Django framework. 

Launching Instructions:

Instructions for Running Game Geek Website in the localhost:

1-Download an Integrated Development Environment (IDE):
Choose and download an IDE such as Visual Studio or PyCharm.


2-Download and Set Up PostgreSQL Database:


3-Download PostgreSQL and pgAdmin.
Create a new PostgreSQL database named "GameGeek."


4-Create and Activate a Virtual Environment:
Create a virtual environment using the command suitable for your operating system.
Activate the virtual environment.


5-Install Django Framework :
Install Django within the virtual environment using the command:
->pip install django


6-Install Required Libraries:
Install the required libraries listed in the requirements.txt file in the Virtual Environment:
->pip install -r requirements.txt


7-Verify Librarie Installations:
Double-check and ensure all the required libraries are successfully installed .


8-Migrate the Database:
Run the following commands to apply migrations and set up the database:
->python manage.py makemigrations
->python manage.py migrate


9-Load Games Dataset , Users Dataset:
Load the games dataset :
->python manage.py import_data
Load Users dataset :
->python manage.py import_users data/Users.csv


10-Run the Development Server:
Start the development server using the command:
->python manage.py runserver


These steps assume you have already cloned the Game Geek repository and have navigated to the project directory. If you encounter any issues during the process, refer to the documentation or seek assistance.
