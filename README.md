# WIS2
Information system for our faculty.  

Idea is, to have courses to whose students can register, course is then separated into classes whose
needs to be registered by students. Students in classes could be then examined by teachers.
It also implements lots of other features useful in faculty information system.


Screenshot:
![Screenshot](https://i3.ytimg.com/vi/MgoSPsoobMg/maxresdefault.jpg)

## Deployment
### Development
Nothing really special, project requires just:
* `pipenv` - installation steps [here](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
* `Python 3.10` - follow steps [here](https://www.python.org/downloads/release/python-3100/)

Pipenv should install all the dependencies, so run:
```bash
pipenv install
```
It may take a while, just wait.  

Then you should be able to run server:
```bash
pipenv run python3.10 web/manage.py runserver
```
Done, now just visit http://127.0.0.1:8000/
