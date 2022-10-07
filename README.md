# WIS2


## Deployment
### Production



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
