from cfx_utils.post_import_hook import (
    when_imported
)

def test_post_hook_import_if_imported():
    # condition that when_imported is registered after specific module is imported
    from _test_helpers.spam import Spam
    s = Spam("spam")
    
    @when_imported("_test_helpers.spam")
    def substitute_spam_to_egg(module):
        from _test_helpers.spam_with_egg import SpamWithEgg
        module.Spam = SpamWithEgg
    
    assert str(s) == "spam"
    
    # note that Spam bound to this namespace is still the old spam
    # because locals()["Spam"] is not changed 
    s_ = Spam("spam_")
    assert str(s_) == "spam_"
    
    from _test_helpers.spam import Spam as Spam1
    
    s1 = Spam1("spam1")
    assert locals()["Spam"] != locals()["Spam1"]
    assert str(s1) == "spam1_with_eggs"
