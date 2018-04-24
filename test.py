import pytest

def test_verbose_raises():
    try:
        raise ValueError('I am a graceful failure')
    except ValueError:
        assert True, 'what a graceful failure!'
    except:
        assert False, 'this is not the graceful failure you were looking for'
    else:
        assert False, 'success is just another form of failure'

def test_succint_raises():
    with pytest.raises(ValueError):
        raise ValueError('I am a graceful failure')

def test_succint_raises_graceful():
    with pytest.raises(ValueError) as exception_info:
        raise ValueError('I am a graceful failure')
    assert 'graceful' in str(exception_info.value), 'the failure was graceful'

#Decorators are used in many places by py.test, to alter the behavior of test functions in several ways, as we will soon see.
################################## Skipping Tests ####################
#pytest.mark.skipif is a function decorator that can be used to mark tests to be skipped:

@pytest.mark.skipif
def test_i_am_unconditionally_skipped_without_reason():
    print('Nothing to see here, we are being skipped')

@pytest.mark.skipif(True, reason='testing skip works')
def test_i_am_being_skipped():
    print('Nothing to see here, I am being skipped')

@pytest.mark.skipif(False, reason='testing not skipping works')
def test_i_am_not_being_skipped():
    print('Look at me, I am not being skipped')

@pytest.mark.skipif(reason='testing skip by default')
def test_yet_another_skipped_test():
    print('Nothing to see here, I am being skipped')

def test_skipping_halfway_through():
    print('This code will be run...')
    pytest.skip('trying imperative skipping out')
    print('...but we will never make it to here.')

########### Marking Tests as Expected Failures ##########################
#Similarly to pytest.mark.skipif there also is pytest.mark.xfail to identify tests known to be failing. This is typically used to keep tests for known bugs around without messing up reporting until you get around to fix them. Since we fix bugs before writing new functionality, this should not be the most used of features. Notice that, by default, xfail marked tests still get run, but the error is not reported as a test failure.

@pytest.mark.xfail
def test_i_will_fail():
    assert False, 'I told you I was going to fail'

@pytest.mark.xfail(run=False)
def test_i_will_break_things_big_time():
    print('Use this to not run e.g. tests that segfault')

@pytest.mark.xfail(raises=IndexError)
def test_moronic_list_access():
    a = []
    assert a[1] == 5

######################## Test Fixtures ##################################################
#Test fixtures create the proper state for tests to run under, e.g. by establishing a connection to a database, or to a hardware device, and performing any necessary setup. Fixtures are implemented as functions decorated with pytest.fixture. The name of the function plays an important role on how this work, so choose a unique, memorable one!

@pytest.fixture
def i_set_things_up():
    projector = {'status': 'doing fine',
                 'flashing': "dicts can't flash!"}
    return projector

# To use this fixture within a test, we have to pass it as a parameter to the test with the exact same name as the fixture function.
def test_fixture_contents(i_set_things_up):
    assert i_set_things_up['status'] == 'doing fine'

#By default, the fixture gets run before every test function, so that each test receives a fresh instance of the fixture, untainted by other tests wrongdoings.
def test_try_to_break_the_fixture_1(i_set_things_up):
    del i_set_things_up['flashing']

def test_try_to_break_the_fixture_2(i_set_things_up):
    assert i_set_things_up['flashing'] == "dicts can't flash!"

#While the default fixture lifetime is a single test function call, they can also be defined to be shared within a module (i.e. a *.py file), a class (a pattern we are not using), or even a session (i.e. over all *.py files discovered by py.test). You can define it by passing a scope keyword argument to the fixture decorator.

@pytest.fixture(scope='module')
def i_also_set_things_up():
    projector = {'status': 'doing fine',
                 'flashing': "dicts can't flash!"}
    return projector
#
#But you now have to be careful that your tests do not affect the state of the shared fixture! The second of this tests will fail as a result of having run the first one:

def test_try_to_break_the_module_fixture_1(i_also_set_things_up):
    del i_also_set_things_up['flashing']

def test_try_to_break_the_module_fixture_2(i_also_set_things_up):
    assert i_also_set_things_up['flashing'] == "dicts can't flash!"

############### Test Fixture Finalizers #######################################
#Often times a test fixture will need some cleaning up after the test (or tests, depending on the scope) completes. You can do this by adding a request parameter to the fixture, and calling the passed in objects addfinalizer method.

@pytest.fixture
def i_set_things_up(request):
    projector = {'status': 'doing fine',
                 'flashing': "dicts can't flash!"}
    def fin():
        projector['status'] = 'torn down by finalizer!'
    request.addfinalizer(fin)
    return projector

def test_nothing(i_set_things_up):
    assert i_set_things_up['status'] == 'doing fine'

