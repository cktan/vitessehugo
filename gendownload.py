from __future__ import print_function
import os,sys,subprocess
import urllib2
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def rfile(path):
    return open(path).read()

def wfile(path, s):
    with open(path, 'w') as f: f.write(s)

def test_link(ln):
    cmd = "curl --silent --range 0-1 '%s'" % ln
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read()
    print(out)
    eprint('processing', ln, out)
    rc = p.wait()
    if rc != 0:
	eprint('Problem with', ln)
    return rc == 0


class Record:
    def __init__(self, name, version, os, arch, build):
        self.name  = name       # deepgreen
        self.version = version  # 16.28
        self.os      = os       # rh6
        self.arch    = arch     # x86_64
        self.build   = build    # 160129

    def getFname(self):
        return '%s.%s.%s.%s.%s.bin' % (self.name, self.version, self.os, self.arch, self.build)

    def getName(self):  return self.name
    def getVersion(self): return self.version
    def getBuild(self): return self.build
    def getArch(self):  return self.arch

    def isMajor(self, name, ver = 0):
        return self.name == name and (ver <= 0 or self.version.split('.')[0] == str(ver))

    def getURL(self):
	a = 'https://s3.amazonaws.com/vitessedata/download/%s'
        return a % self.getFname()

    def getATag(self):
        return ('<a href="%s">%s</a>' % (self.getURL(), self.getFname()))

    def getOS(self):
        if self.os == 'rh6':
            return 'Redhat 6'
        elif self.os == 'rh7':
            return 'Redhat 7'
        elif self.os == 'ubuntu14':
            return 'Ubuntu 14'
        elif self.os == 'ubuntu16':
            return 'Ubuntu 16'
	elif self.os == 'suse12':
	    return 'Suse 12'
	elif self.os == 'suse11':
	    return 'Suse 11'
        else:
            return self.os

    @staticmethod
    def parse(line):
        # deepgreendb.16.21.rh6.x86_64.171007.bin
        line = line.strip().split('.')
	# get rid of .bin
        if line and line[-1] != 'bin': return None
        line = line[:-1]
        if not line: return None

	# extract build 
        build, line = line[-1], line[:-1]
        if not line: return None

	# extract arch
        arch, line = line[-1], line[:-1]
        if not line: return None

	# extract os
        os, line = line[-1], line[:-1]
        if not line: return None

	# extract name
        name, line = line[0], line[1:]
        if not line: return None

	# whatever is left is VERSION
        version = '.'.join(line)

        if name not in ('deepgreendb', 'gpdb', 'beta-deepgreendb', 'beta-gpdb'):
            return None

        rec = Record(name, version, os, arch, build)
        if not rec.getOS(): return None
	if not test_link(rec.getURL()): return None
        return rec

def getRecords():
    #url = 'http://vitessedata.com/download/list.txt'
    url = 'http://s3.amazonaws.com/vitessedata/download/list.txt'
    rec = []
    f = urllib2.urlopen(url)
    for line in f:
        r = Record.parse(line)
        if r: rec += [r]
    return rec


def makeTable(rec):
    tab = [ (r.getOS(), r.getVersion(), r.getBuild(), r.getATag()) for r in rec ]
    tab.sort(key=lambda x: (999999 - int(x[-2])))
    line = []
    for tup in tab:
        l = '</td><td>'.join(tup)
        line += ['<tr><td>' + l + '</td></tr>\n']

    hdr = ['OS', 'Version', 'Build', 'Link']
    hdr = '</th><th>'.join(hdr)
    hdr = '<tr><th>' + hdr + '</th></tr>\n'
    ret = '''
    <table class="download table">
      <thead>
        %s
      </thead>
      <tbody>
        %s
      </tbody>
    </table>
    '''

    return ret % (hdr, '\n'.join(line))


rec = getRecords()
# v16
tab = [ r for r in rec if r.isMajor('deepgreendb', 16) ]
tab = tab and makeTable(tab) or '<p>Not available</p>'
v16 = tab

# v18
tab = [ r for r in rec if r.isMajor('deepgreendb', 18)]
tab = tab and makeTable(tab) or '<p>Not available</p>'
v18 = tab

# v5
tab = [ r for r in rec if r.isMajor('gpdb', 5)]
tab = tab and makeTable(tab) or '<p>Not available</p>'
v5 = tab

# dgbeta
tab = [ r for r in rec if r.isMajor('beta-deepgreendb') ]
tab = tab and makeTable(tab) or '<p>No beta package is available at this time.</p>'
dgbeta = tab

# gpbeta
tab = [ r for r in rec if r.isMajor('beta-gpdb') ]
tab = tab and makeTable(tab) or '<p>No beta package is available at this time.</p>'
gpbeta = tab


#
#  deepgreen-db/download/packages
# 
dir = 'content/products/deepgreen-db/download/'
content = rfile(dir + 'packages.html.src')
content = content.split('V16V16V16')
content = v16.join(content)
content = content.split('V18V18V18')
content = v18.join(content)
wfile(dir + '_index.html', content)


#
#  open-source-greenplum/download/packages
# 
dir = 'content/products/open-source-greenplum/download/'
content = rfile(dir + 'packages.html.src')
content = content.split('V5V5V5')
content = v5.join(content)
wfile(dir + '_index.html', content)


#
# deepgreen-db/download/beta
#
dir = 'content/products/deepgreen-db/download/'
content = rfile(dir + 'beta.html.src')
content = content.split('BETABETABETA')
content = dgbeta.join(content)
wfile(dir + '/beta.html', content)


#
# open-source-greenplum/download/beta
#
dir = 'content/products/open-source-greenplum/download/'
content = rfile(dir + 'beta.html.src')
content = content.split('BETABETABETA')
content = gpbeta.join(content)
wfile(dir + '/beta.html', content)

