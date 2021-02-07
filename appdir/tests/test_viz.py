"""
Test the functionality of viz for valid and invalid inputs
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

def test_valid_input():
    """Return 200 Success for valid track_id"""
    response = client.get('/viz/07j5RLJHwsm4cUb3GGoW3w')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')


def test_invalid_input():
    """Return 500  internal server Error input is not in csv file"""
    response = client.get('/viz/07j5RLJHwsm4cUb3GGoWZ')
    body = response.json()
    assert response.status_code == 500
    assert body['detail'] == "Input is not in the trained dataset"

if __name__ == '__main__':
    test_valid_input()
    test_invalid_input()