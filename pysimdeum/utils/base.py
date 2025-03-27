import uuid
from dataclasses import dataclass


@dataclass
class Base:
    """Base class of pysimdeum for generating objects. 
    
    The only argument of this parent class is an id which can either be set or will be set to a unique identifier
    """

    id: str = str(uuid.uuid4())
