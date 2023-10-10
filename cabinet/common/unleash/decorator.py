def return_on_failure(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                return value
        return applicator
    return decorate
