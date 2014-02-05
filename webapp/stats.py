
try:
    import webapp2
    from google.appengine.ext import db
except:
    webapp2 = None

import json
import numpy as np
import cStringIO

from util import isLocal


try:
    import matplotlib.pyplot as plt
except:
    plt = None

 
# import subprocess, os
# def no_popen(*args, **kwargs): raise OSError("forbjudet")
# subprocess.Popen = no_popen  # not allowed in GAE, missing from module
# subprocess.PIPE = None
# subprocess.STDOUT = None
# os.environ["MATPLOTLIBDATA"] = os.getcwdu()  # own matplotlib data
# os.environ["MPLCONFIGDIR"] = os.getcwdu()    # own matplotlibrc

 
def dynamic_plot(data):
        for l in data: plt.plot(data[l], label=l)
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=len(data), mode="expand", borderaxespad=0.)

def dynamic_png(data, show=False):
    try:
        plt.title("Dynamic PNG")
        dynamic_plot(data)
        if show:
            plt.show()
        else:
            rv = cStringIO.StringIO()
            plt.savefig(rv, format="png")
            plt.clf()
            return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()
    finally:
        plt.clf()

def dynamic_svg(data, show=False):
    try:
        plt.title("Dynamic SVG")
        dynamic_plot(data)
        if show:
            plt.show()
        else:
            rv = cStringIO.StringIO()
            plt.savefig(rv, format="svg")
            return rv.getvalue().partition("-->")[-1]
    finally:
        plt.clf()
# 
# try: dynamic_png()  # crashes first time because it can't cache fonts
# except: logging.exception("don't about it")
        
class Result:
    def __init__(self, _iter, jobs, pop, vals):
        self._iter = _iter
        self.jobs = jobs
        self.pop = pop
        self.vals = vals
        
    @staticmethod
    def serialize(obj):
        return obj.__dict__

if webapp2 is not None:
    class ShowStats(webapp2.RequestHandler):
        def get(self):
            self.response.write("""<html><head/><body>""")
            
            arch = db.GqlQuery("Select * FROM Archive ORDER BY __key__")
            plot, results, last = {}, [], None
            for item in arch:
                r = Result(int(item.key().name()),
                           json.loads(item.jobs),
                           json.loads(item.pop),
                           json.loads(item.vals))
                results.append(r)
            results = sorted(results, key=lambda r: r._iter)
                
            for r in results:
                if last is not None:
                    #count new individuals in the current population
                    r.deltaPop = sum( (np.array(last.pop) != r.pop).any(axis=1).tolist() )
                    
                    #deviation of the changes over all parameters
                    r.deltaPopDev = np.sqrt(np.sum((np.array(last.pop) - r.pop)**2))
                
                last = r
            
            #plot['vals'] = ([r._iter for r in results])
            
            vals = np.array([np.log10(sum(r.vals)+1)-1 for r in results])
            plot['logError'] = ((vals / max(vals)).tolist())
            
            deltaPopDev = np.array([r.deltaPopDev for r in results[1:]])
            plot['deltaPopDev'] = ((deltaPopDev / max(deltaPopDev)).tolist())
            
            deltaPop = np.array([float(r.deltaPop) for r in results[1:]])
            plot['deltaPop'] = ((deltaPop / max(deltaPop)).tolist())
            
            
            if isLocal():
                self.response.write("""Unfortunately, matplotlib doesn't work on the dev server!<br>""")
            else:
                self.response.write(dynamic_png(data=plot))
                self.response.write(dynamic_svg(data=plot))
                
            self.response.write("""<pre>""")
            self.response.write(json.dumps(plot, indent=2))
            self.response.write("""</pre>""")
            self.response.write("""</body></html>""")



if __name__ == "__main__":
    dynamic_png(True)
    dynamic_svg(True)


