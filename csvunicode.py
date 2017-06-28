"""
A CSV writer and reader that correctly handled non ASCII inpout/output
This code taken from https://docs.python.org/2/library/csv.html
"""

import csv, codecs, cStringIO


class EncodingRecoder:
    def __init__(self, f, encoding):
        self.encoding = encoding;
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding)


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.encoding = encoding
        f = EncodingRecoder(f, self.encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, self.encoding) for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.encoding = encoding
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(self.encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
