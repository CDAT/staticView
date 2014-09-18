from distutils.core import setup, Extension
import os,sys
import subprocess
import shutil

f=open("git.py","w")
git_branch=subprocess.Popen(["git","rev-parse","--abbrev-ref","HEAD"],stdout=subprocess.PIPE).stdout.read().strip()
print >>f, "branch = '%s'" % git_branch
git_tag = subprocess.Popen(["git","describe","--tags"],stdout=subprocess.PIPE).stdout.read().strip()
sp=git_tag.split("-")
if len(sp)>2:
    commit = sp[-1]
    nm = "-".join(sp[:-2])
    diff=sp[-2]
else:
    commit = git_tag
    nm = git_tag
    diff=0
print >>f, "closest_tag = '%s' " % nm
print >>f, "commit = '%s' " % commit
print >>f, "diff_from_tag = %s " % diff
f.close()

Version="0.1.0"
packages = {'staticView': 'Lib',
            }
for d in packages.itervalues():
    shutil.copy("git.py",os.path.join(d,"git.py"))

setup (name = "staticView",
       version=Version,
       author='PCMDI',
       description = "statiic views tools",
       url = "http://uvcdat.llnl.gov",
       packages = packages.keys(),
       package_dir = packages,
       scripts = ["Scripts/genPNGS.py",],
       #include_dirs = [numpy.lib.utils.get_include()],
       #       ext_modules = [
       #    Extension('metrics.exts',
       #              ['src/C/add.c',],
       #              library_dirs = [],
       #              libraries = [],
       #              define_macros = [],
       #              extra_compile_args = [],
       #              extra_link_args = [],
       #              ),
       #    ]
      )

