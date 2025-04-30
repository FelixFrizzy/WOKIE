# utils.py
from contextlib import contextmanager

# Function to temporarily change an attribute of a class instance
# e.g. with temporary_setattr(class_instance, "attribute_name", new_value)
@contextmanager
def temporary_setattr(obj, attr, new_value):
    original_value = getattr(obj, attr)
    setattr(obj, attr, new_value)
    try:
        yield
    finally:
        setattr(obj, attr, original_value)
