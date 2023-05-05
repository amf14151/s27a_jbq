class Extension:
    def __init__(self,app):
        self.app = app
        self.extensions = list[str]()

    def add_extension(self,filename:str):
        self.extensions.append(filename)