import pytest
from cfx_utils.post_import_hook import (
    when_imported
)

def test_post_hook_import():
    @when_imported("_test_helpers.spam")
    def substitute_spam_to_egg(module):
        from _test_helpers.spam_with_egg import SpamWithEgg
        module.Spam = SpamWithEgg
    
    from _test_helpers.spam import Spam
    
    s = Spam("spam")
    assert str(s) == "spam_with_eggs"
    

