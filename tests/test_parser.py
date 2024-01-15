from dict2any.parser import Parser

class MyParser(Parser):

    def parse(self):
        pass

def test_parser():
    parser = MyParser()
    assert parser.parse() is None  
