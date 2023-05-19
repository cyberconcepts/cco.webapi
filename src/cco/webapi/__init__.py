""" package cco.webapi
"""

from cybertools.util.jeep import Jeep

# override in your application package:
config = Jeep(integrator=dict(url='http://localhost:8123/webapi'))

