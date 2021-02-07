"""
Test the functionality of predict for valid and invalid inputs
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
    """Return 200 Success when input is valid."""

    response = client.get('/predict/1kKLWkqyZEnrOd5tBYYCUn')

    body = response.json()
    assert response.status_code == 200
    assert len(body['Suggested track IDs']) == 50
    assert "5xNrXJ3xZU7MLQrischxzo" in body['Suggested track IDs']

def test_invalid_input():
    """Return 500  internal server Error input is not in csv file"""
    
    response = client.get('/predict/1kKLWkqyZEnrOd5tBYYCAA')
    assert response.status_code == 500

if __name__ == '__main__':
    test_valid_input()
    test_invalid_input()