import threading


class ExcThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        # threading.Thread.__init__(self, *args, **kwargs)

        super().__init__(*args, **kwargs)
        self.exc = None

    def exc_run(self):
        raise NotImplementedError

    def run(self):

        try:
            self.exc_run()

        except Exception as e:
            import sys
            self.exc = e
            # Save details of the exception thrown but don't rethrow,
            # just complete the function

    def join(self, reraise=True, *args, **kwargs):
        threading.Thread.join(self, *args, **kwargs)
        if reraise and self.exc:
            # msg = "Thread {} threw an exception: {}".format (self.getName(), self.exc)
            # new_exc = Exception(msg)
            # raise new_exc.with_traceback(self.exc[2])

            raise self.exc
