from __future__ import print_function
from functools import wraps


def pipeiflist(func):

    @wraps(func)
    def pipeiflist_inner(self, *args, **kwargs):
        if kwargs.get("conn") is None and isinstance(args[0], list):
            pipelines = self._create_pipelines()
            for i in range(len(args[0])):
                _args = tuple([x[i] for x in args])
                j = self.get_connection_index(_args[0])
                kwargs["conn"] = pipelines[j]
                func(self,  *_args, **kwargs)
            res = [pipe.execute() for pipe in pipelines]
            out = []
            for i in range(len(args[0])):
                _args = tuple([x[i] for x in args])
                j = self.get_connection_index(_args[0])
                out.append(res[j].pop(0))
            return (out)

        elif kwargs.get("conn") is None:
            conn = self.get_connection(args[0])
            kwargs["conn"] = conn

            return func(self,  *args, **kwargs)
    return pipeiflist_inner
