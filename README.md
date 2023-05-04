Tecnhologies:

Python 3.7

Django REST framework 3.14

Nginx

Docker

Postgres

http://51.250.82.73/

Here you can share recipes of dishes, add them to favorites and display a shopping list for cooking your favorite dishes. To preserve order - only administrators are allowed to create tags and ingredients.


And the api documentation is here: http://51.250.82.73/api/docs/

To deploy this project need the next actions:


git clone git@github.com:Markporsh/foodgram-project-react.git

Connect to your server:

ssh <server user>@<server IP>
  
Install Docker on your server
  
sudo apt install docker.io
  
Install Docker Compose (for Linux) - 
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  
Get permissions for docker-compose -
sudo chmod +x /usr/local/bin/docker-compose
  
Create project directory (preferably in your home directory) - 
mkdir foodgram && cd foodgram/
  
Create env-file:
touch .env
  
Fill in the env-file like it:
DEBUG=False
SECRET_KEY=<Your_some_long_string>
ALLOWED_HOSTS=<Your_host>
CSRF_TRUSTED_ORIGINS=https://<Your_host>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Your_password>
DB_HOST=foodgram-db
DB_PORT=5432
  
Copy files from 'infra/' (on your local machine) to your server:
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
  
Run docker-compose
sudo docker-compose up -d
  
To create are superuser

sudo docker exec -it backend python manage.py createsuperuser

And if you want, you can use the list of ingredients offered by us to write recipes. Upload it to the database with the following command:

sudo docker exec -it backend python manage.py loaddata data/dump.json
