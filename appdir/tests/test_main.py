"""
testing the root and predict path
"""

print("\n__file__: {}".format(__file__))
if __name__ == '__main__' and  __package__ is None:
    print("is running as a Python Script")
else:
    print("is running as a Python Module")

print("__name__ is: {}".format(__name__))
print("__package__ is: {}".format(__package__))

# None is for script and "" is for python repl import module
if __package__ in [None, ""]:
    # adding project directory to the path 
    import re
    # remove the "/filename.py"
    c_dir = re.sub(r"(^.*)\/.*\.py$", r"\g<1>", __file__)
    
    from sys import path
    from os.path import dirname as dir
    print("existing path:\n", path)

    # adding FastAPI-Spotify to the path
    # everything under FastAPI-Spotify such as "appdir" would be recognized
    path.append(dir(dir(c_dir)))

    print("expanded system path:\n", path)
    __package__ = "appdir.tests"


from fastapi.testclient import TestClient
from appdir.main import app
client = TestClient(app)


def test_docs():
    """Return HTML docs for root route."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/html')


def test_predict():
    """Test the webs server response and the 
    returned data type on predict method"""
    response = client.get('/predict/07j5RLJHwsm4cUb3GGoW3w')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')

if __name__ == '__main__':
    test_docs()
    test_predict()