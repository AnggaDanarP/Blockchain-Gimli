from setuptools import setup, Extension

setup(name = "hash_lib",
        version = "1",
        ext_modules = [Extension("hash", ["Hash/hashing.c"])])
'''
from distutils.core import setup, Extension

def main():
        setup(name="hash_lib",
              version="1.0.0",
              description="Gimli hash",
              ext_modules=[Extension("hash", ["Hash/hashing.c"])])

if __name__ == "__main__":
        main()
'''