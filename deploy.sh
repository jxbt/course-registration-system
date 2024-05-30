#!/bin/bash


sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx redis-server
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot


python3 -m venv .venv
source .venv/bin/activate


pip3 install -r requirements.txt


export $(cat .env | xargs)


python manage.py makemigrations registration
python manage.py migrate


sudo systemctl start redis-server


nohup celery -A course_registration_system worker --loglevel=info > celery_worker.log 2>&1 &
nohup celery -A course_registration_system beat --loglevel=info > celery_beat.log 2>&1 &

echo -e "\ncreating superuser:\n\n"
python3 manage.py createsuperuser

nohup python3 manage.py runserver > django_server.log 2>&1 &


sudo certbot certonly --nginx -d course-reg.line.pm

sudo cp nginx.conf /etc/nginx/nginx.conf

sudo systemctl restart nginx

echo "Deployment completed successfully!"
