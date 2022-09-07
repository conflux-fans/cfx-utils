from _test_helpers.spam import Spam
class SpamWithEgg(Spam):
    def __init__(self, x):
        Spam.__init__(self, x)
    
    def __str__(self):
        return super().__str__() + "_with_eggs"
